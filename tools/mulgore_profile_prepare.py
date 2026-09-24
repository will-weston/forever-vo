"""Build Mulgore's native sound-family references and full quest dialogue plan."""
import csv
import itertools
import json
import os
from pathlib import Path
import re
import sys

import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'.local-state/profile-packs/mulgore-20260923'
os.environ['FOREVER_VO_DATA_DIR']=str(ROOT/'.local-state')
sys.path.insert(0,str(ROOT/'tools'))
from generate import load_sources
from textclean import clean,split_gender,has_gender_branch,is_speakable,chunk
from textkey import text_key
from tirisfal_profile_prepare import read_audio,words,sha,save
from wowdata import fetch_file


def main():
    STAGE.mkdir(parents=True,exist_ok=True)
    data=load_sources()
    ids=set(json.loads((ROOT/'.local-state/mulgore-index-selection.json').read_text()))
    extra=ROOT/'.local-state/bulk/mulgore-forever.json'
    if extra.exists():ids.update(r['questID'] for r in json.loads(extra.read_text())['quests'].values())
    selected={k:r for k,r in data['quests'].items() if r['questID'] in ids}
    assert {r['questID'] for r in selected.values()}==ids
    dbdir=ROOT/'.local-state/db2/1.60.1.69913'
    def table(name):return {r['ID']:r for r in csv.DictReader((dbdir/(name+'.csv')).open(encoding='utf-8'))}
    displays,sounds,entries=table('CreatureDisplayInfo'),table('NPCSounds'),table('SoundKitEntry')
    kits={}
    for r in entries.values():kits.setdefault(int(r['SoundKitID']),[]).append(int(r['FileDataID']))
    casting={};definitions={}
    for row in selected.values():
        key=str(row.get('npc'))
        if key in casting:continue
        npc=data['npcs'].get(key,{})
        display_id=npc.get('displayID');display=displays.get(str(display_id),{})
        sound_id=display.get('NPCSoundID');sound=sounds.get(sound_id,{})
        hello=int(sound.get('SoundID_0') or 0);bye=int(sound.get('SoundID_1') or 0)
        fallback=None
        if hello or bye:
            profile='npc-sound-'+sound_id
            definitions[profile]=([hello] if hello else [],[bye] if bye else [])
        elif key=='2994':
            profile='npc-sound-67'
            definitions[profile]=([6014],[6015])
            fallback='Ancestral Spirit has NPCSoundID 0 in the cached display; preserve the prior matching Tauren male stock-family casting.'
        elif key=='5891':
            profile='narrator';fallback='Minor Manifestation of Earth has no native spoken greeting kit; preserve prior narrator casting.'
        elif key=='None' or key.startswith('-') or npc.get('isObject'):
            profile='narrator';fallback='Non-speaking item/object narration.'
        else:raise ValueError(f'No native voice mapping for {key}: {npc}')
        casting[key]={'npc':row.get('npc'),'name':row.get('name') or npc.get('name') or 'Narrator',
            'display_id':display_id,'npc_sound_id':sound_id,'greeting_kit':hello,'farewell_kit':bye,
            'profile':profile,'evidence':(npc.get('display_source') or 'Classic NPC display ID')+' → cached CreatureDisplayInfo.NPCSoundID → NPCSounds sound kits',
            'fallback':fallback}
    save(STAGE/'casting.json',{'npcs':casting,'db2_hashes':{n:sha(dbdir/(n+'.csv')) for n in ['CreatureDisplayInfo','NPCSounds','SoundKitEntry']}})
    transcript_file=STAGE/'reference-transcripts.json'
    transcripts=json.loads(transcript_file.read_text()) if transcript_file.exists() else {}
    asr=None;references={};provenance={}
    for profile,(hello,bye) in sorted(definitions.items()):
        candidates=[];seen=set()
        for activity,kit_ids in [('Greeting',hello),('Farewell',bye)]:
            for kit in kit_ids:
                for fid in kits[kit]:
                    if fid in seen:continue
                    seen.add(fid)
                    cached=list((ROOT/'tools/voices/raw').glob(f'*/{fid}.ogg'))
                    path=cached[0] if cached else fetch_file(fid,STAGE/f'references/raw/{fid}.ogg')
                    if str(fid) not in transcripts:
                        if asr is None:
                            import torch
                            from transformers import pipeline
                            torch.set_num_threads(3)
                            asr=pipeline('automatic-speech-recognition',model='openai/whisper-small.en',device=-1)
                        heard=asr({'raw':read_audio(path,16000).astype(np.float32),'sampling_rate':16000})['text'].strip()
                        transcripts[str(fid)]=heard;save(transcript_file,transcripts)
                        print('REFERENCE',profile,fid,heard,flush=True)
                    text=transcripts[str(fid)];seconds=sf.info(path).duration
                    if re.search(r'(.)\1{8,}',text) or len(words(text))>max(15,seconds*6):continue
                    candidates.append({'file_data_id':fid,'activity':activity,'kit':kit,'path':str(path),
                        'sha256':sha(path),'text':text,'words':len(words(text)),'seconds':seconds})
        usable=[c for c in candidates if c['words']>=3]
        if len(usable)<3 or (bye and not any(c['activity']=='Farewell' for c in usable)):
            usable=[c for c in candidates if c['words']>=2]
        groups=[]
        for count in range(2,min(7,len(usable))+1):
            for group in itertools.combinations(usable,count):
                duration=sum(c['seconds'] for c in group)+.08*(count-1)
                if duration>14.8:continue
                if hello and bye and {c['activity'] for c in group}!={'Greeting','Farewell'}:continue
                tokens=[w for c in group for w in words(c['text'])]
                groups.append((min(len(tokens),30)+.3*len(set(tokens))-.35*count,-count,-duration,group))
        if not groups:raise ValueError(f'Insufficient native speech: {profile}')
        chosen=sorted(max(groups,key=lambda r:r[:3])[-1],key=lambda c:(c['activity']!='Greeting',-c['words'],c['file_data_id']))
        wave=np.concatenate([p for i,c in enumerate(chosen) for p in ((np.zeros(1920),read_audio(c['path'])) if i else (read_audio(c['path']),))])
        gain=min(1.,.95/float(abs(wave).max()))
        out=STAGE/f'references/{profile}.wav';out.parent.mkdir(parents=True,exist_ok=True)
        sf.write(out,wave*gain,24000,subtype='PCM_24')
        references[profile]={'path':str(out),'sha256':sha(out),'word_count':sum(c['words'] for c in chosen),
            'seconds':len(wave)/24000,'approved_pilot':False}
        provenance[profile]={'candidates':candidates,'selected':chosen,'reference':references[profile],
            'exception':'Native sound family exposes no separate farewells; use its complete spoken greetings.' if not bye else None}
        print('ASSEMBLED',profile,references[profile],flush=True)
    if any(c['profile']=='narrator' for c in casting.values()):
        prior=json.loads((ROOT/'.local-state/profile-packs/tirisfal-20260923/plan.json').read_text())
        references['narrator']={**prior['references']['human-male-standard'],'reused_from':'Tirisfal neutral object narration'}
    jobs=[]
    for key,row in sorted(selected.items(),key=lambda pair:(pair[1]['questID'],{'accept':0,'progress':1,'complete':2}[pair[1]['event']])):
        cleaned=clean(row['text'])
        variants=[('m-'+key,split_gender(cleaned)[0]),('f-'+key,split_gender(cleaned)[1])] if has_gender_branch(cleaned) else [(key,cleaned)]
        for base,original in variants:
            assert is_speakable(original),(base,original)
            text=original.replace('--',', ').replace(' - ',', ')
            parts=chunk(text,max_chars=340) if len(words(text))>60 else [text]
            assert ' '.join(text.split())==' '.join(' '.join(parts).split()),base
            assert max(len(words(p)) for p in parts)<=85,(base,'overlong passage')
            cast=casting[str(row.get('npc'))];profile=cast['profile']
            jobs.append({'base':base,'quest':row['questID'],'event':row['event'],'title':row['title'],
                'npc':row.get('npc'),'name':row.get('name') or cast['name'],'profile':profile,
                'source_text':row['text'],'text':text,'text_key':text_key(original),'parts':parts,'reuse':None,
                'source':row.get('source'),'reference_sha256':references[profile]['sha256']})
    plan={'version':1,'zone':'mulgore','model':'IndexTeam/IndexTTS-2.5','formula':'native-profile-word-coverage-v1',
        'seed':43,'temperature':.65,'duration_factor':1.,'tail_seconds':.5,'paragraph_gap_seconds':.12,
        'references':references,'quest_ids':sorted(ids),'files':jobs,
        'policy':'Full dialogue in complete sentence/paragraph groups; float capture, one constant gain, native PCM24. No EQ/reverb/compression/tempo or per-sentence acting edits.'}
    save(STAGE/'plan.json',plan);save(STAGE/'sources.json',{'quests':selected,'npcs':data['npcs'],'gossip':{}})
    save(STAGE/'reference-provenance.json',provenance)
    save(ROOT/'tools/voice_profiles/mulgore-production.json',{'formula':plan['formula'],'references':references,'npcs':casting})
    save(ROOT/'.local-state/latest-mulgore-profile-pack.json',{'stage':str(STAGE),'installed':False})
    print('READY',len(ids),'quests,',len(jobs),'files,',len(references),'profiles,',sum(len(r['parts']) for r in jobs),'passages',flush=True)


if __name__=='__main__':main()
