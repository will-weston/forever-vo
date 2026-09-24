"""Stage, validate and install the fully checked native-profile Tirisfal pack."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
STAGE=Path(os.environ.get('FOREVER_VO_PROFILE_STAGE',str(ROOT/'.local-state/profile-packs/tirisfal-20260923'))).resolve()
os.environ['FOREVER_VO_DATA_DIR']=str(ROOT/'.local-state')
sys.path.insert(0,str(ROOT/'tools'))
from config import SOUNDS_DIR,SOUND_INDEX,PACK_DATA_DIR
from generate import load_sources,load_items,rebuild_tables


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2),encoding='utf-8');tmp.replace(path)


def replace_file(source,target):
    temp=target.with_name(target.name+'.profile-update.tmp')
    shutil.copy2(source,temp);os.replace(temp,target)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--install',action='store_true');args=ap.parse_args()
    plan=json.loads((STAGE/'plan.json').read_text());manifest=json.loads((STAGE/'manifest.json').read_text())
    zone=plan.get('zone','tirisfal')
    assert zone and all(c in 'abcdefghijklmnopqrstuvwxyz-' for c in zone),'Invalid zone identifier'
    checks=json.loads((STAGE/'speech-check.json').read_text())['files']
    override_path=STAGE/'qa-overrides.json';overrides=json.loads(override_path.read_text()) if override_path.exists() else {}
    expected={r['base'] for r in plan['files']}
    assert set(manifest['files'])==expected,'Rendering is incomplete'
    assert expected<=set(checks),'Speech verification is incomplete'
    for row in plan['files']:
        base=row['base'];render=manifest['files'][base]
        assert render['text']==row['text'] and render['text_key']==row['text_key'],f'Stale dialogue: {base}'
        assert ' '.join(' '.join(p['text'] for p in render['parts']).split())==' '.join(row['text'].split()),f'Incomplete dialogue: {base}'
        assert [p['expected'] for p in checks[base]['parts']]==[p['text'] for p in render['parts']],f'Stale transcript check: {base}'
        assert render['reference_sha256']==plan['references'][row['profile']]['sha256']
        assert sha(STAGE/(base+'.wav'))==render['wav_sha256']==checks[base]['wav_sha256']
        assert sha(STAGE/(base+'.mp3'))==render['mp3_sha256']
        assert abs(sf.info(STAGE/(base+'.mp3')).duration-render['seconds'])<.001
        if checks[base]['needs_review']:
            assert overrides.get(base,{}).get('wav_sha256')==render['wav_sha256'],f'Unresolved speech check: {base}'
            assert overrides[base].get('reason'),f'Missing review reason: {base}'
    assembled=STAGE/'assembled'
    (assembled/'Data').mkdir(parents=True,exist_ok=True)
    shutil.copytree(SOUNDS_DIR,assembled/'Sounds',dirs_exist_ok=True)
    index=json.loads(SOUND_INDEX.read_text())
    for base,row in manifest['files'].items():
        shutil.copy2(STAGE/(base+'.mp3'),assembled/'Sounds/Quests'/(base+'.mp3'))
        index[base]={'d':row['seconds'],'v':row['profile'],'t':row['text_key'],
            'engine':'indextts-2.5','reference_sha256':row['reference_sha256'],
            'formula':plan['formula'],'fingerprint':row['fingerprint'],'mp3_sha256':row['mp3_sha256']}
    items=load_items(load_sources(),include_progress=True)
    rebuilt=rebuild_tables(items,index,data_dir=assembled/'Data',sounds_dir=assembled/'Sounds',write_index=False)
    assert expected<=rebuilt['files'],'Some generated recordings would not be indexed'
    save(assembled/'sound_index.json',index)
    subprocess.run([str(ROOT/'.bootstrap/Scripts/python.exe'),str(ROOT/'tools/tirisfal_profile_validate_lua.py'),
                    '--pack',str(assembled)],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/apicheck.py')],check=True)
    installed=SOUNDS_DIR/'Quests'
    untouched={p.name:sha(p) for p in installed.glob('*.mp3') if p.stem not in expected}
    if not args.install:
        print('STAGED AND VERIFIED',assembled);return
    game=Path('C:/Program Files (x86)/World of Warcraft/_classic_beta_/Interface/AddOns/ForeverVO_Data')
    assert game.exists() and os.path.samefile(game,ROOT/'ForeverVO_Data'),'Installed addon does not point to this pack'
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=ROOT/'.local-state/backups'/('before-'+zone+'-profiles-'+stamp)
    backup.mkdir(parents=True)
    shutil.copy2(SOUND_INDEX,backup/'sound_index.json')
    shutil.copytree(PACK_DATA_DIR,backup/'Data')
    (backup/'Quests').mkdir()
    old_hashes={}
    for base in expected:
        target=installed/(base+'.mp3')
        if target.exists():
            old_hashes[base]=sha(target);shutil.copy2(target,backup/'Quests'/target.name)
    save(backup/'rollback.json',{'updated':sorted(expected),'previous':old_hashes,
        'new_files':sorted(expected-set(old_hashes)),'untouched':untouched})
    for base in expected:replace_file(STAGE/(base+'.mp3'),installed/(base+'.mp3'))
    replace_file(assembled/'sound_index.json',SOUND_INDEX)
    for p in (assembled/'Data').glob('*.lua'):replace_file(p,PACK_DATA_DIR/p.name)
    for name,expected_hash in untouched.items():assert sha(installed/name)==expected_hash,name
    for base,row in manifest['files'].items():assert sha(installed/(base+'.mp3'))==row['mp3_sha256'],base
    subprocess.run([str(ROOT/'.bootstrap/Scripts/python.exe'),str(ROOT/'tools/tirisfal_profile_validate_lua.py'),
                    '--pack',str(ROOT/'ForeverVO_Data')],check=True)
    manifest.update(installed=True,backup=str(backup),installed_at=datetime.datetime.now().isoformat())
    save(STAGE/'manifest.json',manifest)
    summary={'stage':str(STAGE),'installed':True,'backup':str(backup),'quest_count':len(plan['quest_ids']),
        'recordings':len(expected),'replaced':len(old_hashes),'new':len(expected-set(old_hashes)),
        'unrelated_audio_preserved':len(untouched),'game_addon':str(game)}
    save(ROOT/('.local-state/latest-'+zone+'-profile-pack.json'),summary)
    save(STAGE/'installation.json',summary)
    print('INSTALLED',json.dumps(summary),flush=True)


if __name__=='__main__':main()
