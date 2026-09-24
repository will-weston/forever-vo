"""Prepare Silverpine's complete available dialogue using the approved native-profile recipe."""
import csv
import itertools
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / '.local-state/profile-packs/silverpine-20260923'
UPSTREAM = Path('C:/repos/wow-voice-research/forever-vo-upstream/tools/data')
os.environ['FOREVER_VO_DATA_DIR'] = str(ROOT / '.local-state')
sys.path.insert(0, str(ROOT / 'tools'))
from generate import load_sources
from ingest import repair_entry, Repairs, SourceTexts
from textclean import clean, split_gender, has_gender_branch, is_speakable, chunk
from textkey import text_key
from tirisfal_profile_prepare import read_audio, words, sha, save
from wowdata import fetch_file

OBSERVED = {
    '259611': (141689, 'deathguard-baldren'),
    '248755': (131648, 'lumina-windsinger'),
    '259620': (131648, 'lumina-windsinger'),
    '250686': (136424, 'tabitha-heartweaver'),
    '248840': (129405, 'trevan-rol'),
}


def assemble(profile, hello, bye, kits, transcripts):
    """Whole native greeting/farewell clips, word coverage, 14.8-second ceiling."""
    candidates = []
    seen = set()
    asr = None
    for activity, kit in [('Greeting', hello), ('Farewell', bye)]:
        if not kit:
            continue
        for fid in kits[kit]:
            if fid in seen:
                continue
            seen.add(fid)
            cached = list((ROOT / 'tools/voices/raw').glob(f'*/{fid}.ogg'))
            path = cached[0] if cached else fetch_file(fid, STAGE / f'references/raw/{fid}.ogg')
            if str(fid) not in transcripts:
                if asr is None:
                    import torch
                    from transformers import pipeline
                    torch.set_num_threads(3)
                    asr = pipeline('automatic-speech-recognition', model='openai/whisper-small.en', device=-1)
                transcripts[str(fid)] = asr({'raw': read_audio(path, 16000).astype(np.float32),
                    'sampling_rate': 16000})['text'].strip()
                save(STAGE / 'reference-transcripts.json', transcripts)
                print('REFERENCE', profile, fid, transcripts[str(fid)], flush=True)
            text = transcripts[str(fid)]
            seconds = sf.info(path).duration
            if re.search(r'(.)\1{8,}', text) or len(words(text)) > max(15, seconds * 6):
                continue
            candidates.append({'file_data_id': fid, 'activity': activity, 'kit': kit,
                'path': str(path), 'sha256': sha(path), 'text': text,
                'words': len(words(text)), 'seconds': seconds})
    usable = [c for c in candidates if c['words'] >= 3]
    if len(usable) < 3 or (bye and not any(c['activity'] == 'Farewell' for c in usable)):
        usable = [c for c in candidates if c['words'] >= 2]
    groups = []
    for count in range(2, min(7, len(usable)) + 1):
        for group in itertools.combinations(usable, count):
            duration = sum(c['seconds'] for c in group) + .08 * (count - 1)
            if duration > 14.8:
                continue
            if hello and bye and {c['activity'] for c in group} != {'Greeting', 'Farewell'}:
                continue
            tokens = [w for c in group for w in words(c['text'])]
            groups.append((min(len(tokens), 30) + .3 * len(set(tokens)) - .35 * count,
                -count, -duration, group))
    if not groups:
        raise ValueError(f'Insufficient native speech: {profile}')
    chosen = sorted(max(groups, key=lambda r: r[:3])[-1],
        key=lambda c: (c['activity'] != 'Greeting', -c['words'], c['file_data_id']))
    wave = np.concatenate([part for i, c in enumerate(chosen)
        for part in ((np.zeros(1920), read_audio(c['path'])) if i else (read_audio(c['path']),))])
    wave *= min(1., .95 / float(abs(wave).max()))
    out = STAGE / f'references/{profile}.wav'
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, wave, 24000, subtype='PCM_24')
    reference = {'path': str(out), 'sha256': sha(out), 'word_count': sum(c['words'] for c in chosen),
        'seconds': len(wave) / 24000, 'approved_pilot': False}
    return reference, {'candidates': candidates, 'selected': chosen, 'reference': reference}


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    upstream = json.loads((UPSTREAM / 'capture.json').read_text())
    cache = json.loads((UPSTREAM / 'bulk/questcache.json').read_text())
    with sqlite3.connect(ROOT / '.local-state/classicdb/sqlite-dump/mangos.sqlite') as db:
        ids = {r[0] for r in db.execute('SELECT entry FROM quest_template WHERE ZoneOrSort IN (130,209)')}
    ids.update(r['questID'] for r in upstream['quests'].values() if r.get('zone') == 'Silverpine Forest')
    ids.add(445)  # Existing Tirisfal handoff, Delivery to Silverpine Forest.
    prior_plans = {zone: json.loads((ROOT / f'.local-state/profile-packs/{zone}-20260923/plan.json').read_text())
        for zone in ['tirisfal', 'mulgore']}
    protected = set().union(*(set(p['quest_ids']) for p in prior_plans.values()))
    existing = ids & protected
    new_ids = ids - protected
    imports = {'version': 2, 'quests': {}, 'npcs': {}, 'gossip': {}}
    for key, row in cache['quests'].items():
        if row['questID'] in new_ids:
            imports['quests'][key] = row
    repairs = Repairs()
    sources = SourceTexts()
    sources.quests.update({k: r['text'] for k, r in cache['quests'].items()})
    for key, row in upstream['quests'].items():
        if row['questID'] not in new_ids:
            continue
        fixed = repair_entry(row, 'quests', key, sources, repairs)
        if fixed is None:
            raise ValueError(f'Unrepairable capture: {key}')
        imports['quests'][key] = {**fixed, 'source': 'community'}
        npc = str(fixed.get('npc'))
        if npc in upstream['npcs']:
            imports['npcs'][npc] = dict(upstream['npcs'][npc])
    for npc, (display, slug) in OBSERVED.items():
        if npc in imports['npcs']:
            imports['npcs'][npc].update(displayID=display,
                display_source=f'https://www.wowhead.com/forever/npc={npc}/{slug}')
    imports['provenance'] = {'upstream_commit': '600a37d4e08b1b3a8d27fbfa00c8c685f4d014f7',
        'capture_sha256': sha(UPSTREAM / 'capture.json'), 'questcache_sha256': sha(UPSTREAM / 'bulk/questcache.json'),
        'sources': [str(UPSTREAM / 'capture.json'), str(UPSTREAM / 'bulk/questcache.json')],
        'covered_quest_ids': sorted(ids), 'already_installed_quest_ids': sorted(existing),
        'repairs': {'reconciled': repairs.reconciled, 'restored': repairs.restored, 'dropped': repairs.dropped}}
    save(ROOT / '.local-state/bulk/silverpine-forever.json', imports)
    data = load_sources()
    selected = {k: r for k, r in data['quests'].items() if r['questID'] in new_ids}
    assert {r['questID'] for r in selected.values()} == new_ids
    dbdir = ROOT / '.local-state/db2/1.60.1.69913'
    def table(name):
        return {r['ID']: r for r in csv.DictReader((dbdir / (name + '.csv')).open(encoding='utf-8'))}
    displays, sounds, entries = table('CreatureDisplayInfo'), table('NPCSounds'), table('SoundKitEntry')
    kits = {}
    for r in entries.values():
        kits.setdefault(int(r['SoundKitID']), []).append(int(r['FileDataID']))
    reused = {}
    all_references = {}
    for zone, prior in prior_plans.items():
        registry = json.loads((ROOT / f'tools/voice_profiles/{zone}-production.json').read_text())
        all_references.update(prior['references'])
        for c in registry['npcs'].values():
            if c.get('npc_sound_id') not in (None, '', '0') and not c.get('fallback'):
                reused[str(c['npc_sound_id'])] = c['profile']
    casting = {}
    row_cast = {}
    definitions = {}
    for key, row in selected.items():
        npc_key = str(row.get('npc'))
        alaric = row['questID'] in (460, 461) and key != '460-progress'
        cast_key = 'character:alaric' if alaric else npc_key
        row_cast[key] = cast_key
        if cast_key in casting:
            continue
        npc = data['npcs'].get(npc_key, {})
        display_id = npc.get('displayID')
        sound_id = displays.get(str(display_id), {}).get('NPCSoundID')
        sound = sounds.get(sound_id, {})
        hello, bye = int(sound.get('SoundID_0') or 0), int(sound.get('SoundID_1') or 0)
        fallback = None
        if alaric:
            profile = 'undead-male-standard'
            fallback = 'Alaric speaks through an item and objects; no native NPC greeting is available. Editorial casting uses the existing undead male standard family consistently across his five spoken stages.'
        elif hello or bye:
            profile = reused.get(str(sound_id), 'npc-sound-' + str(sound_id))
            if profile not in all_references:
                definitions[profile] = (hello, bye)
        elif npc_key == '4444':
            profile = 'narrator'
            fallback = "Vincent's completion describes his dead body; use narration, not a speaking corpse."
        elif npc_key == 'None' or npc_key.startswith('-') or npc.get('isObject'):
            profile = 'narrator'
            fallback = 'Item, object, grave, or corpse description.'
        else:
            raise ValueError(f'Unmapped speaker {npc_key}: {npc}')
        casting[cast_key] = {'npc': row.get('npc'), 'name': 'Alaric' if alaric else row.get('name') or npc.get('name') or 'Narrator',
            'display_id': display_id, 'npc_sound_id': sound_id, 'greeting_kit': hello, 'farewell_kit': bye,
            'profile': profile, 'fallback': fallback,
            'evidence': (npc.get('display_source') or 'Classic NPC display ID') + ' → cached CreatureDisplayInfo.NPCSoundID → NPCSounds'}
    save(STAGE / 'casting.json', {'npcs': casting, 'row_cast': row_cast,
        'db2_hashes': {n: sha(dbdir / (n + '.csv')) for n in ['CreatureDisplayInfo', 'NPCSounds', 'SoundKitEntry']}})
    transcripts = {}
    for p in [ROOT / '.local-state/profile-packs/tirisfal-20260923/reference-transcripts.json',
              ROOT / '.local-state/profile-packs/mulgore-20260923/reference-transcripts.json', STAGE / 'reference-transcripts.json']:
        if p.exists():
            transcripts.update(json.loads(p.read_text()))
    references, provenance = {}, {}
    for profile in sorted({c['profile'] for c in casting.values()}):
        if profile == 'narrator':
            references[profile] = {**prior_plans['tirisfal']['references']['human-male-standard'], 'reused_from': 'Tirisfal neutral narration'}
        elif profile in all_references:
            references[profile] = {**all_references[profile], 'reused_from': 'Installed native-profile pack'}
        else:
            references[profile], provenance[profile] = assemble(profile, *definitions[profile], kits, transcripts)
        assert sha(Path(references[profile]['path'])) == references[profile]['sha256']
    jobs = []
    narration = []
    for key, row in sorted(selected.items(), key=lambda pair: (pair[1]['questID'], {'accept': 0, 'progress': 1, 'complete': 2}[pair[1]['event']])):
        cast = casting[row_cast[key]]
        source_text = row['text']
        prepared = source_text
        if not clean(prepared) and cast['profile'] == 'narrator':
            prepared = prepared.replace('<', '').replace('>', '')
            narration.append(key)
        original = clean(prepared)
        variants = [('m-' + key, split_gender(original)[0]), ('f-' + key, split_gender(original)[1])] if has_gender_branch(original) else [(key, original)]
        for base, text in variants:
            assert is_speakable(text), (base, text)
            original = text
            text = text.replace('--', ', ').replace(' - ', ', ')
            # Emphasis markers are visual; preserve the words and the original lookup key.
            text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
            if key == '444-accept':
                text = text.replace('you brought me and separated', 'you brought me, and separated')
            if key == '95034-accept':
                text = text.replace('"worgen"', 'worgen')
            parts = chunk(text, max_chars=340) if len(words(text)) > 60 else [text]
            assert ' '.join(text.split()) == ' '.join(' '.join(parts).split()), base
            assert max(len(words(p)) for p in parts) <= 85, (base, 'overlong passage')
            jobs.append({'base': base, 'quest': row['questID'], 'event': row['event'], 'title': row['title'],
                'npc': row.get('npc'), 'name': 'Alaric' if row_cast[key] == 'character:alaric' else row.get('name') or cast['name'],
                'profile': cast['profile'], 'source_text': source_text, 'text': text, 'text_key': text_key(original),
                'parts': parts, 'reuse': None, 'source': row.get('source'),
                'reference_sha256': references[cast['profile']]['sha256']})
    plan = {'version': 1, 'zone': 'silverpine', 'model': 'IndexTeam/IndexTTS-2.5', 'formula': 'native-profile-word-coverage-v1',
        'seed': 43, 'temperature': .65, 'duration_factor': 1., 'tail_seconds': .5, 'paragraph_gap_seconds': .12,
        'references': references, 'quest_ids': sorted(new_ids), 'covered_quest_ids': sorted(ids),
        'already_installed_quest_ids': sorted(existing), 'files': jobs, 'narrated_bracketed_descriptions': narration,
        'policy': 'Full dialogue in complete sentence/paragraph groups; float capture, one constant gain, native PCM24. No EQ/reverb/compression/tempo or per-sentence acting edits.'}
    save(STAGE / 'plan.json', plan)
    save(STAGE / 'sources.json', {'quests': selected, 'npcs': data['npcs'], 'gossip': {}})
    save(STAGE / 'reference-provenance.json', provenance)
    save(ROOT / 'tools/voice_profiles/silverpine-production.json', {'formula': plan['formula'], 'references': references, 'npcs': casting})
    save(ROOT / '.local-state/latest-silverpine-profile-pack.json', {'stage': str(STAGE), 'installed': False})
    print('READY', len(new_ids), 'new quests +', len(existing), 'already installed;', len(jobs), 'new recordings;', len(references), 'profiles;', sum(len(words(r['text'])) for r in jobs), 'words', flush=True)


if __name__ == '__main__':
    main()
