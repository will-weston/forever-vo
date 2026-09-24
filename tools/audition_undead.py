"""Audition individual undead greeting sets without changing the installed pack."""
import argparse
import json
import random
import subprocess

import numpy as np
import soundfile as sf
import torch

from config import TOOLS_DIR, VOICES_DIR
from wowdata import fetch_file

OUT = TOOLS_DIR / 'samples' / 'undead'
TEXT = "We Forsaken are at war with the Lich King's army of the Scourge. Mindless undead roam these woods. Show them no mercy."
# NPCSounds 82: Shadow Priest Sarvis and Maximillion. NPCSounds 83: Undertaker Mordo.
SETS = {
    'sarvis': [563161, 563162, 563157, 563150, 563158, 563163, 563151,
               563147, 563154, 563167, 563148, 563152, 563155, 563165],
    'mordo': [563174, 563172, 563175, 563180, 563183, 563181,
              563177, 563178, 563176, 563185, 563173],
    # NPCSounds 84, used by Deathguard Dillinger and other undead guards.
    'deathguard': [563198, 563199, 563188, 563190, 563191, 563195,
                  563194, 563196, 563187, 563204, 563189, 563205, 563192, 563202],
    # Sarvis's greeting-only material, without the farewell-heavy selection.
    'dark-greetings': [563161, 563162, 563157, 563150, 563158, 563163, 563151],
    # VocalUISounds RaceID 5, NormalSoundID_0 (male), kits 2054-2058 and 2060.
    'undead-player': [542633, 542631, 542623, 542666, 542632, 542663, 542674,
                      542630, 542622, 542621, 542653, 542644, 542655],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', choices=sorted(SETS), action='append')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    references = {}
    provenance = {'text': TEXT, 'voices': {}}
    for name in args.voice or ['sarvis', 'mordo']:
        ids = SETS[name]
        usable = []
        for fdid in ids:
            path = VOICES_DIR / 'raw' / 'scourge-male' / f'{fdid}.ogg'
            if not path.exists():
                fetch_file(fdid, path)
            wave, sr = sf.read(path)
            duration = len(wave) / sr
            if 0.8 <= duration <= 8:
                usable.append((duration, fdid, path))
        chosen, total = [], 0
        for duration, fdid, path in sorted(usable, reverse=True):
            chosen.append((fdid, path))
            total += duration
            if total >= 10:
                break
        if total < 4:
            raise RuntimeError(f'Insufficient reference audio for {name}')
        concat = OUT / f'{name}-concat.txt'
        concat.write_text(''.join(f"file '{p.resolve().as_posix()}'\n" for _, p in chosen))
        reference = OUT / f'{name}-original.wav'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(concat),
                        '-ac', '1', '-ar', '24000', str(reference)], check=True)
        references[name] = reference
        provenance['voices'][name] = {'fileDataIDs': [i for i, _ in chosen], 'seconds': total}
        print(f'{name}: {total:.1f}s reference from one NPC sound set', flush=True)

    from chatterbox.tts import ChatterboxTTS
    model = ChatterboxTTS.from_pretrained(device='cuda')
    for name, reference in references.items():
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)
        wav = model.generate(TEXT, audio_prompt_path=str(reference), exaggeration=0.3, cfg_weight=0.8)
        path = OUT / f'{name}-audition.wav'
        sf.write(path, wav.squeeze().cpu().numpy(), model.sr)
        print(f'{path}: {wav.shape[-1] / model.sr:.1f}s', flush=True)
    provenance.update({'exaggeration': 0.3, 'cfg_weight': 0.8, 'seed': 42})
    (OUT / ('provenance-' + '-'.join(references) + '.json')).write_text(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
