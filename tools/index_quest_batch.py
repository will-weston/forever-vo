"""Stage selected quests with IndexTTS 2.5; optionally install the verified batch.

Run with the isolated IndexTTS Python, with the IndexTTS checkout as cwd.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ['FOREVER_VO_DATA_DIR'] = str(ROOT / '.local-state')
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
sys.path.insert(0, str(Path.cwd()))

import numpy as np
import soundfile as sf
import torch


# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.config import PACK_DATA_DIR, SOUND_INDEX, SOUNDS_DIR
from tools.generate import load_sources, load_items, rebuild_tables, save_sound_index
from tools.textclean import chunk, is_speakable
from tools.textkey import text_key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quest', action='append', type=int, default=[])
    parser.add_argument('--quest-file', type=Path)
    parser.add_argument('--skip-current', action='store_true')
    parser.add_argument('--extra-references', type=Path)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    quest_ids = set(args.quest)
    if args.quest_file:
        quest_ids.update(json.loads(args.quest_file.read_text()))
    if not quest_ids:
        parser.error('Specify quests or a quest selection file')
    items = load_items(load_sources(), include_progress=True)
    selected = [i for i in items if i.kind == 'quests' and i.entry['questID'] in quest_ids]
    if {i.entry['questID'] for i in selected} != quest_ids:
        raise ValueError('One or more requested quests are missing')
    references = {
        'scourge-male': ROOT / 'tools/samples/undead/maximillion-forsaken-victory-reference.wav',
        'scourge-female': ROOT / 'tools/samples/elreth/elreth-reference.wav',
    }
    if args.extra_references:
        extra = json.loads(args.extra_references.read_text())
        references.update({k: Path(v) for k, v in extra['references'].items()})
        for item in selected:
            item.voice = extra.get('npc_voices', {}).get(str(item.speaker_key), item.voice)
    for item in selected:
        if item.voice not in references:
            raise ValueError(f'No approved reference for {item.voice}')
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    stage = ROOT / '.local-state/index-batches' / stamp
    stage.mkdir(parents=True)
    ffmpeg = next((ROOT / '.local-tools/ffmpeg').rglob('ffmpeg.exe'))
    jobs = [(item, variant.base, variant.text) for item in selected for variant in item.variants()]
    current_index = json.loads(SOUND_INDEX.read_text()) if SOUND_INDEX.exists() else {}
    reused = []
    if args.skip_current:
        pending = []
        for job in jobs:
            item, base, text = job
            record = current_index.get(base, {})
            if (record.get('engine') == 'indextts-2.5' and record.get('v') == item.voice
                    and record.get('t') == text_key(text)
                    and (SOUNDS_DIR / 'Quests' / f'{base}.mp3').exists()):
                reused.append(base)
            else:
                pending.append(job)
        jobs = pending
    manifest = {
        'model': 'IndexTeam/IndexTTS-2.5', 'quest_ids': sorted(quest_ids),
        'seed': 42, 'duration_factor': 1.0, 'emotion_override': False,
        'tone_policy': 'Preserve approved reference delivery for this first IndexTTS trial; no angry-reference mixing.',
        'reused': reused,
        'references': {k: {'path': str(v), 'sha256': hashlib.sha256(v.read_bytes()).hexdigest()}
                       for k, v in references.items()}, 'files': [], 'installed': False,
    }
    print(f'Staging {len(jobs)} recordings for {len(quest_ids)} quests in {stage}', flush=True)
    from indextts.infer_v2_5 import IndexTTS2
    model = IndexTTS2(cfg_path='checkpoints/config.yaml', model_dir='checkpoints',
                      use_bf16=True, use_cuda_kernel=False, use_deepspeed=False,
                      use_accel=False, use_torch_compile=False, use_qwen_emo=False)
    updates = {}
    for number, (item, base, text) in enumerate(jobs, 1):
        if not is_speakable(text):
            raise ValueError(f'Unresolved game markup in {base}')
        spoken = text.replace('--', ', ').replace(' - ', ', ')
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)
        wav_path = stage / f'{base}.wav'
        # This long monologue lost its ending in the first full-length rendering.
        segments = chunk(spoken, max_chars=220) if base == '3099-complete' or len(spoken) > 450 else [spoken]
        segments_audio = []
        for part_number, segment in enumerate(segments):
            part_path = wav_path if len(segments) == 1 else stage / f'{base}-part-{part_number}.wav'
            model.infer(spk_audio_prompt=str(references[item.voice]), text=segment, lang='EN',
                        output_path=str(part_path), verbose=False, use_random=False, duration_factor=1.0)
            if len(segments) > 1:
                part_audio, part_sr = sf.read(part_path)
                if segments_audio:
                    segments_audio.append(np.zeros(int(part_sr * .2)))
                segments_audio.append(part_audio)
        if len(segments) > 1:
            sf.write(wav_path, np.concatenate(segments_audio), part_sr)
        wave, sr = sf.read(wav_path)
        if not np.isfinite(wave).all() or np.max(np.abs(wave)) == 0:
            raise ValueError(f'Invalid audio: {base}')
        duration = len(wave) / sr
        mp3 = stage / f'{base}.mp3'
        subprocess.run([str(ffmpeg), '-y', '-v', 'error', '-i', str(wav_path), '-ac', '1',
                        '-ar', '44100', '-codec:a', 'libmp3lame', '-q:a', '4', str(mp3)], check=True)
        if abs(sf.info(mp3).duration - duration) > .15:
            raise ValueError(f'Encoded duration mismatch: {base}')
        updates[base] = {'d': duration, 'v': item.voice, 't': text_key(text), 'engine': 'indextts-2.5'}
        manifest['files'].append({'base': base, 'quest': item.entry['questID'], 'npc': item.speaker_key,
                                  'title': item.entry['title'], 'text': spoken, 'seconds': duration,
                                  'segments': segments,
                                  'voice': item.voice, 'sha256': hashlib.sha256(mp3.read_bytes()).hexdigest()})
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        print(f'[{number}/{len(jobs)}] {base}: {duration:.1f}s ({item.entry["title"]})', flush=True)
    if args.install:
        backup = ROOT / '.local-state/backups' / f'before-index-batch-{stamp}'
        backup.mkdir(parents=True)
        shutil.copy2(SOUND_INDEX, backup / 'sound_index.json')
        shutil.copytree(PACK_DATA_DIR, backup / 'Data')
        for _, base, _ in jobs:
            target = SOUNDS_DIR / 'Quests' / f'{base}.mp3'
            if target.exists():
                shutil.copy2(target, backup / target.name)
            shutil.copy2(stage / f'{base}.mp3', target)
        save_sound_index(updates)
        rebuild_tables(items, updates)
        manifest.update({'installed': True, 'backup': str(backup)})
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        (ROOT / '.local-state/latest-index-batch.json').write_text(json.dumps(manifest, indent=2))
        print(f'Installed {len(jobs)} recordings; backup: {backup}', flush=True)
    print('DONE', stage, flush=True)


if __name__ == '__main__':
    main()
