"""Gather verifiable Wowhead voice sets and stage Tirisfal dialogue for local auditions.

This never writes addon folders. Run with the project's audio Python environment.
"""
from __future__ import annotations

import concurrent.futures
import argparse
import hashlib
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/samples/tirisfal-stock-profiles'
EVIDENCE = OUT / 'evidence'
RESEARCH = Path('C:/repos/wow-voice-research')
NPCS = {1568: 'Undertaker Mordo', 1569: 'Shadow Priest Sarvis',
        2126: 'Maximillion', 1661: 'Novice Elreth', 1740: 'Deathguard Saltain',
        1515: 'Executor Zygand', 244808: 'Aramis Hammerhand'}
QUEST_ORDER = [363, 364, 3099, 376, 3901, 3902, 1470]


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_page(kind, ident, version):
    path = EVIDENCE / f'{version}-{kind}-{ident}.html'
    url = f'https://www.wowhead.com/{version}/{kind}={ident}'
    if not path.exists():
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        if '<html' not in response.text.lower():
            raise ValueError(f'Not HTML: {url}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
    return path, url


def listview(page, template, ident=None):
    for match in re.finditer(r'new Listview\(\{template:\s*[\'"]' + template + r'[\'"]', page):
        fragment = page[match.end():]
        # Only search this constructor; JSON is parsed, never evaluated as JS.
        end = fragment.find('});')
        fragment = fragment[:end] if end >= 0 else fragment
        if ident and not re.search(r"\bid:\s*['\"]" + ident + r"['\"]", fragment):
            continue
        data = re.search(r'\bdata:\s*', fragment)
        if data:
            return json.JSONDecoder().raw_decode(fragment[data.end():])[0]
    return []


def npc_page(pair):
    npc, name = pair
    version = 'forever' if npc > 200000 else 'classic'
    path, url = get_page('npc', npc, version)
    html = path.read_text(encoding='utf-8')
    kits = [k for k in listview(html, 'sound', 'sounds') if k['activity'] in ('Greeting', 'Farewell', 'Angry')]
    families = sorted({re.split(r'NPC(?:Greeting|Farewell|Pissed)', f['title'])[0]
                       for k in kits for f in k['files']})
    result = {'npc_id': npc, 'name': name, 'url': url + '#sounds',
              'snapshot_sha256': digest(path), 'families': families, 'kits': kits}
    save(EVIDENCE / f'npc-{npc}-sounds.json', result)
    print(name, families, [(k['activity'], k['id']) for k in kits], flush=True)
    return str(npc), result


def stage_corpus():
    paths = {
        'classic': ROOT / '.local-state/bulk/classic.json',
        'community': RESEARCH / 'forever-vo-upstream/tools/data/capture.json',
        'upstream-cache': RESEARCH / 'forever-vo-upstream/tools/data/bulk/questcache.json',
        'local-cache': RESEARCH / 'forever-local-quest-offers-2026-09-23.json',
        'wowhead-forever': ROOT / '.local-state/wowhead-tirisfal-additions-2026-09-23.json',
    }
    sources = {k: json.loads(p.read_text(encoding='utf-8')) for k, p in paths.items()}
    classic_ids = {r['questID'] for r in sources['classic']['quests'].values()}
    local_ids = {r['questID'] for r in sources['local-cache']['quests'].values()
                 if r.get('sortID') in (85, 154, 16611)}
    community_ids = {r['questID'] for r in sources['community']['quests'].values()
                     if r.get('zone') in ('Tirisfal Glades', 'Deathknell') or r.get('mapID') == 1420}
    chosen = local_ids | community_ids | set(QUEST_ORDER) | {r['questID'] for r in sources['wowhead-forever']['quests'].values()}
    records = {}
    # Keep all observed variants, including conflicts. Cache text is not enough
    # to infer progress/completion or the speaker of the offer.
    for label in ('classic', 'upstream-cache', 'community', 'local-cache', 'wowhead-forever'):
        for key, row in sources[label]['quests'].items():
            if row['questID'] not in chosen:
                continue
            records.setdefault(key, []).append({'source_dataset': label, **row,
                'text_sha256': hashlib.sha256(row['text'].encode()).hexdigest()})
    corpus = {'schema': 1, 'date': '2026-09-23', 'scope': 'Observed Tirisfal/Deathknell quest IDs; not a complete database',
              'sources': {k: {'path': str(p), 'sha256': digest(p)} for k, p in paths.items()},
              'quest_order': QUEST_ORDER, 'candidate_forever_ids': sorted(chosen - classic_ids),
              'quests': records, 'npcs': sources['wowhead-forever']['npcs'] | sources['classic']['npcs'] | sources['community']['npcs']}
    save(OUT / 'tirisfal-corpus.json', corpus)
    print('CORPUS', len(chosen), 'quests;', len(records), 'stages;', len(chosen-classic_ids), 'IDs absent Classic', flush=True)


def import_forever():
    """Connect only previously absent Forever IDs to the active local inputs.

    Existing different records are left untouched and reported as conflicts.
    Keep both raw source variants in the audition corpus for later review.
    """
    corpus = json.loads((OUT/'tirisfal-corpus.json').read_text(encoding='utf-8'))
    speaker_file = ROOT/'tools/voice_profiles/forever-tirisfal-quest-speakers.json'
    speakers = json.loads(speaker_file.read_text())['quests']
    novel = set(corpus['candidate_forever_ids'])
    imported = {'version': 2, 'quests': {}, 'gossip': {}, 'npcs': {}}
    cache_only = {'version': 2, 'quests': {}, 'gossip': {}, 'npcs': {}}
    pending = {}
    for key, rows in corpus['quests'].items():
        qid = str(rows[0]['questID'])
        if int(qid) not in novel:
            continue
        community = next((r for r in rows if r['source_dataset']=='community'), None)
        local = next((r for r in rows if r['source_dataset']=='local-cache'), None)
        current = dict(local or community or rows[-1])
        if community:
            current = {**community, **current}
        speaker = speakers.get(qid)
        if speaker:
            role = 'start' if current['event']=='accept' else 'end'
            expected = str(speaker[role])
            if current.get('npc') and str(current['npc']) != expected:
                raise ValueError(f'Speaker conflict in {key}')
            current.update(npc=expected, name=speaker[role+'_name'], speaker_source=speaker['source'])
        if not current.get('npc'):
            pending[key] = current
            continue
        # These are fresh, separate IDs. Never transplant same-title Classic speech.
        current['text_sha256'] = hashlib.sha256(current['text'].encode()).hexdigest()
        current['imported_from'] = str(OUT/'tirisfal-corpus.json')
        imported['quests'][key] = current
        npc = str(current['npc'])
        imported['npcs'][npc] = corpus['npcs'].get(npc, {'name':current['name']})
        if current['event']=='accept':
            cache_only['quests'][key] = current
            cache_only['npcs'][npc] = imported['npcs'][npc]
    audit = {'corpus_sha256': digest(OUT/'tirisfal-corpus.json'), 'speaker_evidence_sha256': digest(speaker_file),
             'stages': len(imported['quests']), 'quests': len({r['questID'] for r in imported['quests'].values()}),
             'collected_forever_ids': len(novel), 'pending': pending, 'audio_installed': False, 'writes': []}
    for path, additions in [(ROOT/'.local-state/capture.json', imported), (ROOT/'.local-state/bulk/questcache.json', cache_only)]:
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'version':2,'quests':{},'gossip':{},'npcs':{}}
        conflicts = []
        for kind in ('quests','npcs'):
            target = data.setdefault(kind,{})
            for key, row in additions[kind].items():
                if key in target and target[key] != row:
                    conflicts.append(f'{kind}:{key}')
                    continue
                target[key] = row
        before = digest(path) if path.exists() else None
        if path.exists():
            backup = EVIDENCE/(path.name+'.before-'+before[:12]+'.json')
            if not backup.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(path.read_bytes())
        save(path, data)
        audit['writes'].append({'path':str(path),'before_sha256':before,'after_sha256':digest(path),'preserved_conflicts':conflicts})
    save(OUT/'forever-import-audit.json',audit)
    print('IMPORTED',audit['quests'],'Forever quest IDs,',len(imported['quests']),'observed stages;',len(pending),'pending speaker verification. No installed audio changed.',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-wowhead', action='store_true', help='Optional HTTP refresh; use browser evidence if the site rejects HTTP clients.')
    parser.add_argument('--import-forever', action='store_true', help='Import verified, new Forever IDs into active local inputs, preserving any conflicts.')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    stage_corpus()
    if args.import_forever:
        import_forever()
    if args.fetch_wowhead:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = dict(pool.map(npc_page, NPCS.items()))
        save(OUT / 'npc-sound-map.json', results)


if __name__ == '__main__':
    main()
