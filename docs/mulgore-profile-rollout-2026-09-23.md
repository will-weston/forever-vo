# Mulgore native-profile rollout — September 23, 2026

Status: installed into the active ForeverVO_Data addon on September 23, 2026. Use `/reload` in game. The pack contains 46.7 minutes of audio across 147 files.

## Scope

55 quests and 147 recordings: the existing 54-quest Mulgore/Camp Narache pack, including its class and delivery chains, plus the available offer for Forever quest 95350, Welcome to Azeroth. Full available offer, progress, and completion text is retained. The new quest has no captured progress/completion in the inspected source.

## Formula

The same word-weighted native voice formula as the approved Tirisfal pack: NPC → display → NPCSounds → greeting/farewell audio. Select whole phrases for word coverage and varied vocabulary under 14.8 seconds, with 80 ms joins. Keep actors separate. Some sparse families have shorter references; the limit is a ceiling, not a requirement to pad the sample.

IndexTTS 2.5, BF16, temperature 0.65, seed 43 initially, duration factor 1.0. Long text is split into coherent groups of complete sentences, with all words retained. Float vocoder capture, one constant headroom gain across each event, native PCM24 masters, 120 ms passage joins and a 500 ms final tail. No added reverb, EQ, dynamic compression, pitch changes, or time stretching. Encoded for the addon as mono 44.1 kHz, 128 kbps MP3.

## Cast

The IDs below identify native NPC sound families. NPCs sharing a stock actor keep that actor; this does not create a unique actor for every NPC.

| Family | Representative speakers | Reference words | Seconds | Files |
|---|---|---:|---:|---:|
| narrator | Minor Manifestation of Earth, Sealed Supply Crate, Demon Scarred Cloak | 26 | 6.75 | 6 |
| npc-sound-132 | Innkeeper Kauth | 32 | 14.40 | 2 |
| npc-sound-171 | Cairne Bloodhoof | 33 | 13.56 | 4 |
| npc-sound-3773 | Alaana Stormwalker | 27 | 14.79 | 1 |
| npc-sound-54 | Dendrite Starblaze | 25 | 10.97 | 5 |
| npc-sound-60 | Thork | 20 | 10.82 | 1 |
| npc-sound-67 | Turak Runetotem, Baine Bloodhoof, Chief Hawkwind, Zarlman Two-Moons | 30 | 14.49 | 34 |
| npc-sound-68 | Gart Mistrunner, Holt Thunderhorn, Mull Thunderhorn, Seer Graytongue | 27 | 13.67 | 31 |
| npc-sound-69 | Grull Hawkwind, Harutt Thunderhorn, Lanka Farshot, Yaw Sharpmane | 16 | 5.28 | 47 |
| npc-sound-70 | Seer Ravenfeather, Brave Windfeather, Greatmother Hawkwind | 34 | 12.83 | 11 |
| npc-sound-71 | Meela Dawnstrider, Gennia Runetotem, Kary Thunderhorn | 35 | 13.81 | 4 |
| npc-sound-72 | Antur Fallow | 15 | 6.19 | 1 |

Cairne uses his own native speech (NPCSounds 171). The Ancestral Spirit has no native greeting kit in its cached display; its prior matching Tauren stock casting is retained and documented. Minor Manifestation of Earth has no native spoken greeting kit and retains narration. Items and objects also use the existing neutral narrator.

