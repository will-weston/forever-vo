"""Check the staged full dialogue as it is rendered; CPU ASR keeps GPU free."""
import argparse
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import torch
from transformers import pipeline

ROOT=Path(__file__).resolve().parents[1]
STAGE=Path(os.environ.get('FOREVER_VO_PROFILE_STAGE',str(ROOT/'.local-state/profile-packs/tirisfal-20260923'))).resolve()


def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2),encoding='utf-8');tmp.replace(path)


def normalize(text):
    text=text.lower().replace('\u2019',"'")
    text=re.sub(r'\b(north|south)[ -](east|west)\b',r'\1\2',text)
    ones=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
    tens=['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    def number(match):
        n=int(match.group())
        return ones[n] if n<20 else tens[n//10]+(' '+ones[n%10] if n%10 else '')
    text=re.sub(r'\b\d{1,2}\b',number,text)
    replacements={"i'm":"i am","i've":"i have","i'll":"i will","we're":"we are","we've":"we have",
        "you're":"you are","you've":"you have","you'll":"you will","it's":"it is","that's":"that is",
        "they're":"they are","they'll":"they will","don't":"do not","doesn't":"does not","isn't":"is not",
        "can't":"cannot","won't":"will not","wouldn't":"would not","shouldn't":"should not",
        'death knell':'deathknell','death guards':'deathguards','rattle cage':'rattlecage','rattletage':'rattlecage',
        'leech king':'lich king','maximilian':'maximillion','under city':'undercity',
        'plague lands':'plaguelands','thunderbluff':'thunder bluff',
        'great mother':'greatmother','earth mother':'earthmother','blood hoof':'bloodhoof',
        'rune totem':'runetotem','winter hoof':'winterhoof','thunder horn':'thunderhorn',
        'eagle talon':'eagletalon','wind fury':'windfury',"what's":"what is",
        'silver pine':'silverpine','shadow fang':'shadowfang','pyre wood':'pyrewood',
        'spell-casting':'spellcasting','spell casting':'spellcasting'}
    for a,b in replacements.items():text=text.replace(a,b)
    text=re.sub(r'\b(\w+)[’\']s\b',r'\1s',text)
    return re.findall('[a-z0-9]+',text)


def assess(expected,heard):
    a,b=normalize(expected),normalize(heard)
    matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
    differences=[{'op':tag,'expected':' '.join(a[i:j]),'heard':' '.join(b[k:l]),'expected_count':j-i}
        for tag,i,j,k,l in matcher.get_opcodes() if tag!='equal']
    ratio=matcher.ratio()
    end_n=min(6,len(a),len(b))
    end_ratio=difflib.SequenceMatcher(None,a[-end_n:],b[-end_n:],autojunk=False).ratio() if end_n else 0
    missing=max([d['expected_count'] for d in differences if d['op']=='delete'] or [0])
    flag=ratio<(.78 if len(a)<10 else .87) or missing>=4 or (end_n>=4 and end_ratio<.6)
    return {'ratio':ratio,'ending_ratio':end_ratio,'differences':differences,'needs_review':flag}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');args=ap.parse_args()
    torch.set_num_threads(3)
    output=STAGE/'speech-check.json'
    report=json.loads(output.read_text()) if output.exists() else {'files':{},'method':'Whisper small.en, CPU; transcription is a diagnostic, not a timbre or acting-quality score.'}
    for row in report['files'].values():
        for part in row['parts']:part.update(assess(part['expected'],part['heard']))
        row['needs_review']=any(p['needs_review'] for p in row['parts'])
    report['comparison_rules_version']=6
    save(output,report)
    asr=None;idle_since=time.time()
    while True:
        try:manifest=json.loads((STAGE/'manifest.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):
            if not args.watch:raise
            time.sleep(2);continue
        for base,row in manifest['files'].items():
            if report['files'].get(base,{}).get('wav_sha256')==row['wav_sha256']:continue
            if asr is None:asr=pipeline('automatic-speech-recognition',model='openai/whisper-small.en',device=-1)
            results=[]
            for part in row['parts']:
                path=Path(part['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==part['sha256']
                wave,rate=sf.read(path);assert np.isfinite(wave).all() and abs(wave).max()<=.750001
                g=math.gcd(rate,16000);sample=resample_poly(wave,16000//g,rate//g).astype(np.float32)
                text=asr({'raw':sample,'sampling_rate':16000},chunk_length_s=30)['text'].strip()
                results.append({'expected':part['text'],'heard':text,**assess(part['text'],text)})
            report['files'][base]={'wav_sha256':row['wav_sha256'],'parts':results,
                'needs_review':any(r['needs_review'] for r in results)}
            save(output,report);idle_since=time.time()
            print('CHECK',len(report['files']),base,'REVIEW' if report['files'][base]['needs_review'] else 'OK',
                'min',round(min(r['ratio'] for r in results),3),flush=True)
        complete=manifest.get('render_complete') and len(report['files'])==len(manifest['files'])
        if not args.watch or complete:break
        if time.time()-idle_since>3600:raise TimeoutError('No new renders for one hour')
        time.sleep(2)
    print('DONE; needs review:',[b for b,r in report['files'].items() if r['needs_review']],flush=True)


if __name__=='__main__':main()
