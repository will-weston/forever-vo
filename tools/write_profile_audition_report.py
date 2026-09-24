"""Create the paired listening index from verified local render manifests."""
import json

from prepare_profile_auditions import ROOT, OUT


def main():
    registry = json.loads((ROOT/'tools/voice_profiles/tirisfal.json').read_text())
    refs = json.loads((OUT/'reference-manifest.json').read_text())['profiles']
    plan = json.loads((OUT/'performance-plan.json').read_text())
    manifest = json.loads((OUT/'manifest.json').read_text())
    rendered = {r['base']:r for r in manifest['files']}
    lines = [
        '# Tirisfal: native voice profiles and auditions',
        '',
        'September 23, 2026. IndexTTS 2.5. These are casting auditions; the installed game audio has not been replaced.',
        '',
        'The pilot covers Rude Awakening, The Mindless Ones, Tainted Scroll, The Damned, Rattling the Rattlecages, Scavenging Deathknell, and Piercing the Veil. It maps 21 stage/variant records across those seven quests, and renders their offers plus a Maximillion turn-in excerpt. Two additional auditions use Forever quest text: A Difficult Path and Patience.',
        '',
        '**Casting**',
        '',
        '| Native profile | NPCs verified on Wowhead | Reference |',
        '| --- | --- | --- |',
    ]
    for pid, ref in refs.items():
        names = ', '.join(f'[{n["name"]}]({n["source"]})' for n in registry['npcs'].values() if n['profile']==pid)
        lines.append(f'| {ref["native_name"]} | {names} | {ref["word_count"]} words / {ref["seconds"]:.2f} seconds |')
    lines += [
        '', '**Selection formula**', '',
        'NPC ID → verified greeting/farewell sound kits → one reusable identity reference. The recording suffix (such as Greeting03) identifies a line, not a distinct actor.', '',
        'Select complete phrases by total words and lexical variety, with a 14.8-second budget below the model’s 15-second truncation point. Target up to 30 words, but accept fewer rather than cutting or speeding up speech. Prefer at least three words per clip; order greetings before farewells; preserve each original recording and insert an 80 ms gap. The four selected references contain 22–27 words. Word diversity is a practical proxy, not a measured phoneme-coverage guarantee.', '',
        'Keep the Dark set’s “I am Forsaken” and “Victory for Sylvanas” anchors. Other families retain their own actors. Angry lines stay out of identity references; they can be separately auditioned for a specific performance later.', '',
        'Render a continuous utterance at normal speed. This comparison uses the speaker reference without a separate emotion reference. Editorial tone notes guide text selection and punctuation; they are not an unsupported natural-language style prompt sent to IndexTTS.', '',
        'Preserve float vocoder output, apply a single headroom gain if needed, write native-rate PCM24, and append 0.5 seconds of silence. No added reverb, EQ, pitch change, dynamic compression, or sentence stitching.', '',
        '**Listen: source on the left, generated quest speech on the right**', '',
        'Several first-pass long takes lost or mangled ending words. Their retakes below use coherent opening paragraphs, labeled as excerpts. Earlier failed takes remain archived under previous-takes and are not linked as candidates.', '',
        '| Quest / speaker | Assembled original reference | IndexTTS audition |',
        '| --- | --- | --- |',
    ]
    for row in plan['files']:
        base, pid = row['base'], row['voice']
        if base not in rendered:
            raise ValueError(f'Missing render: {base}')
        npc = registry['npcs'][row['npc']]
        kind = 'excerpt' if row.get('synthesis_text') else 'full offer'
        source = refs[pid]['reference']['path'].replace('\\','/')
        target = (OUT/(base+'.wav')).as_posix()
        lines.append(f'| **{row["title"]}** — {npc["name"]}<br>{kind}, {rendered[base]["seconds"]:.1f}s | ![{pid} source]({source}) | ![{row["title"]} audition]({target}) |')
    lines += [
        '', '**Forever data imported**', '',
        'Collected available evidence for 58 Tirisfal/Deathknell quest IDs, including 22 IDs absent from our Classic snapshot. Twenty-one of those Forever IDs, with 26 observed dialogue stages, are now in the active local input files. Whispering Horror Residue is preserved separately pending verification of its non-NPC starter. Missing stages remain missing; this is not a complete Forever database.', '',
        f'[Preserved source variants and hashes]({(OUT/"tirisfal-corpus.json").as_posix()}) · [Import audit]({(OUT/"forever-import-audit.json").as_posix()}) · [Verified additional quest speakers]({(ROOT/"tools/voice_profiles/forever-tirisfal-quest-speakers.json").as_posix()})', '',
        'The active loader was checked against every imported text and NPC ID. Same-title Classic recordings were not reassigned to new IDs. The native-profile mapping currently drives this audition plan; the installed pack still uses its previously generated audio.', '',
        'Aramis Hammerhand’s inspected Forever page exposes no sound list. His dialogue is preserved, but no native voice-set identity has been invented for him. New speakers need the same mapping verification before they enter this profile-based rendering workflow.', '',
        '**Next decision**', '',
        'Choose the best reference/voice family before generating full dialogue. Reuse it for NPCs sharing that native set, then vary performance through quest-specific intent and punctuation. Keep short auditions for casting; long final speeches require their own content checks and retakes. Reference hashes belong in generation cache keys so a revised voice cannot silently reuse old audio.', '',
        f'[Profile registry]({(ROOT/"tools/voice_profiles/tirisfal.json").as_posix()}) · [Reference provenance]({(OUT/"reference-manifest.json").as_posix()}) · [Performance plan]({(OUT/"performance-plan.json").as_posix()}) · [Audio checks]({(OUT/"audio-verification.json").as_posix()})', '',
        'Audio checks cover finite samples, peak headroom, the silent tail, and local speech-to-text comparisons. ASR is not a listening-quality score; proper names and small word ambiguities are retained in the diagnostic file for review.',
    ]
    target = ROOT/'docs/tirisfal-profile-auditions-2026-09-23.md'
    target.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
