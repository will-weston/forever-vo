"""Build Elreth's ~10-second reference and audition The Damned without installing it."""
import csv
import itertools
import json
import random

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly

import sys
from pathlib import Path

# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.config import BETA_BUILD, DATA_DIR, TOOLS_DIR, VOICES_DIR
from tools.textclean import clean, chunk


def main():
    out = TOOLS_DIR / 'samples' / 'elreth'
    out.mkdir(parents=True, exist_ok=True)
    # Wowhead NPC 1661: greetings 6046, farewells 6047, angry 6048.
    # Editorial assessment of quest 376: helpful, cautionary, dry humor.
    # References to wounds/death are not hostility toward the listener.
    allowed_kits = {6046, 6047}
    candidates = []
    with (DATA_DIR / 'db2' / BETA_BUILD / 'SoundKitEntry.csv').open() as stream:
        for row in csv.DictReader(stream):
            kit, fdid = int(row['SoundKitID']), int(row['FileDataID'])
            if kit not in allowed_kits:
                continue
            path = VOICES_DIR / 'raw' / 'scourge-female' / f'{fdid}.ogg'
            seconds = sf.info(path).duration
            if 1.8 <= seconds <= 3.0:
                candidates.append({'id': fdid, 'kit': kit, 'seconds': seconds, 'path': path})
    choices = [group for n in range(3, min(6, len(candidates)) + 1)
               for group in itertools.combinations(candidates, n)
               if {c['kit'] for c in group} == allowed_kits]
    if not choices:
        raise RuntimeError('Insufficient longer clips from Elreth\'s voice set')
    def score(group):
        duration = sum(c['seconds'] for c in group) + 0.1 * (len(group) - 1)
        return abs(duration - 10), sum(abs(c['seconds'] - 2) for c in group)
    chosen = sorted(min(choices, key=score), key=lambda c: (c['kit'], -c['seconds']))
    pieces = []
    for c in chosen:
        wave, sr = sf.read(c['path'])
        if wave.ndim > 1:
            wave = wave.mean(axis=1)
        if pieces:
            pieces.append(np.zeros(2400))
        pieces.append(resample_poly(wave, 24000, sr))
    reference = out / 'elreth-reference.wav'
    ref_wave = np.concatenate(pieces)
    sf.write(reference, ref_wave, 24000)
    manifest = {
        'npc': 1661, 'quest': 376,
        'source': 'https://www.wowhead.com/classic/npc=1661/novice-elreth#sounds',
        'tone_assessment': 'Helpful and practical, cautionary progress, dry humor on completion; no anger.',
        'angry_clips': False, 'reference_seconds': len(ref_wave) / 24000,
        'clips': [{k: v for k, v in c.items() if k != 'path'} for c in chosen],
        'cfg_weight': 0.3, 'exaggeration': 0.3, 'seed': 42, 'outputs': [],
    }
    print(json.dumps(manifest, indent=2), flush=True)
    from chatterbox.tts import ChatterboxTTS
    model = ChatterboxTTS.from_pretrained(device='cuda')
    quests = json.loads((DATA_DIR / 'bulk' / 'classic.json').read_text(encoding='utf-8'))['quests']
    for event in ['accept', 'progress', 'complete']:
        text = clean(quests[f'376-{event}']['text']).replace('--', ', ')
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)
        pieces = []
        for part in chunk(text):
            if pieces:
                pieces.append(np.zeros(int(model.sr * 0.25)))
            wave = model.generate(part, audio_prompt_path=str(reference),
                                  cfg_weight=0.3, exaggeration=0.3)
            pieces.append(wave.squeeze().cpu().numpy())
        audio = np.concatenate(pieces)
        assert np.isfinite(audio).all() and np.max(np.abs(audio)) > 0
        path = out / f'the-damned-{event}.wav'
        sf.write(path, audio, model.sr)
        manifest['outputs'].append({'event': event, 'text': text, 'seconds': len(audio) / model.sr})
        print(f'{event}: {len(audio) / model.sr:.1f}s', flush=True)
    (out / 'provenance.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
