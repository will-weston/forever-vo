"""Build word-weighted, single-voice references and a clean IndexTTS audition plan.

No addon files are changed. Stock recordings are matched by verified FileDataID.
"""
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from prepare_profile_auditions import ROOT, OUT, QUEST_ORDER, digest, save


def words(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())


def audio(path, rate=24000):
    wave, sr = sf.read(path)
    if wave.ndim > 1:
        wave = wave.mean(axis=1)
    divisor = math.gcd(sr, rate)
    return resample_poly(wave, rate // divisor, sr // divisor)


def main():
    registry_path = ROOT / 'tools/voice_profiles/tirisfal.json'
    registry = json.loads(registry_path.read_text())
    cfg = registry['selection']
    transcripts = {}
    for path in (ROOT/'.local-state/undead-greeting-transcripts.json', ROOT/'.local-state/undead-transcripts.json', ROOT/'.local-state/elreth-transcripts.json'):
        for row in json.loads(path.read_text()):
            transcripts[row['id']] = {'asr': row['text'].strip(), 'text': row['text'].strip()}
    more_path = OUT / 'additional-source-transcripts.json'
    if more_path.exists():
        transcripts.update({int(k): v for k, v in json.loads(more_path.read_text()).items()})
    # Correct obvious prior ASR substitutions; retain the raw ASR for audit.
    corrections = {563161: 'This had better be good.', 563155: 'Remember: patience, discipline.',
                   563192: 'Remember: patience, discipline.', 563204: 'Beware. Our enemies abound.',
                   563124: 'Dark Lady watch over you.', 563181: 'And you are?'}
    for fid, text in corrections.items():
        transcripts[fid]['text'] = text
    asr = None
    profiles = {}
    for profile_id, definition in registry['profiles'].items():
        candidates = []
        for activity, field in [('Greeting', 'greetings'), ('Farewell', 'farewells')]:
            for fid in definition[field]:
                matches = list((ROOT/'tools/voices/raw').glob(f'*/{fid}.ogg'))
                if not matches:
                    raise FileNotFoundError(f'Original stock recording {fid}')
                path = matches[0]
                if fid not in transcripts:
                    if asr is None:
                        import torch
                        from transformers import pipeline
                        torch.set_num_threads(3)
                        asr = pipeline('automatic-speech-recognition', model='openai/whisper-small.en', device=-1)
                    text = asr({'raw': audio(path, 16000).astype(np.float32), 'sampling_rate': 16000})['text'].strip()
                    transcripts[fid] = {'text': text, 'asr': text}
                    save(more_path, {str(k): v for k, v in transcripts.items()})
                    print('ASR', fid, text, flush=True)
                record = {'file_data_id': fid, 'activity': activity, 'kit': definition['kits'][activity],
                          'path': str(path), 'sha256': digest(path), 'seconds': sf.info(path).duration,
                          'transcript': transcripts[fid]['text'], 'asr_transcript': transcripts[fid]['asr']}
                record['word_count'] = len(words(record['transcript']))
                candidates.append(record)
        usable = [c for c in candidates if c['word_count'] >= cfg['min_clip_words'] or c['file_data_id'] in definition['mandatory']]
        groups = []
        for count in range(3, min(cfg['max_clips'], len(usable)) + 1):
            for group in itertools.combinations(usable, count):
                seconds = sum(c['seconds'] for c in group) + cfg['gap_seconds'] * (count-1)
                if seconds > cfg['max_seconds']:
                    continue
                if not set(definition['mandatory']).issubset({c['file_data_id'] for c in group}):
                    continue
                if {c['activity'] for c in group} != {'Greeting', 'Farewell'}:
                    continue
                tokens = [w for c in group for w in words(c['transcript'])]
                # Word quantity and lexical variety first; fewer tiny snippets
                # break ties. Duration is a hard constraint, not the objective.
                score = min(len(tokens), cfg['target_words']) + .3*len(set(tokens)) - .35*count
                groups.append((score, len(tokens), -count, -seconds, group))
        if not groups:
            raise ValueError(f'No complete reference fits: {profile_id}')
        selected = max(groups, key=lambda g: g[:4])[-1]
        selected = sorted(selected, key=lambda c: (c['activity'] != 'Greeting', c['file_data_id'] not in definition['mandatory'], -c['word_count'], c['file_data_id']))
        pieces = []
        for clip in selected:
            if pieces:
                pieces.append(np.zeros(round(24000*cfg['gap_seconds'])))
            pieces.append(audio(clip['path']))
        wave = np.concatenate(pieces)
        gain = min(1., .95/float(np.max(np.abs(wave))))
        reference = OUT / f'{profile_id}-source.wav'
        sf.write(reference, wave*gain, 24000, subtype='PCM_24')
        assert len(wave)/24000 <= 15
        profiles[profile_id] = {**definition, 'candidates': candidates, 'selected': selected,
            'reference': {'path': str(reference), 'sha256': digest(reference)},
            'seconds': len(wave)/24000, 'word_count': sum(c['word_count'] for c in selected),
            'unique_words': len(set(w for c in selected for w in words(c['transcript']))),
            'constant_gain': gain, 'source_urls': [n['source'] for n in registry['npcs'].values() if n['profile'] == profile_id]}
        print('REFERENCE', profile_id, profiles[profile_id]['word_count'], 'words', round(len(wave)/24000, 2), 'seconds', [c['file_data_id'] for c in selected], flush=True)
    save(OUT/'reference-manifest.json', {'registry_sha256': digest(registry_path), 'selection': cfg,
        'note': 'Word counts are lexical, not phoneme coverage. Complete original phrases; no EQ, compression, pitch changes, reverb, time stretching, or word cuts.', 'profiles': profiles})

    prior_path = ROOT/'tools/samples/deathknell-clean-nine/performance-plan.json'
    prior = json.loads(prior_path.read_text())
    stages = []
    for row in prior['files']:
        if row['quest'] not in QUEST_ORDER:
            continue
        npc = registry['npcs'][row['npc']]
        stages.append({'base': row['base'], 'quest': row['quest'], 'title': row['title'],
                       'npc': row['npc'], 'name': npc['name'], 'profile': npc['profile']})
    save(OUT/'seven-quest-casting.json', {'quest_order': QUEST_ORDER, 'stages': stages})
    plan = {'seed': 42, 'quest_order': QUEST_ORDER, 'install': False,
            'speaker_references': {p: d['reference'] for p, d in profiles.items()},
            'references': {}, 'prior_text_plan_sha256': digest(prior_path), 'files': []}
    # Seven complete offers, plus Maximillion's turn-in and an observed Forever addition.
    for row in prior['files']:
        if row['quest'] not in QUEST_ORDER or not (row['base'].endswith('-accept') or row['base']=='3099-complete'):
            continue
        row = dict(row)
        row.update(voice=registry['npcs'][row['npc']]['profile'], emotion_reference=None, emo_alpha=0., reuse_approved=False)
        row['analysis'] = {**row['analysis'], 'render_control': 'Existing reviewed punctuation; whole continuous event. Identity-only baseline, no separate angry/emotion reference.'}
        plan['files'].append(row)
    corpus = json.loads((OUT/'tirisfal-corpus.json').read_text())
    source = next(r for r in corpus['quests']['98601-accept'] if r['source_dataset']=='community')
    # A Difficult Path is a paladin quest, so resolve its class token to paladin.
    text = re.sub(r'\s+', ' ', source['text'].replace('$c', 'paladin')).strip()
    plan['files'].append({'base':'98601-accept', 'quest':98601, 'title':source['title'], 'npc':source['npc'],
        'voice':registry['npcs'][source['npc']]['profile'], 'source_text':source['text'], 'text':text,
        'analysis':{'tone':'Uneasy, dry sarcasm', 'reason':'Sarvis wants the paladin to move away before reading a holy scroll.', 'class_token':'paladin; class-specific quest'},
        'emotion_reference':None, 'emo_alpha':0., 'reuse_approved':False})
    source = next(r for r in corpus['quests']['99141-accept'] if r['source_dataset']=='local-cache')
    text = re.sub(r'\s+', ' ', source['text'].replace('$c', 'warlock')).strip()
    plan['files'].append({'base':'99141-accept', 'quest':99141, 'title':source['title'], 'npc':'1515',
        'voice':'undead-male-warrior', 'source_text':source['text'], 'text':text,
        'analysis':{'tone':'Controlled authority, impatience', 'reason':'Executor Zygand demands overdue reports. A direct command rather than a battle cry.', 'class_token':'warlock for this audition'},
        'emotion_reference':None, 'emo_alpha':0., 'reuse_approved':False})
    excerpt_ends = {
        '3099-complete': 'We seek to have creatures serve us.',
        '376-accept': "hunting the Mindless Ones, if I know his mind.",
        '3902-accept': "Most likely, they'll be in stacks of boxes.",
        '1470-accept': 'Knowledge is our greatest power.',
        '99141-accept': 'Needless to say, my patience has run out.',
    }
    for row in plan['files']:
        row['audition_scope'] = 'complete offer'
        if row['base'] in excerpt_ends:
            marker = excerpt_ends[row['base']]
            if marker not in row['text']:
                raise ValueError(f'Excerpt boundary changed: {row["base"]}')
            row['synthesis_text'] = row['text'].split(marker)[0] + marker
            row['audition_scope'] = 'opening paragraph excerpt; full source text retained in plan'
            row['generation_kwargs'] = {'temperature': .65}
            row['analysis']['retake_reason'] = 'The long pilot take had missing or degraded ending words; use a coherent continuous excerpt for casting review.'
    save(OUT/'performance-plan.json', plan)
    print('PLAN', len(plan['files']), 'continuous auditions;', len(stages), 'mapped quest stages', flush=True)


if __name__ == '__main__':
    main()
