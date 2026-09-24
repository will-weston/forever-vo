"""Render continuous, lightly guided IndexTTS WAV auditions without installing them.

Run using C:\repos\index-tts\.venv\Scripts\python.exe from that checkout.
The JSON plan contains the editorial analysis and preserves the original words.
"""
import argparse
import hashlib
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path.cwd()))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'tools/samples/deathknell-clean-nine/performance-plan.json')
    parser.add_argument('--base', action='append')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--rerender', action='store_true')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    out = args.plan.parent
    intermediates = out/'intermediates'
    intermediates.mkdir(exist_ok=True)
    references = {
        'scourge-male': ROOT/'tools/samples/undead/maximillion-forsaken-victory-reference.wav',
        'scourge-female': ROOT/'tools/samples/elreth/elreth-reference.wav',
    }
    # Auditions can use an NPC's own sound set without replacing a shared voice.
    for voice, reference in plan.get('speaker_references', {}).items():
        path = Path(reference['path'])
        if digest(path) != reference['sha256']:
            raise ValueError(f'Speaker reference changed: {voice}')
        references[voice] = path
    manifest_path = out/'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'model': 'IndexTeam/IndexTTS-2.5', 'installed': False,
        'speaker_references': {k: {'path': str(v), 'sha256': digest(v)} for k, v in references.items()},
        'duration_factor': 1., 'emotion_vector': None, 'tail_seconds': .5,
        'post': 'Float vocoder output; constant gain before PCM24 conversion; 0.5s tail. No resampling or effects.',
        'files': [],
    }
    model = None
    captured = []

    def retain_float(module, inputs, output):
        # This is after any internal vocoder bounding, but before integer conversion.
        captured.append(output.detach().float().cpu().numpy().reshape(-1).copy())
        peak = output.detach().abs().max()
        return output * (.8 / peak.clamp(min=.8))

    chosen = [r for r in plan['files'] if not args.base or r['base'] in args.base]
    if args.base and set(args.base) != {r['base'] for r in chosen}:
        raise ValueError('Unknown requested base')
    for row in chosen:
        base = row['base']
        target = out/f'{base}.wav'
        old = next((r for r in manifest['files'] if r['base'] == base), None)
        if old and not args.rerender:
            assert target.exists() and digest(target) == old['sha256'], base
            continue
        if old:
            archive = out/'previous-takes'
            archive.mkdir(exist_ok=True)
            shutil.copy2(target, archive/f"{base}-{old['sha256'][:12]}.wav")
            atomic_json(archive/f"{base}-{old['sha256'][:12]}.json", old)
        if row['reuse_approved'] and not args.rerender:
            source = ROOT/'tools/samples/rattlecages-clean-retake/rattlecages-continuous-light-reference.wav'
            shutil.copy2(source, target)
            prior = json.loads((source.parent/'provenance.json').read_text())
            record = {**row, 'seed': 42, 'reused_approved': True,
                      'source_float_peak': prior['source_float_peak'], 'gain': prior['gain'],
                      'vocoder_chunks': 1, 'source': str(source)}
        else:
            if model is None:
                from indextts.infer_v2_5 import IndexTTS2
                model = IndexTTS2(cfg_path='checkpoints/config.yaml', model_dir='checkpoints',
                                  use_bf16=True, use_cuda_kernel=False, use_deepspeed=False,
                                  use_accel=False, use_torch_compile=False, use_qwen_emo=False)
                model.bigvgan.register_forward_hook(retain_float)
            seed = args.seed if args.seed is not None else plan['seed']
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            captured.clear()
            kwargs = {}
            if row['emotion_reference']:
                ref = plan['references'][row['emotion_reference']]
                assert digest(Path(ref['path'])) == ref['sha256']
                kwargs = {'emo_audio_prompt': ref['path'], 'emo_alpha': row['emo_alpha']}
            intermediate = intermediates/f'{base}.wav'
            model.infer(spk_audio_prompt=str(references[row['voice']]), text=row.get('synthesis_text', row['text']),
                        lang='EN', output_path=str(intermediate), duration_factor=1.,
                        max_text_tokens_per_segment=256, use_random=False,
                        **row.get('generation_kwargs', {}), **kwargs)
            if len(captured) != 1:
                raise ValueError(f'{base}: expected one continuous waveform, got {len(captured)}')
            wave = captured[0]
            assert np.isfinite(wave).all() and np.max(np.abs(wave)) > 0, base
            peak = float(np.max(np.abs(wave)))
            gain = min(1., .75 / peak)
            sr = sf.info(intermediate).samplerate
            final = np.concatenate([wave * gain, np.zeros(int(sr * .5))])
            sf.write(target, final, sr, subtype='PCM_24')
            record = {**row, 'seed': seed, 'reused_approved': False,
                      'source_float_peak': peak, 'gain': gain, 'vocoder_chunks': len(captured)}
        audio, sr = sf.read(target)
        assert np.isfinite(audio).all() and max(abs(audio)) <= .750001, base
        assert np.max(abs(audio[-int(.49*sr):])) == 0, base
        record.update({'seconds': len(audio)/sr, 'sample_rate': sr,
                       'format': sf.info(target).subtype, 'sha256': digest(target)})
        manifest['files'] = [r for r in manifest['files'] if r['base'] != base] + [record]
        atomic_json(manifest_path, manifest)
        print(f"[{len(manifest['files'])}/{len(plan['files'])}] {base}: {record['seconds']:.1f}s", flush=True)
    print('DONE', out, flush=True)


if __name__ == '__main__':
    main()