Alaana Stormwalker’s [Wowhead page](https://www.wowhead.com/forever/npc=259119/alaana-stormwalker) supplies display ID 143208 in its public model metadata. The cached client tables map that display to NPCSounds 3773 and greeting/farewell kits 353056/353058. Although her page does not show a Sounds tab, those native clips were available from the client archive. The quest text came from the pinned community capture snapshot, repaired with the existing ingestion routine, and matches the visible [quest description](https://www.wowhead.com/forever/quest=95350/welcome-to-azeroth). The page confirms Alaana as the starter and Thrall as the finisher; its missing progress/completion speech has not been invented.

## Verification and installation

All 147 recordings received passage-level transcript checks and waveform/file-integrity checks. The final critical-word audit found no ASR differences involving negation, directions, or quantities. All masters are finite mono PCM24 with the intended headroom and final silence; the installed encodes are mono 44.1 kHz MP3 and match their recorded hashes.

Fourteen recordings were retaken; five received a third take. The selected takes corrected dropped words, pronouns, and a damaged passage ending. Five remaining primary-ASR flags were reviewed against a vocabulary-only secondary pass and recorded as hash-bound transcription exceptions. Expected sentences were never supplied as ASR prompts. A separate Whisper base.en pass helped inspect ambiguous consonants without a vocabulary prompt.

Some pronunciation ambiguity remains across takes, including crates/grates, prying/frying, pitcher/picture, and several native names or consonant endings. These are documented in [listening-notes.json](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/listening-notes.json), not represented as proven correct pronunciations. The selected recordings are ready for in-game listening. ASR and waveform checks do not establish acting quality, and no full listening pass or running-game playback test was performed.

Staged and installed tables both compiled and executed under Lua 5.1. All 147 quest-stage lookups and measured durations were verified, with all 75 unrelated quest records preserved. The API-name scanner exited successfully and printed five existing informational names. This audio update changes no runtime addon Lua.

Installation replaced 146 Mulgore recordings and added the captured Welcome to Azeroth offer. All 183 approved Tirisfal MP3 hashes were independently verified unchanged afterward. The combined installed pack now contains 130 quests and 330 audio files.

[Backup and rollback inventory](C:/repos/forever-vo/.local-state/backups/before-mulgore-profiles-20260923-222638/rollback.json) · [Installation record](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/installation.json).

## Quest coverage

| ID | Quest | Stages |
|---:|---|---|
| 743 | Dangers of the Windfury | accept, progress, complete |
| 745 | Sharing the Land | accept, progress, complete |
| 746 | Dwarven Digging | accept, progress, complete |
| 747 | The Hunt Begins | accept, progress, complete |
| 748 | Poison Water | accept, progress, complete |
| 749 | The Ravaged Caravan | accept, complete |
| 750 | The Hunt Continues | accept, progress, complete |
| 751 | The Ravaged Caravan | accept, progress, complete |
| 752 | A Humble Task | accept, complete |
| 753 | A Humble Task | accept, progress, complete |
| 754 | Winterhoof Cleansing | accept, progress, complete |
| 755 | Rites of the Earthmother | accept, complete |
| 756 | Thunderhorn Totem | accept, progress, complete |
| 757 | Rite of Strength | accept, progress, complete |
| 758 | Thunderhorn Cleansing | accept, progress, complete |
| 759 | Wildmane Totem | accept, progress, complete |
| 760 | Wildmane Cleansing | accept, progress, complete |
| 761 | Swoop Hunting | accept, progress, complete |
| 763 | Rites of the Earthmother | accept, progress, complete |
| 764 | The Venture Co. | accept, progress, complete |
| 765 | Supervisor Fizsprocket | accept, progress, complete |
| 766 | Mazzranache | accept, progress, complete |
| 767 | Rite of Vision | accept, complete |
| 770 | The Demon Scarred Cloak | accept, complete |
| 771 | Rite of Vision | accept, progress, complete |
| 772 | Rite of Vision | accept, complete |
| 773 | Rite of Wisdom | accept, complete |
| 775 | Journey into Thunder Bluff | accept, complete |
| 776 | Rites of the Earthmother | accept, progress, complete |
| 780 | The Battleboars | accept, progress, complete |
| 781 | Attack on Camp Narache | accept, progress, complete |
| 833 | A Sacred Burial | accept, progress, complete |
| 854 | Journey to the Crossroads | accept, complete |
| 861 | The Hunter's Way | accept, progress, complete |
| 1519 | Call of Earth | accept, progress, complete |
| 1520 | Call of Earth | accept, complete |
| 1521 | Call of Earth | accept, progress, complete |
| 1656 | A Task Unfinished | accept, progress, complete |
| 3091 | Simple Note | accept, progress, complete |
| 3092 | Etched Note | accept, progress, complete |
| 3093 | Rune-Inscribed Note | accept, progress, complete |
| 3094 | Verdant Note | accept, progress, complete |
| 3376 | Break Sharptusk! | accept, progress, complete |
| 5922 | Moonglade | accept, complete |
| 5928 | Heeding the Call | accept, complete |
| 5930 | Great Bear Spirit | accept, progress, complete |
| 5932 | Back to Thunder Bluff | accept, complete |
| 6002 | Body and Heart | accept, progress, complete |
| 6061 | Taming the Beast | accept, progress, complete |
| 6065 | The Hunter's Path | accept, complete |
| 6066 | The Hunter's Path | accept, complete |
| 6087 | Taming the Beast | accept, progress, complete |
| 6088 | Taming the Beast | accept, progress, complete |
| 6089 | Training the Beast | accept, complete |
| 95350 | Welcome to Azeroth | accept |

## Local records

- [Casting registry](C:/repos/forever-vo/tools/voice_profiles/mulgore-production.json)
- [Full text and generation plan](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/plan.json)
- [Original clips and reference provenance](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/reference-provenance.json)
- [Render manifest](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/manifest.json)
- [Speech checks](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/speech-check.json)
- [Retake decisions](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/retake-notes.json)
- [Remaining listening notes](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/listening-notes.json)
- [Hash-bound ASR reviews](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/qa-overrides.json)
- [Critical-word audit](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/critical-word-audit.json)
- [Waveform and encoding checks](C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923/file-integrity.json)
