"""Resumable production rendering of complete Tirisfal quest dialogue.

Run with the IndexTTS environment from its checkout. Never installs by itself.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

import numpy as np
import soundfile as sf
import torch

ROOT=Path(__file__).resolve().parents[1]
STAGE=Path(os.environ.get('FOREVER_VO_PROFILE_STAGE',str(ROOT/'.local-state/profile-packs/tirisfal-20260923'))).resolve()
sys.path.insert(0,str(Path.cwd()))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data,indent=2),encoding='utf-8');tmp.replace(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',action='append')
    parser.add_argument('--seed',type=int)
    parser.add_argument('--rerender',action='store_true')
    parser.add_argument('--capture-before-clamp',action='store_true',
        help='Audition mode: capture the final vocoder convolution before its hard clamp; requires a non-tanh vocoder.')
    args=parser.parse_args()
    plan=json.loads((STAGE/'plan.json').read_text())
    manifest_path=STAGE/'manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'model':plan['model'],'formula':plan['formula'],'references':plan['references'],
        'post':'Float waveform, one constant headroom gain across a whole event, native PCM24, 0.12s between complete passages, 0.5s final tail. No effects.',
        'files':{},'installed':False}
    manifest['render_complete']=False
    capture_mode='pre-clamp' if args.capture_before_clamp else 'vocoder-output'
    manifest['capture_mode']=capture_mode
    if args.capture_before_clamp:
        manifest['post']='Final vocoder convolution captured before its hard clamp; one constant event gain, PCM24, original passage gaps and tail. No effects.'
    save(manifest_path,manifest)
    rows=[r for r in plan['files'] if not args.base or r['base'] in args.base]
    if args.base and set(args.base)!={r['base'] for r in rows}:raise ValueError('Unknown requested file')
    for ref in plan['references'].values():assert sha(Path(ref['path']))==ref['sha256']
    ffmpeg=next((ROOT/'.local-tools/ffmpeg').rglob('ffmpeg.exe'))
    model=None; captured=[]
    def retain_float(module,inputs,output):
        captured.append(output.detach().float().cpu().numpy().reshape(-1).copy())
        peak=output.detach().abs().max()
        return output*(.8/peak.clamp(min=.8))
    started=time.time()
    for row in rows:
        base=row['base'];wav=STAGE/(base+'.wav');mp3=STAGE/(base+'.mp3')
        fingerprint=hashlib.sha256(json.dumps({'row':row,'formula':plan['formula'],'temperature':plan['temperature'],
            'duration':plan['duration_factor'],'renderer':'float-preclamp-v1' if args.capture_before_clamp else 'float-paragraph-v1'},sort_keys=True).encode()).hexdigest()
        old=manifest['files'].get(base)
        if old and not args.rerender and old['fingerprint']==fingerprint and mp3.exists() and sha(mp3)==old['mp3_sha256']:
            continue
        if old:
            archive=STAGE/'previous-takes';archive.mkdir(exist_ok=True)
            if wav.exists():shutil.copy2(wav,archive/(base+'-'+old['wav_sha256'][:12]+'.wav'))
            save(archive/(base+'-'+old['wav_sha256'][:12]+'.json'),old)
        seed=args.seed if args.seed is not None else plan['seed']
        reused=bool(row.get('reuse') and not args.rerender)
        parts=[]
        if reused:
            source=Path(row['reuse']['path']);assert sha(source)==row['reuse']['sha256']
            shutil.copy2(source,wav)
            final,rate=sf.read(wav)
            gain=None;raw_peak=None
            parts=[{'text':row['text'],'path':str(wav),'sha256':sha(wav),'seconds':len(final)/rate}]
        else:
            if model is None:
                from indextts.infer_v2_5 import IndexTTS2
                model=IndexTTS2(cfg_path='checkpoints/config.yaml',model_dir='checkpoints',use_bf16=True,
                    use_cuda_kernel=False,use_deepspeed=False,use_accel=False,use_torch_compile=False,use_qwen_emo=False)
                if args.capture_before_clamp:
                    assert model.bigvgan.use_tanh_at_final is False,'Pre-clamp capture requires a hard-clamp vocoder'
                    model.bigvgan.conv_post.register_forward_hook(retain_float)
                else:
                    model.bigvgan.register_forward_hook(retain_float)
            pieces=[]
            part_dir=STAGE/'parts'/base;part_dir.mkdir(parents=True,exist_ok=True)
            for i,text in enumerate(row['parts']):
                random.seed(seed+i);np.random.seed(seed+i);torch.manual_seed(seed+i)
                captured.clear()
                intermediate=part_dir/f'{i}-intermediate.wav'
                model.infer(spk_audio_prompt=plan['references'][row['profile']]['path'],text=text,lang='EN',
                    output_path=str(intermediate),duration_factor=1.,temperature=plan['temperature'],
                    max_text_tokens_per_segment=256,use_random=False,verbose=False)
                if len(captured)!=1:raise ValueError(f'Unexpected segmentation: {base}, part {i}')
                wave=captured[0];assert np.isfinite(wave).all() and abs(wave).max()>0
                rate=sf.info(intermediate).samplerate
                pieces.append(wave)
            raw_peak=max(float(abs(w).max()) for w in pieces)
            gain=min(1.,.75/raw_peak)
            joined=[]
            for i,(wave,text) in enumerate(zip(pieces,row['parts'])):
                part_path=part_dir/f'{i}.wav'
                sf.write(part_path,np.concatenate([wave*gain,np.zeros(int(rate*.5))]),rate,subtype='PCM_24')
                parts.append({'text':text,'path':str(part_path),'sha256':sha(part_path),'seconds':len(wave)/rate})
                if i:joined.append(np.zeros(int(rate*plan['paragraph_gap_seconds'])))
                joined.append(wave*gain)
            joined.append(np.zeros(int(rate*plan['tail_seconds'])))
            final=np.concatenate(joined)
            sf.write(wav,final,rate,subtype='PCM_24')
        assert np.isfinite(final).all() and abs(final).max()<=.750001
        assert not np.any(final[-int(.49*rate):])
        subprocess.run([str(ffmpeg),'-y','-v','error','-i',str(wav),'-ac','1','-ar','44100',
                        '-codec:a','libmp3lame','-b:a','128k',str(mp3)],check=True)
        seconds=sf.info(mp3).duration
        assert abs(seconds-len(final)/rate)<.15
        manifest['files'][base]={**row,'fingerprint':fingerprint,'parts':parts,'seed':seed,'capture_mode':capture_mode,
            'temperature':plan['temperature'],'approved_pilot_reuse':reused,'source_float_peak':raw_peak,'gain':gain,
            'seconds':seconds,'sample_rate':rate,'wav_sha256':sha(wav),'mp3_sha256':sha(mp3)}
        save(manifest_path,manifest)
        print(f"READY {len(manifest['files'])}/{len(plan['files'])} {base}: {seconds:.1f}s, {len(parts)} passages, {row['name']} [{row['profile']}]",flush=True)
    manifest['render_complete']=len(manifest['files'])==len(plan['files'])
    save(manifest_path,manifest)
    print('DONE',len(manifest['files']),'files;',round(time.time()-started),'seconds',flush=True)


if __name__=='__main__':main()
