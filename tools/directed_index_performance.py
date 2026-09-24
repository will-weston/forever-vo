"""Render the reviewed Deathknell performance score; never modifies the game pack.

Run with the IndexTTS environment and checkout as working directory.
"""
import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/samples/directed-tirisfal'
sys.path.insert(0, str(Path.cwd()))

# Light interpolation with the original reference emotion, not categorical acting.
# Order: happy, angry, sad, afraid, disgusted, melancholic, surprised, calm.
TONES = {
    'dry': [.02, .03, 0, 0, .05, 0, 0, .09],
    'matter_of_fact': [0, 0, 0, 0, 0, 0, 0, .16],
    'practical': [0, 0, 0, 0, 0, 0, 0, .12],
    'explain': [0, 0, 0, 0, 0, 0, 0, .18],
    'resolve': [0, .06, 0, 0, 0, 0, 0, .16],
    'firm': [0, .13, 0, 0, .02, 0, 0, .12],
    'stern': [0, .18, 0, 0, .04, 0, 0, .08],
    'challenge': [.02, .11, 0, 0, 0, 0, 0, .10],
    'reassure': [.05, 0, 0, 0, 0, 0, 0, .18],
    'regret': [0, 0, .06, 0, 0, .09, 0, .12],
    'persuade': [.03, 0, 0, 0, 0, 0, 0, .17],
    'ambition': [.05, .10, 0, 0, 0, 0, 0, .08],
    'wry': [.07, 0, 0, 0, .03, 0, 0, .10],
    'warm': [.12, 0, 0, 0, 0, 0, 0, .14],
    'concern': [0, 0, .04, .025, 0, 0, 0, .15],
    'approval': [.07, 0, 0, 0, 0, 0, 0, .15],
    'brisk': [.02, .12, 0, 0, 0, 0, 0, .06],
}


def trim_quiet_edges(wave, sr):
    """Remove only near-silent excess, retaining generous consonant/breath margins."""
    frame = max(1, int(.01 * sr))
    energies = np.array([np.sqrt(np.mean(wave[i:i+frame] ** 2))
                         for i in range(0, len(wave), frame)])
    active = np.flatnonzero(energies > 10 ** (-52 / 20))
    if not len(active):
        raise ValueError('No audible speech')
    first = max(0, int(active[0] * frame - .10 * sr))
    last = min(len(wave), int((active[-1] + 1) * frame + .16 * sr))
    return wave[first:last], {'trim_head_s': first / sr,
                              'trim_tail_s': (len(wave)-last) / sr}


def master(raw, target, ffmpeg):
    """Measure loudness, then apply bounded static gain; preserve performance dynamics."""
    result = subprocess.run([str(ffmpeg), '-hide_banner', '-i', str(raw), '-af',
                             'loudnorm=I=-20:TP=-2:LRA=11:print_format=json',
                             '-f', 'null', '-'], capture_output=True, text=True, check=True)
    measured = json.loads(re.findall(r'\{[^{}]+\}', result.stderr)[-1])
    gain = min(6., -20 - float(measured['input_i']), -2 - float(measured['input_tp']))
    gain = max(-12., gain)
    subprocess.run([str(ffmpeg), '-y', '-v', 'error', '-i', str(raw),
                    '-af', f'volume={gain:.4f}dB', '-ac', '1', '-ar', '44100',
                    '-c:a', 'pcm_s24le', str(target)], check=True)
    return {'input_lufs': float(measured['input_i']), 'input_true_peak_db': float(measured['input_tp']),
            'static_gain_db': gain, 'processing': 'static gain only; no pitch shift, reverb or hard gate'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', action='append')
    args = parser.parse_args()
    plan = json.loads((OUT/'performance-score.json').read_text())
    references = {
        'scourge-male': ROOT/'tools/samples/undead/maximillion-forsaken-victory-reference.wav',
        'scourge-female': ROOT/'tools/samples/elreth/elreth-reference.wav',
    }
    ffmpeg = next((ROOT/'.local-tools/ffmpeg').rglob('ffmpeg.exe'))
    raw_dir = OUT/'raw'; raw_dir.mkdir(exist_ok=True)
    manifest_path = OUT/'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'model': 'IndexTTS-2.5', 'installed': False, 'seed': plan['seed'],
        'references': {k: {'path': str(v), 'sha256': hashlib.sha256(v.read_bytes()).hexdigest()}
                       for k, v in references.items()}, 'tone_vectors': TONES, 'files': []}
    from indextts.infer_v2_5 import IndexTTS2
    model = IndexTTS2(cfg_path='checkpoints/config.yaml', model_dir='checkpoints',
                      use_bf16=True, use_cuda_kernel=False, use_deepspeed=False,
                      use_accel=False, use_torch_compile=False, use_qwen_emo=False)
    for row in plan['files']:
        base = row['base']
        if args.only and base not in args.only:
            continue
        if any(r['base'] == base for r in manifest['files']):
            continue
        audio = []; beat_records = []
        for n, beat in enumerate(row['beats']):
            path = raw_dir/f'{base}-beat-{n}.wav'
            kwargs = {'emo_vector': TONES[beat['tone']], 'emo_alpha': 1.0} if beat['tone'] != 'impatient' else {
                'emo_audio_prompt': str(OUT/'references/563164.ogg'), 'emo_alpha': .24}
            if not path.exists():
                random.seed(plan['seed']); np.random.seed(plan['seed']); torch.manual_seed(plan['seed'])
                model.infer(spk_audio_prompt=str(references[row['voice']]), text=beat.get('synthesis_text', beat['text']),
                            lang='EN', output_path=str(path), verbose=False, use_random=False,
                            duration_factor=beat['duration_factor'], interval_silence=180,
                            max_text_tokens_per_segment=160, **kwargs)
            wave, sr = sf.read(path)
            assert wave.ndim == 1 and np.isfinite(wave).all(), path
            wave, trims = trim_quiet_edges(wave, sr)
            if not audio:
                audio.append(np.zeros(int(sr * .08)))
            offset = sum(len(a) for a in audio)/sr
            audio.append(wave)
            # Existing breath/consonant margins remain, plus a restrained thought pause.
            gap = beat['pause_after'] if n < len(row['beats'])-1 else row['tail_s']
            audio.append(np.zeros(int(sr * gap)))
            beat_records.append({**beat, **trims, 'path': str(path), 'offset': offset,
                                 'seconds': len(wave)/sr, 'controls': kwargs})
        raw = raw_dir/f'{base}-assembled.wav'; sf.write(raw, np.concatenate(audio), sr, subtype='PCM_24')
        wav = OUT/f'{base}.wav'; processing = master(raw, wav, ffmpeg)
        mp3 = OUT/f'{base}.mp3'
        subprocess.run([str(ffmpeg), '-y', '-v', 'error', '-i', str(wav),
                        '-codec:a', 'libmp3lame', '-q:a', '2', str(mp3)], check=True)
        record = {**row, 'beats': beat_records, 'post': processing,
                  'seconds': sf.info(wav).duration, 'sha256': hashlib.sha256(mp3.read_bytes()).hexdigest()}
        manifest['files'].append(record)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"[{len(manifest['files'])}/18] {base}: {record['seconds']:.1f}s", flush=True)
    print('DONE', OUT, flush=True)


if __name__ == '__main__':
    main()
