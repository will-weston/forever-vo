# Tirisfal native-profile rollout — September 23, 2026

Status: installed into the active ForeverVO_Data addon on September 23, 2026. Use `/reload` in game. The pack contains 62.1 minutes of audio across 183 files.

## Scope

75 quests, 182 quest stages, and 183 audio files, including a male/female text variant. This covers the available Tirisfal/Deathknell corpus and the previously selected warlock chain, including 22 Forever-specific quest IDs. It does not claim that unavailable Forever progress or completion text has been recovered.

The four approved pilot references are preserved byte for byte. Six additional stock families follow the same native-kit, complete-phrase selection method. NPCs sharing a Blizzard actor share that voice family; this is not a claim of a unique actor for every NPC.

## Formula

- Resolve NPC display IDs to NPCSounds and greeting/farewell kits. Prefer complete words and varied vocabulary within 14.8 seconds; no mixed actors or added angry/combat clips.
- IndexTTS 2.5, BF16, temperature 0.65, duration factor 1.0, seed 43 by default. Retakes record their own seed.
- Full dialogue in continuous sentence groups; preserve approved full pilot takes when they match. Casting excerpts are never installed as full dialogue.
- Capture the float waveform, apply one constant headroom gain, preserve native PCM24 masters, add 120 ms between passages and a 500 ms final tail. No added EQ, reverb, compression, pitch, or tempo processing.
- Install mono 44.1 kHz, 128 kbps MP3 files with measured durations in regenerated addon tables.

## Voice families

| Stock family | Reference words | Reference seconds | Files |
|---|---:|---:|---:|
| abomination | 9 | 6.00 | 1 |
| dwarf-male-standard | 27 | 8.65 | 2 |
| human-male-standard | 26 | 6.75 | 10 |
| necromancer | 16 | 6.85 | 7 |
| undead-female-magic | 25 | 14.45 | 1 |
| undead-female-standard | 24 | 14.27 | 27 |
| undead-female-warrior | 25 | 13.49 | 6 |
| undead-male-dark | 23 | 14.41 | 63 |
| undead-male-standard | 22 | 13.66 | 11 |
| undead-male-warrior | 27 | 14.49 | 55 |

Gordo and the necromancer use shorter native references because their coherent spoken kits are sparse. Non-speaking objects use narration. The human and dwarf prisoners have no native NPCSoundID/voice list in the inspected sources, so their matching stock race/sex sets are documented fallbacks.

## Verification and installation

All 183 recordings received passage-level transcript checks and file-integrity checks. Five recordings were retaken. Two remaining proper-name flags were resolved by a second ASR pass with a names-only glossary; expected sentences were not supplied. The exact transcripts, hashes, and reasons are retained in [lexicon-check.json](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/lexicon-check.json) and [retake-notes.json](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/retake-notes.json).

Staged and installed tables both compiled and executed with Lua 5.1. All 182 quest-stage durations and the gender variant flags were verified. All 183 installed MP3 hashes matched their staged masters' encodes. The 146 unrelated audio files and 54 unrelated quest records were preserved. The API-name scanner exited successfully and printed five existing informational names; this audio update changes no runtime addon Lua.

Installation replaced 142 recordings and added 41. [Backup and rollback inventory](C:/repos/forever-vo/.local-state/backups/before-tirisfal-profiles-20260923-205103/rollback.json) · [Installation record](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/installation.json).

Automated transcripts check content, not acting quality. I have not listened to every recording or tested playback in the running game; the in-game listening test remains the user’s check after `/reload`.

## Quest coverage

