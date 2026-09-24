"""Prepare the approved native-profile formula for a full local Tirisfal pack."""
import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parents[1]
os.environ['FOREVER_VO_DATA_DIR'] = str(ROOT/'.local-state')
STAGE = ROOT/'.local-state/profile-packs/tirisfal-20260923'
PILOT = ROOT/'tools/samples/tirisfal-stock-profiles'
sys.path.insert(0, str(ROOT/'tools'))

# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.generate import load_sources
from tools.textclean import clean, split_gender, has_gender_branch, is_speakable, chunk
from tools.textkey import text_key
from tools.wowdata import fetch_file


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    temp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())


def read_audio(path, target=24000):
    wave, rate = sf.read(path)
    if wave.ndim > 1:
        wave = wave.mean(axis=1)
    g = math.gcd(rate, target)
    return resample_poly(wave, target//g, rate//g)


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    data = load_sources()
    ids = set(json.loads((ROOT/'.local-state/tirisfal-index-selection.json').read_text()))
    with sqlite3.connect(ROOT/'.local-state/classicdb/sqlite-dump/mangos.sqlite') as db:
        ids.update(r[0] for r in db.execute('SELECT entry FROM quest_template WHERE ZoneOrSort IN (85,154)'))
    imports = json.loads((ROOT/'.local-state/capture.json').read_text())
    ids.update(r['questID'] for r in imports['quests'].values())
    # This offer is narration, with no speaking NPC identified by its page.
    # Keep npc null instead of manufacturing a creature or object ID.
    raw = json.loads((ROOT/'.local-state/wowhead-tirisfal-additions-2026-09-23.json').read_text())
    narration = raw['quests']['95328-accept']
    narration.update(narration=True, name='Whispering Horror Residue')
    data['quests']['95328-accept'] = narration
    ids.add(95328)
    extra = {'version':2,'quests':{'95328-accept':narration},'npcs':{},'gossip':{}}
    save(ROOT/'.local-state/bulk/tirisfal-narration.json',extra)
    selected = {k:r for k,r in data['quests'].items() if r['questID'] in ids}
    # Wowhead display IDs read from embedded public NPC metadata on 2026-09-23.
    observed = {244808:129405,246378:129985,246389:129986,248840:129405,
                251001:1590,259190:129990,267008:10474,267009:146496,275954:148433,
                10665:9999,10666:10006,2132:1601,3549:1607,1495:2858,1738:2862,
                1931:11428,2211:11424}
    dbdir = ROOT/'.local-state/db2/1.60.1.69913'
    def table(name):
        return {r['ID']:r for r in csv.DictReader((dbdir/(name+'.csv')).open(encoding='utf-8'))}
    displays, sounds, entries = table('CreatureDisplayInfo'),table('NPCSounds'),table('SoundKitEntry')
    kit_files = {}
    for r in entries.values():
        kit_files.setdefault(int(r['SoundKitID']),[]).append(int(r['FileDataID']))
    by_kit = {6036:'undead-male-standard',6039:'undead-male-warrior',6042:'undead-male-dark',
              6046:'undead-female-standard',6049:'undead-female-warrior',6052:'undead-female-magic',
              6663:'undead-female-magic',6484:'necromancer',6486:'abomination'}
    registry = json.loads((ROOT/'tools/voice_profiles/tirisfal.json').read_text())
    casting = {}
    for row in selected.values():
        key = str(row.get('npc'))
        if key in casting:
            continue
        npc = data['npcs'].get(key,{})
        display_id = observed.get(int(key)) if key not in ('None','') else None
        display_id = display_id or npc.get('displayID')
        display = displays.get(str(display_id),{})
        sound_id = display.get('NPCSoundID')
        kit = int(sounds.get(sound_id,{}).get('SoundID_0') or 0)
        profile = by_kit.get(kit)
        evidence = 'Wowhead display ID → cached CreatureDisplayInfo.NPCSoundID → NPCSounds sound kits' if key not in ('None','') and int(key) in observed else 'Classic NPC display ID → cached CreatureDisplayInfo.NPCSoundID → NPCSounds sound kits'
        if key in registry['npcs'] and registry['npcs'][key].get('profile'):
            profile = registry['npcs'][key]['profile']
            evidence = registry['npcs'][key]['source']
        fallback = None
        if not profile:
            if key=='1931':
                profile='human-male-standard'; fallback='No native NPCSoundID or Wowhead voice list; coherent stock human male set for the human prisoner.'
            elif key=='2211':
                profile='dwarf-male-standard'; fallback='No native NPCSoundID or Wowhead voice list; coherent stock dwarf male set for the dwarf prisoner.'
            elif key=='None' or npc.get('isObject') or key.startswith('-'):
                profile='human-male-standard'; fallback='Non-speaking item/object narration, read with the neutral human reference.'
            else:
                raise ValueError(f'Unmapped speaker {key}: {npc}, kit {kit}')
        casting[key]={'npc':row.get('npc'),'name':row.get('name') or npc.get('name') or 'Narrator',
                      'display_id':display_id,'npc_sound_id':sound_id,'greeting_kit':kit,
                      'profile':profile,'evidence':evidence,'fallback':fallback}
    save(STAGE/'casting.json',{'npcs':casting,'db2_hashes':{n:sha(dbdir/(n+'.csv')) for n in ['CreatureDisplayInfo','NPCSounds','SoundKitEntry']},'wowhead_display_ids':observed})
    prior = json.loads((PILOT/'reference-manifest.json').read_text())['profiles']
    references = {k:{**v['reference'],'word_count':v['word_count'],'seconds':v['seconds'],'approved_pilot':True} for k,v in prior.items()}
    definitions = {
        'undead-female-warrior':([6049],[6050],[]),
        'undead-female-magic':([6663],[6053],[563097,563104]),
        'necromancer':([6484],[],[556296]),
        'abomination':([6486],[],[543355,543364]),
        'human-male-standard':([5974],[5975],[]),
        'dwarf-male-standard':([5904],[5905],[]),
    }
    transcript_file = STAGE/'reference-transcripts.json'
    transcripts = json.loads(transcript_file.read_text()) if transcript_file.exists() else {}
    ref_manifest = {}
    asr = None
    for profile in sorted(set(c['profile'] for c in casting.values())-set(references)):
        hello,bye,excluded = definitions[profile]
        candidates=[]
        for kind,kits in [('Greeting',hello),('Farewell',bye)]:
            for kit in kits:
                for fid in kit_files[kit]:
                    if fid in excluded: continue
                    files=list((ROOT/'tools/voices/raw').glob(f'*/{fid}.ogg'))
                    path=files[0] if files else fetch_file(fid,STAGE/f'references/raw/{fid}.ogg')
                    if str(fid) not in transcripts:
                        if asr is None:
                            import torch
                            from transformers import pipeline
                            torch.set_num_threads(3)
                            asr=pipeline('automatic-speech-recognition',model='openai/whisper-small.en',device=-1)
                        text=asr({'raw':read_audio(path,16000).astype(np.float32),'sampling_rate':16000})['text'].strip()
                        transcripts[str(fid)]=text
                        save(transcript_file,transcripts)
                        print('REFERENCE ASR',fid,text,flush=True)
                    text=transcripts[str(fid)]
                    if re.search(r'(.)\1{8,}',text) or len(words(text))>max(15,sf.info(path).duration*6):
                        print('EXCLUDE nonverbal/unreliable ASR',fid,flush=True)
                        continue
                    candidates.append({'file_data_id':fid,'activity':kind,'kit':kit,'path':str(path),
                        'sha256':sha(path),'text':text,'words':len(words(text)),'seconds':sf.info(path).duration})
        usable=[c for c in candidates if c['words']>=3]
        if len(usable)<3 or (bye and not any(c['activity']=='Farewell' for c in usable)):
            usable=[c for c in candidates if c['words']>=2]
        groups=[]
        for count in range(2,min(7,len(usable))+1):
            for group in itertools.combinations(usable,count):
                duration=sum(c['seconds'] for c in group)+.08*(count-1)
                if duration>14.8: continue
                if bye and {c['activity'] for c in group}!={'Greeting','Farewell'}: continue
                tokens=[w for c in group for w in words(c['text'])]
                score=min(len(tokens),30)+.3*len(set(tokens))-.35*count
                groups.append((score,-count,-duration,group))
        if not groups:raise ValueError(f'Insufficient coherent stock speech: {profile}')
        chosen=sorted(max(groups,key=lambda r:r[:3])[-1],key=lambda c:(c['activity']!='Greeting',-c['words'],c['file_data_id']))
        wave=np.concatenate([p for i,c in enumerate(chosen) for p in ((np.zeros(1920),read_audio(c['path'])) if i else (read_audio(c['path']),))])
        gain=min(1.,.95/float(abs(wave).max()))
        output=STAGE/f'references/{profile}.wav';output.parent.mkdir(parents=True,exist_ok=True)
        sf.write(output,wave*gain,24000,subtype='PCM_24')
        references[profile]={'path':str(output),'sha256':sha(output),'word_count':sum(c['words'] for c in chosen),'seconds':len(wave)/24000,'approved_pilot':False}
        ref_manifest[profile]={'candidates':candidates,'selected':chosen,'reference':references[profile],
            'exception':'Native kit has no farewells; use complete non-combat lines from that same actor.' if not bye else None}
        print('REFERENCE',profile,references[profile],flush=True)
    save(STAGE/'new-reference-provenance.json',ref_manifest)
    # Retain the reviewed editorial wording for the original opening quests, but
    # never use the audition excerpt in place of a complete quest event.
    editorial={r['base']:r for r in json.loads((ROOT/'tools/samples/deathknell-clean-nine/performance-plan.json').read_text())['files']}
    pilot_rows={r['base']:r for r in json.loads((PILOT/'performance-plan.json').read_text())['files']}
    pilot_render={r['base']:r for r in json.loads((PILOT/'manifest.json').read_text())['files']}
    jobs=[]
    for key,row in sorted(selected.items(),key=lambda pair:(pair[1]['questID'],{'accept':0,'progress':1,'complete':2}[pair[1]['event']])):
        raw_text=row['text']; cleaned=clean(raw_text)
        variants=[('m-'+key,split_gender(cleaned)[0]),('f-'+key,split_gender(cleaned)[1])] if has_gender_branch(cleaned) else [(key,cleaned)]
        for base,text in variants:
            if not is_speakable(text):raise ValueError(f'Unresolved text in {base}: {text}')
            original=text
            if base in editorial:text=editorial[base]['text']
            text=text.replace('--',', ').replace(' - ',', ')
            # Full utterances of the same length as the accepted casting samples.
            # Preserve sentences/clauses, never cut words or drop any quest text.
            parts=chunk(text,max_chars=340) if len(words(text))>60 else [text]
            assert re.sub(r'\s+',' ',text).strip()==re.sub(r'\s+',' ',' '.join(parts)).strip(),base
            if max(map(lambda t:len(words(t)),parts))>85:raise ValueError(f'Overlong unsplittable passage: {base}')
            profile=casting[str(row.get('npc'))]['profile']
            reuse=None
            if base in pilot_rows and base in pilot_render and 'synthesis_text' not in pilot_rows[base]:
                p=pilot_rows[base]
                if p['voice']==profile and p['text'].replace('--',', ').replace(' - ',', ')==text:
                    reuse={'path':str(PILOT/(base+'.wav')),'sha256':pilot_render[base]['sha256']}
            jobs.append({'base':base,'quest':row['questID'],'event':row['event'],'title':row['title'],
                'npc':row.get('npc'),'name':casting[str(row.get('npc'))]['name'],'profile':profile,
                'source_text':raw_text,'text':text,'text_key':text_key(original),'parts':parts,'reuse':reuse,
                'source':row.get('source'),'reference_sha256':references[profile]['sha256']})
    plan={'version':1,'model':'IndexTeam/IndexTTS-2.5','formula':'native-profile-word-coverage-v1',
          'seed':43,'temperature':.65,'duration_factor':1.,'tail_seconds':.5,'paragraph_gap_seconds':.12,
          'references':references,'quest_ids':sorted(ids),'files':jobs,
          'policy':'Full dialogue in complete sentence/paragraph groups; float capture, one constant gain, native PCM24. No EQ/reverb/compression/tempo or per-sentence acting edits.'}
    save(STAGE/'plan.json',plan)
    save(STAGE/'sources.json',{'quests':selected,'npcs':data['npcs'],'gossip':{}})
    save(ROOT/'.local-state/latest-tirisfal-profile-pack.json',{'stage':str(STAGE),'installed':False})
    print('READY',len(ids),'quests,',len(jobs),'files,',sum(len(r['parts']) for r in jobs),'continuous passages,',sum(len(words(r['text'])) for r in jobs),'spoken words',flush=True)


if __name__=='__main__':main()
