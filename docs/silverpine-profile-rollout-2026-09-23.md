# Silverpine native-profile rollout — September 23, 2026

Status: installed into the active ForeverVO_Data addon on September 24, 2026. Use `/reload` in game. This addition contains 47.0 minutes of audio across 153 files.

## Scope

59 quests covered: 57 newly voiced quests with 153 recordings, plus the already installed Delivery to Silverpine Forest (445) and Diplomatic Incident (91858). Includes the available Silverpine quests, three Shadowfang Keep quests, and delivery/class chains captured in the zone. Nine new Forever-specific quest IDs contribute 17 available stages; Diplomatic Incident is already in Tirisfal. Missing Forever stages are not invented.

Source priority for this addition is repaired community capture over the pinned Forever quest-cache offers over the Classic database. The community snapshot is [ForeverVO commit 600a37d](https://github.com/quinn-dougherty/forever-vo/blob/600a37d4e08b1b3a8d27fbfa00c8c685f4d014f7/tools/data/capture.json). Existing Tirisfal and Mulgore quest records and audio are protected. The current local cache snapshot adds no further Silverpine-sort offers.

## Formula

Use the same approved native sound-family method: NPC → display → NPCSounds → original greeting/farewell clips. Reuse existing matching references byte for byte. New families select complete phrases by word coverage and varied vocabulary under 14.8 seconds, with 80 ms joins. Keep actors separate.

IndexTTS 2.5, BF16, initial seed 43, temperature 0.65, duration factor 1.0, no emotion override. Preserve complete available dialogue in coherent sentence groups. Capture float output and apply one constant headroom gain across each event. Retain native PCM24 masters, 120 ms extra passage gaps, and a 500 ms final tail. No added EQ, reverb, dynamic compression, pitch, or tempo effects. Encode mono 44.1 kHz, 128 kbps MP3 for the addon.

## Cast

| Native family | Speakers | Reference words | Seconds | Recordings |
|---|---|---:|---:|---:|
| narrator | Corpse Laden Boat, Dalaran Crate, Deathstalker Vincent, Dusty Shelf, Shallow Grave, Unknown, Yuriv's Tombstone | 26 | 6.75 | 11 |
| npc-sound-142 | Tabitha Heartweaver | 28 | 14.67 | 2 |
| npc-sound-145 | Gordon Wendham | 27 | 14.20 | 3 |
| npc-sound-3773 | Lumina Windsinger | 27 | 14.79 | 9 |
| npc-sound-68 | Tonga Runetotem | 27 | 13.67 | 1 |
| npc-sound-71 | Mura Runetotem | 35 | 13.81 | 2 |
| npc-sound-79 | Apothecary Zinge | 25 | 14.45 | 2 |
| undead-female-standard | Clarice Foster | 24 | 14.27 | 1 |
| undead-female-warrior | Deathstalker Faerleia, Rane Yorick | 25 | 13.49 | 10 |
| undead-male-dark | Apothecary Lydon, Apothecary Renferrel, Bethor Iceshard, Dalar Dawnweaver, Keeper Bel'dugur, Magistrate Sevren | 23 | 14.41 | 50 |
| undead-male-standard | Alaric, Karos Razok, Master Apothecary Faranell, Trevan Rol | 22 | 13.66 | 14 |
| undead-male-warrior | Deathguard Baldren, Deathguard Podrig, Deathstalker Erland, High Executor Hadrec, Michael Garrett, Quinn Yorick, Raleigh Andrean, Shadow Priest Allister | 27 | 14.49 | 48 |

Alaric has no ordinary NPC greeting set: he speaks through a talking-head item, a grave, and a shelf. His five first-person stages use the existing undead male standard voice as an explicit editorial fallback. His grave-description progress line remains narration. Vincent's completion describes his dead body and is also narrated.

Four wholly bracketed object descriptions (477-complete, 478-accept, 91860-complete, 91861-accept) would be erased by ordinary stage-direction cleanup. Their actual descriptive words are retained for the narrator; the source text is preserved separately. No runtime Lua or general text-cleaning behavior is changed.

The public model metadata for [Deathguard Baldren](https://www.wowhead.com/forever/npc=259611/deathguard-baldren) supplies display 141689 → NPCSounds 84. [Lumina 248755](https://www.wowhead.com/forever/npc=248755/lumina-windsinger) and [Lumina 259620](https://www.wowhead.com/forever/npc=259620/lumina-windsinger) both use display 131648 → NPCSounds 3773. [Tabitha Heartweaver](https://www.wowhead.com/forever/npc=250686/tabitha-heartweaver) uses display 136424 → NPCSounds 142. Voice-kit mappings come from the cached client tables; public page metadata was inspected on September 23.

## Verification and installation

All 153 recordings received passage-level transcript and waveform/file-integrity checks. The final critical-word audit found no ASR differences involving quantities, negations, or directions. All masters are finite mono PCM24 with the intended headroom and final silence. MP3s are mono 44.1 kHz, and installed file hashes match the manifest. The checks can be reproduced with the stage's `audit.py`.

Eleven recordings were retaken, with 17 additional takes in total. Selected takes restore missing words such as the second Thule and adventurer, clarify Beren's Peril, and recover the recipient Bethor Iceshard. Five remaining primary-ASR flags were reviewed against vocabulary-only secondary transcripts and recorded as hash-bound exceptions. Expected sentences were never provided as ASR prompts.

Three small speech-input punctuation adjustments preserve every source word and the original game-text lookup keys: remove visual asterisks around *high* in 91859-accept; remove quotation marks around worgen in 95034-accept; add a clause comma in 444-accept. The first two eliminate the corresponding missing-word/extra-syllable transcript problems. The comma does not resolve the weak-word issue below. These are local plan preparation rules, not runtime text-cleaner changes.

Residual issues are documented in [listening-notes.json](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/listening-notes.json). ASR still omits the weak "it" in 444-accept across takes. Skulkers/sculters, hardened/heart and, holing/holding, and several proper names remain pronunciation or transcription ambiguities. These were not represented as fixed or certified exact speech. Transcript checks diagnose content, not acting quality; no full auditory pass or running-game playback test was performed.

Staged and installed tables compiled and executed under Lua 5.1. All 153 quest-stage lookups and measured durations were verified, with all 130 unrelated quest records preserved. The API-name scanner exited successfully and printed five existing informational names. This rollout changes no runtime addon Lua.

Installation added 153 files and replaced none. All 330 existing Tirisfal/Mulgore recordings were independently checked against the pre-rollout hashes and remain byte-for-byte unchanged. The combined installed pack contains 187 quests and 483 sound files.

[Backup and rollback inventory](C:/repos/forever-vo/.local-state/backups/before-silverpine-profiles-20260924-001341/rollback.json) · [Installation record](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/installation.json).

## Quest coverage

| ID | Quest | Available stages | Status |
|---:|---|---|---|
| 99 | Arugal's Folly | accept, progress, complete | Installed |
| 264 | Until Death Do Us Part | accept, progress, complete | Installed |
| 421 | Prove Your Worth | accept, progress, complete | Installed |
| 422 | Arugal's Folly | accept, progress, complete | Installed |
| 423 | Arugal's Folly | accept, progress, complete | Installed |
| 424 | Arugal's Folly | accept, progress, complete | Installed |
| 425 | Ivar the Foul | accept, progress, complete | Installed |
| 428 | Lost Deathstalkers | accept, complete | Installed |
| 429 | Wild Hearts | accept, progress, complete | Installed |
| 430 | Return to Quinn | accept, progress, complete | Installed |
| 435 | Escorting Erland | accept, progress, complete | Installed |
| 437 | The Dead Fields | accept, progress, complete | Installed |
| 438 | The Decrepit Ferry | accept, complete | Installed |
| 439 | Rot Hide Clues | accept, progress, complete | Installed |
| 440 | The Engraved Ring | accept, progress, complete | Installed |
| 441 | Raleigh and the Undercity | accept, progress, complete | Installed |
| 442 | Assault on Fenris Isle | accept, progress, complete | Installed |
| 443 | Rot Hide Ichor | accept, progress, complete | Installed |
| 444 | Rot Hide Origins | accept, progress, complete | Installed |
| 445 | Delivery to Silverpine Forest | accept, progress, complete | Already installed |
| 446 | Thule Ravenclaw | accept, progress, complete | Installed |
| 447 | A Recipe For Death | accept, progress, complete | Installed |
| 448 | Report to Hadrec | accept, complete | Installed |
| 449 | The Deathstalkers' Report | accept, progress, complete | Installed |
| 450 | A Recipe For Death | accept, progress, complete | Installed |
| 451 | A Recipe For Death | accept, progress, complete | Installed |
| 452 | Pyrewood Ambush | accept, complete | Installed |
| 460 | Resting in Pieces | accept, progress, complete | Installed |
| 461 | The Hidden Niche | accept, progress, complete | Installed |
| 477 | Border Crossings | accept, complete | Installed |
| 478 | Maps and Runes | accept, progress, complete | Installed |
| 479 | Ambermill Investigations | accept, progress, complete | Installed |
| 480 | The Weaver | accept, progress, complete | Installed |
| 481 | Dalar's Analysis | accept, progress, complete | Installed |
| 482 | Dalaran's Intentions | accept, complete | Installed |
| 491 | Wand to Bethor | accept, progress, complete | Installed |
| 493 | Journey to Hillsbrad Foothills | accept, progress, complete | Installed |
| 516 | Beren's Peril | accept, progress, complete | Installed |
| 530 | A Husband's Revenge | accept, progress, complete | Installed |
| 1013 | The Book of Ur | accept, progress, complete | Installed |
| 1014 | Arugal Must Die | accept, progress, complete | Installed |
| 1098 | Deathstalkers in Shadowfang | accept, complete | Installed |
| 1359 | Zinge's Delivery | accept, progress, complete | Installed |
| 3221 | Speak with Renferrel | accept, complete | Installed |
| 3301 | Mura Runetotem | accept, progress, complete | Installed |
| 6321 | Supplying the Sepulcher | accept, progress, complete | Installed |
| 6322 | Michael Garrett | accept, progress, complete | Installed |
| 6323 | Ride to the Undercity | accept, progress, complete | Installed |
| 6324 | Return to Podrig | accept, progress, complete | Installed |
| 91858 | Diplomatic Incident | accept, complete | Already installed |
| 91859 | A Curious Pair | accept, complete | Installed |
| 91860 | A Grim Fate | accept, complete | Installed |
| 91861 | Into Fenris Keep | accept, complete | Installed |
| 91862 | Lumina Windsinger | accept, progress, complete | Installed |
| 92401 | A Frightened Request | accept, complete | Installed |
| 95034 | The Debt | accept, complete | Installed |
| 95036 | A Moon-Kissed Blade | accept | Installed |
| 95981 | Watching the Roads | accept | Installed |
| 96204 | The Windshaper's Wrath | accept, complete | Installed |

## Local records

- [Generation plan](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/plan.json)
- [Casting and evidence](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/casting.json)
- [New native reference provenance](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/reference-provenance.json)
- [Render manifest](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/manifest.json)
- [Speech checks](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/speech-check.json)
- [Prior audio hashes](C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923/before-audio-hashes.json)
