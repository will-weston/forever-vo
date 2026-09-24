"""Recheck flagged speech using a names-only ASR glossary; record, never auto-approve."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import torch
from transformers import pipeline

import sys

# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.tirisfal_profile_check import assess,save


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--glossary',type=Path,required=True)
    ap.add_argument('--base',action='append')
    ap.add_argument('--all-parts',action='store_true',help='With --base, inspect all passages even when the primary score passed.')
    args=ap.parse_args()
    if args.all_parts and not args.base:
        ap.error('--all-parts requires at least one explicit --base')
    stage=Path(os.environ['FOREVER_VO_PROFILE_STAGE']).resolve()
    manifest=json.loads((stage/'manifest.json').read_text())
    checks=json.loads((stage/'speech-check.json').read_text())['files']
    vocabulary=args.glossary.read_text(encoding='utf-8').strip()
    path=stage/'lexicon-check.json'
    report=json.loads(path.read_text()) if path.exists() else {'method':'Whisper small.en with a names-only glossary. Expected sentences are never supplied.','files':{}}
    report['glossary']=vocabulary
    torch.set_num_threads(3);asr=None
    for base,row in checks.items():
        if (not row['needs_review'] and not args.all_parts) or (args.base and base not in args.base):continue
        render=manifest['files'][base]
        assert row['wav_sha256']==render['wav_sha256'],f'Stale primary check: {base}'
        old=report['files'].get(base)
        if old and old['wav_sha256']==row['wav_sha256'] and old.get('glossary')==vocabulary and old.get('all_parts',False)==args.all_parts:continue
        if asr is None:
            asr=pipeline('automatic-speech-recognition',model='openai/whisper-small.en',device=-1)
            prompt=asr.tokenizer.get_prompt_ids(vocabulary,return_tensors='pt')
        parts=[]
        for i,previous in enumerate(row['parts']):
            if not previous['needs_review'] and not args.all_parts:continue
            part=render['parts'][i];audio=Path(part['path'])
            assert hashlib.sha256(audio.read_bytes()).hexdigest()==part['sha256']
            wave,rate=sf.read(audio);g=math.gcd(rate,16000)
            sample=resample_poly(wave,16000//g,rate//g).astype(np.float32)
            heard=asr({'raw':sample,'sampling_rate':16000},chunk_length_s=30,
                generate_kwargs={'prompt_ids':prompt})['text'].strip()
            parts.append({'part':i,'expected':part['text'],'heard':heard,**assess(part['text'],heard)})
        report['files'][base]={'wav_sha256':row['wav_sha256'],'glossary':vocabulary,'all_parts':args.all_parts,'parts':parts,
            'needs_review':any(p['needs_review'] for p in parts)}
        save(path,report)
        print('LEXICON',base,'REVIEW' if report['files'][base]['needs_review'] else 'OK',flush=True)


if __name__=='__main__':main()