| ID | Quest | Available stages |
|---:|---|---|
| 8 | A Rogue's Deal | accept, progress, complete |
| 354 | Deaths in the Family | accept, progress, complete |
| 355 | Speak with Sevren | accept, complete |
| 356 | Rear Guard Patrol | accept, progress, complete |
| 358 | Graverobbers | accept, progress, complete |
| 359 | Forsaken Duties | accept, complete |
| 360 | Return to the Magistrate | accept, complete |
| 361 | A Letter Undelivered | accept, progress, complete |
| 362 | The Haunted Mills | accept, progress, complete |
| 363 | Rude Awakening | accept, complete |
| 364 | The Mindless Ones | accept, progress, complete |
| 365 | Fields of Grief | accept, progress, complete |
| 366 | Return the Book | accept, progress, complete |
| 367 | A New Plague | accept, progress, complete |
| 368 | A New Plague | accept, progress, complete |
| 369 | A New Plague | accept, progress, complete |
| 370 | At War With The Scarlet Crusade | accept, progress, complete |
| 371 | At War With The Scarlet Crusade | accept, progress, complete |
| 372 | At War With The Scarlet Crusade | accept, progress, complete |
| 374 | Proof of Demise | accept, progress, complete |
| 375 | The Chill of Death | accept, progress, complete |
| 376 | The Damned | accept, progress, complete |
| 380 | Night Web's Hollow | accept, progress, complete |
| 381 | The Scarlet Crusade | accept, progress, complete |
| 382 | The Red Messenger | accept, progress, complete |
| 383 | Vital Intelligence | accept, progress, complete |
| 398 | Wanted: Maggot Eye | accept, progress, complete |
| 404 | A Putrid Task | accept, progress, complete |
| 405 | The Prodigal Lich | accept, progress, complete |
| 407 | Fields of Grief | accept, progress, complete |
| 408 | The Family Crypt | accept, progress, complete |
| 409 | Proving Allegiance | accept, progress, complete |
| 410 | The Dormant Shade | progress, complete |
| 411 | The Prodigal Lich Returns | accept, progress, complete |
| 426 | The Mills Overrun | accept, progress, complete |
| 427 | At War With The Scarlet Crusade | accept, progress, complete |
| 431 | Candles of Beckoning | complete |
| 445 | Delivery to Silverpine Forest | accept, progress, complete |
| 492 | A New Plague | accept, progress, complete |
| 590 | A Rogue's Deal | accept, complete |
| 1470 | Piercing the Veil | accept, progress, complete |
| 1471 | The Binding | accept, progress, complete |
| 1473 | Creature of the Void | accept, progress, complete |
| 1478 | Halgar's Summons | accept, complete |
| 3099 | Tainted Scroll | accept, progress, complete |
| 3901 | Rattling the Rattlecages | accept, progress, complete |
| 3902 | Scavenging Deathknell | accept, progress, complete |
| 5481 | Gordo's Task | accept, progress, complete |
| 5482 | Doom Weed | accept, progress, complete |
| 5847 | Welcome! | accept, progress, complete |
| 5901 | A Plague Upon Thee | accept, progress, complete |
| 5902 | A Plague Upon Thee | accept, complete |
| 6395 | Marla's Last Wish | accept, progress, complete |
| 86784 | Sticks and Bones | accept |
| 90902 | Rediscovering the Light | accept |
| 91858 | Diplomatic Incident | accept, complete |
| 92422 | The Wrath of Rath'mael | accept, complete |
| 95314 | That Shadowvale Green Elixir | accept |
| 95328 | Whispering Horror Residue | accept |
| 96895 | The Argent Emissary | accept, complete |
| 96896 | A Righteous Cause | accept |
| 96897 | The Cult of the Damned | accept |
| 96898 | Remnants of War | accept |
| 96899 | Bandarion Keep | accept |
| 97558 | Hides for the Forsaken | accept, progress, complete |
| 98389 | A Light in the Darkness | accept |
| 98545 | Leonid's Letter | accept |
| 98601 | A Difficult Path | accept, progress, complete |
| 99134 | Discipline | accept, complete |
| 99141 | Patience | accept, progress, complete |
| 99142 | Tomb Weed | accept, progress |
| 99144 | Seeking Refuge | accept |
| 99152 | As Above, So Below | accept |
| 99153 | The One That Got Away | accept |
| 99156 | Rear Guard Patrol | accept |

## Forever text still unavailable

These are absent from the available source corpus. An absent progress entry does not prove that the quest has separate progress speech. No text was invented to fill these slots.

| Quest | Unavailable stages |
|---|---|
| 86784: Sticks and Bones | complete, progress |
| 90902: Rediscovering the Light | complete, progress |
| 91858: Diplomatic Incident | progress |
| 92422: The Wrath of Rath'mael | progress |
| 95314: That Shadowvale Green Elixir | complete, progress |
| 95328: Whispering Horror Residue | complete, progress |
| 96895: The Argent Emissary | progress |
| 96896: A Righteous Cause | complete, progress |
| 96897: The Cult of the Damned | complete, progress |
| 96898: Remnants of War | complete, progress |
| 96899: Bandarion Keep | complete, progress |
| 98389: A Light in the Darkness | complete, progress |
| 98545: Leonid's Letter | complete, progress |
| 99134: Discipline | progress |
| 99142: Tomb Weed | complete |
| 99144: Seeking Refuge | complete, progress |
| 99152: As Above, So Below | complete, progress |
| 99153: The One That Got Away | complete, progress |
| 99156: Rear Guard Patrol | complete, progress |

## Local records

- [Production casting registry](C:/repos/forever-vo/tools/voice_profiles/tirisfal-production.json)
- [Plan and full spoken text](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/plan.json)
- [Reference provenance](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/new-reference-provenance.json)
- [Render manifest](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/manifest.json)
- [Speech checks](C:/repos/forever-vo/.local-state/profile-packs/tirisfal-20260923/speech-check.json)
- [Production recipe](C:/repos/forever-vo/docs/voice-audition-recipe.md)
