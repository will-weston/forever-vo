# Quest voice audition recipe

**Current production recipe:** the user approved the September 23 [native-profile pilot](C:/repos/forever-vo/docs/tirisfal-profile-auditions-2026-09-23.md) and authorized applying it to the available Tirisfal, Mulgore, and Silverpine quest packs. Use the [Tirisfal registry](C:/repos/forever-vo/tools/voice_profiles/tirisfal-production.json), [Mulgore registry](C:/repos/forever-vo/tools/voice_profiles/mulgore-production.json), [Silverpine registry](C:/repos/forever-vo/tools/voice_profiles/silverpine-production.json), and the production section below. Older shared-race references, duration-first selection, and effects experiments are historical.

## Native-profile production — September 23, 2026

Installed Tirisfal: 75 quests / 183 recordings. See the [rollout and coverage record](C:/repos/forever-vo/docs/tirisfal-profile-rollout-2026-09-23.md). Installed Mulgore: 55 quests / 147 recordings, including its class chains and the available Forever welcome offer. See the [Mulgore rollout and listening notes](C:/repos/forever-vo/docs/mulgore-profile-rollout-2026-09-23.md).

Installed Silverpine on September 24: 57 new quests / 153 recordings, plus two already installed cross-zone handoffs for 59 quests covered. Includes nine new Forever quest IDs and their 17 available stages. See the [Silverpine rollout and listening notes](C:/repos/forever-vo/docs/silverpine-profile-rollout-2026-09-23.md). Combined installed total: 187 quests / 483 recordings; all prior Tirisfal and Mulgore audio was preserved.

1. Resolve NPC → display ID → NPCSounds → greeting/farewell sound kits. Keep each stock actor's family separate. Reuse the four approved pilot references byte for byte; keep both Dark-set anchors. Other native families follow the same selection method. Document fallback narration and NPCs with no native speech kit.
2. Prefer complete phrases with useful word coverage and vocabulary, ordered as greetings then farewells, with 80 ms joins and a 14.8-second limit. Do not pad sparse kits with grunts, combat cries, repeated words, or another actor. Short native references are an explicit exception, including Gordo and the necromancer set.
3. Render complete quest text, including available progress and completion. Pilot excerpts are casting demonstrations, not replacements for full quest events. Preserve already approved full-length takes when their text and reference match.
4. Use IndexTTS 2.5, BF16, seed 43, temperature 0.65, duration factor 1.0, without an emotion override. Keep short dialogue continuous; split long text into coherent groups of complete sentences. Generate no separate sentence-level acting beats. If a passage fails its content check, retake it and retain the reason and seed.
5. Capture the floating-point vocoder signal. Apply one constant headroom gain across the entire quest event, leaving a peak no higher than 0.75. Join complete passages with 120 ms additional silence and retain a 500 ms final tail. Store native-rate PCM24 masters. Add no EQ, compression, pitch shift, time stretch, or reverb. The reference already contains the original character sound.
6. Check every passage with ASR for omitted words, repetition, and damaged endings. Normalize numerical spelling and contractions for comparison. Inspect flagged differences; ASR spelling errors are not evidence that a generated word is wrong. These checks do not establish timbre, acting quality, or an in-game listening result.
7. Encode the checked masters to the addon's mono 44.1 kHz, 128 kbps MP3 format. Rebuild generated tables with measured durations and text keys, validate them with Lua 5.1, back up replaced files, install, and verify installed hashes. Preserve audio outside the selected pack.

Local execution: `tools/tirisfal_profile_prepare.py` builds the plan; run `tools/tirisfal_profile_render.py` from the isolated IndexTTS environment and checkout; `tools/tirisfal_profile_check.py --watch` checks new renders using CPU ASR. `tools/tirisfal_profile_install.py --install` requires all planned files and completed content checks, stages and validates the pack, then backs up and installs it. The plan, reference provenance, masters, transcripts, retake history, and installation record live under `.local-state/profile-packs/tirisfal-20260923/`.

For Mulgore, `tools/mulgore_profile_prepare.py` resolves its own cast and builds the zone plan. Set `FOREVER_VO_PROFILE_STAGE` to the absolute Mulgore stage directory in every shell used for rendering, checking, or installation: `C:/repos/forever-vo/.local-state/profile-packs/mulgore-20260923`. The shared render/check/install scripts retain their Tirisfal filenames and default stage; the explicit environment setting selects Mulgore. Consult the [Mulgore rollout record](C:/repos/forever-vo/docs/mulgore-profile-rollout-2026-09-23.md) for its scope and installation status.

For Silverpine, use `tools/silverpine_profile_prepare.py` and set `FOREVER_VO_PROFILE_STAGE` to `C:/repos/forever-vo/.local-state/profile-packs/silverpine-20260923` in every render/check/install shell. This plan protects already installed cross-zone handoffs, reuses matching native references, and preserves four wholly bracketed object descriptions for narration without changing the general text cleaner. Alaric's first-person dialogue has a documented undead-family fallback. See the [registry](C:/repos/forever-vo/tools/voice_profiles/silverpine-production.json) and [rollout record](C:/repos/forever-vo/docs/silverpine-profile-rollout-2026-09-23.md) for exact scope and status.

For doubtful proper-name transcripts, `tools/profile_lexicon_check.py --glossary <file>` provides a secondary ASR pass with vocabulary only. Never supply the expected sentences as the prompt or treat a high score as automatic approval. Inspect wording differences, retake unclear speech, and bind any justified ASR override to the exact WAV hash. Check quantities, negations, directions, and ending words separately from the overall match score.

September 24 Gordo diagnostic: the existing float hook is after BigVGAN's internal hard clamp. A 0.75 export peak therefore does not prove absence of earlier clipping. The opt-in `--capture-before-clamp` flag captures the final convolution before that clamp and applies the same constant headroom gain. The user approved and installed Gordo audition B, using the original two paragraphs and this capture mode, as 5481-accept. Preserve that exact approved take from `.local-state/profile-packs/gordo-selected-20260924` instead of restoring the older Tirisfal-stage recording. This is a specific approved Gordo replacement; the rest of the installed packs and the renderer's default remain unchanged. See the [Gordo comparison and remaining uncertainties](C:/repos/forever-vo/docs/gordo-stability-auditions-2026-09-24.md).

## Earlier accepted audition method: clean continuous IndexTTS retake

The user preferred the simpler Rattlecages retake after rejecting the heavily
directed audition for compression-like artifacts. Use
`tools/clean_index_quest_performance.py` and its per-file text analysis for the
first nine quests. These are WAV review outputs, not installed pack audio.

- Keep the approved speaker references intact. Read the whole quest event and
  distinguish intent toward the listener from dark subject matter.
- Generate one continuous waveform per event at duration factor 1.0. Do not
  independently generate and stitch sentence beats or use emotion vectors.
- Use a matching emotional audio reference only where justified, at 0.05–0.12
  influence. Stern instructions may use "I am not amused"; caring or mournful
  dialogue should not inherit that guidance automatically.
- Preserve source words; adjust punctuation sparingly. Capture floating-point
  vocoder output before integer conversion, apply one constant gain for headroom,
  append 0.5 seconds of silence, and export native-rate PCM24 WAV. This preserves
  any internal neural/vocoder artifacts; it does not guarantee artifact-free sound.
- Check transcripts for omissions/repetition and waveform/file integrity. These
  checks cannot establish acting quality. Listener approval is the quality gate.

The former multi-beat experiment in `tools/samples/directed-tirisfal` is rejected
for Rattlecages and must not be treated as an accepted recipe or installed.

## Human source for an undead processing experiment

The user rejected the dry `human-to-undead-audition/B-human-original.wav`
as not raspy. Its stock human warrior reference must not be described as an
approved raspy source. A voice-set label does not establish vocal texture.
Judge the dry voice before using effects to turn it into an undead character.

The user approved `raspy-human-dry-auditions/B-breathy-human.wav` as the base
voice and asked to add the undead effect. This is a synthetic Qwen3-TTS
VoiceDesign voice (seed 43), directed as breathy, worn, and raspy. Preserve
that exact take: SHA-256
`5aa1de27029c9f63d3cd0e930fd1c8729a21a8467e5ee0f80951c8609997553b`.

`breathy-b-undead-audition/` applies the existing human-to-undead treatment
to B, without regenerating its performance: mild EQ, a quiet detuned copy,
and the measured-decay dark-tail reconstruction. The comparison is matched
in loudness, with the full reverb tail retained. The effects audition needs
listener review; approval of the dry voice does not approve the processing.
This does not replace the IndexTTS production workflow or installed audio.

## Required undead male anchors

The approved undead male reference is `tools/voices/scourge-male.wav`: the
complete "I am Forsaken" (563151), followed by "Victory for Sylvanas" (563154).
Both lines must remain in alternatives to this Sarvis/Maximillion reference.
NPCs with a different sound set use their own recordings when requested; do not
insert Sarvis's clips into another character's reference.
Use this approved two-line reference by default. Do not add clips merely to reach
10 seconds: an approved voice takes priority over the generic duration recipe.
Changing its composition requires an audition before applying it to quests.
The Rattling the Rattlecages reference already contained both anchors, plus two
other lines; their absence was not the cause of that recording's reported issue.

## General recipe

1. Identify the NPC's actual greeting, farewell, and angry sound kits from its
   Wowhead Sounds tab. Keep one voice set; do not pool voices just by race/sex.
2. Measure complete clips. Keep lines 1.8–3.0 seconds long, preferring about
   2 seconds. Exclude combat sounds, very short responses, and clipped words.
3. Read the quest offer, progress, and completion separately. Judge the speaker's
   attitude toward the listener, not isolated words such as "dead" or "wounded".
   Helpful, explanatory, mournful, or dryly humorous text gets no angry material.
   For explicit irritation or threats, try one longer angry clip among the
   greeting/farewell clips and audition it against a neutral reference. This is
   an editorial starting point, not a measured sentiment-to-audio relationship.
4. Choose distinct eligible clips whose total duration plus 0.1-second gaps is
   closest to 10 seconds. Preserve whole lines; never cut speech to hit exactly
   10 seconds. Include greetings and farewells when available. Prefer clips close
   to 2 seconds to break ties. If too few fit, report the shortage rather than
   silently using another voice or duplicating clips.
5. Put representative delivery first. Original Chatterbox uses the first 6 seconds
   for speech prompting, the first 10 seconds for decoder conditioning, and the
   full reference for the speaker embedding. Appending anger at the very end may
   not steer delivery as intended. Mixing clips does not guarantee emotion control.
6. Begin with the approved B settings: CFG 0.3, exaggeration 0.3, seed 42.
   Use commas instead of double hyphens; preserve the quest's words. Generate
   sentence-aligned chunks, with 0.25-second gaps only where a split is needed.
   Audition before replacing an installed NPC voice.

## Novice Elreth: The Damned (376)

Source: https://www.wowhead.com/classic/npc=1661/novice-elreth#sounds

Her kits are Undead Female Standard: greetings 6046, farewells 6047, angry 6048.
The offer is practical and helpful. Progress expresses concern for the player's
safety. Completion combines gratitude and macabre humor. None calls for anger,
so 6048 is excluded. This is a manual reading of the actual quest text.

The selected four clips are 563123, 563124, 563117, and 563125, each 2.27–2.62
seconds. Together with three 0.1-second gaps they make about 10.00 seconds.
They say "I haven't got all day", "Dark Lady watch over you", "Embrace the shadow",
and "Do not seek death" (automatic transcripts; check the audio by ear).

Reproduce locally with `Run-Local.ps1 audition_elreth`. The script writes the
reference, all three quest-event auditions, and a provenance record under
`tools/samples/elreth/`. It does not change installed quest audio.

## IndexTTS zone generation

The accepted IndexTTS 2.5 audition supersedes the Chatterbox settings above for
the Tirisfal pack. Use `tools/index_quest_batch.py` from the isolated IndexTTS
environment. Current settings are BF16, seed 42, duration factor 1.0, without an
emotion override. Chatterbox CFG and exaggeration values do not transfer.

Keep the approved male reference containing both "I am Forsaken" and "Victory
for Sylvanas" intact, even though it is shorter than ten seconds. Keep Elreth's
four-line reference for female undead. These are shared voice families for this
zone trial, not independently matched voices for every NPC. Gordo uses his own
NPC sound set; human and dwarf prisoners use one matching race/gender set each.
Object dialogue uses the human narrator. Exact source IDs, durations, paths,
and exceptions are recorded in `.local-state/tirisfal-index-references.json`.

Preserve reference delivery without mixing angry clips in this first zone pass.
Normalize double hyphens to commas. Generate long speeches in sentence-aligned
chunks with 0.2-second joins and check their transcripts for omissions or loops.
Stage the complete batch, back up installed files, rebuild duration tables, and
verify hashes, text keys, audio durations, and Lua syntax before handing it over.

## Undertaker Mordo: auditions using his own sound set

The user requested Mordo's actual voice after noticing that the zone trial gave
him the same voice as Sarvis. Wowhead NPC 1568 lists greetings 6036, farewells
6037, and angry lines 6038 (NPCSounds 83). Sarvis uses NPCSounds 82 instead.

`tools/samples/mordo-index-auditions/` contains review-only recordings of the
complete Rude Awakening offer. The 10.2195-second reference uses whole clips
563181, 563175, 563178, 563177, and 563185, with 0.1-second gaps. Every selected
clip is 1.8–3.0 seconds and belongs to Mordo's greeting or farewell kit.

- A: natural delivery, no emotion override.
- B: light dry impatience, Mordo's own 563179 at emotion strength 0.08.
- C: a slightly sterner, weary take, Mordo's own 563184 at strength 0.12.

All three use the accepted continuous IndexTTS method, seed 42, natural duration,
constant gain for headroom, and a half-second tail in lossless PCM24 WAV.
The text warrants restrained impatience and dark humor; it does not call for
shouting or a threat. There are no pitch, time-stretch, compression, or reverb
effects. These auditions do not replace installed audio or the approved shared
Sarvis reference. The plan's `speaker_references` field supplies the explicit
NPC reference to `tools/clean_index_quest_performance.py`.
# Current profile pilot — September 23, 2026

For the latest user-approved direction, use [the native-profile casting recipe and paired auditions](C:/repos/forever-vo/docs/tirisfal-profile-auditions-2026-09-23.md) and [the registry](C:/repos/forever-vo/tools/voice_profiles/tirisfal.json). This supersedes the older duration-first, roughly ten-second reference selection below for this pilot.

Map each NPC to its actual greeting/farewell sound family, not just race and gender. Select complete phrases by word count and lexical diversity within 14.8 seconds (the installed IndexTTS 2.5 truncates at 15). Keep actors separate, retain the two established Dark-set anchors, and do not add angry clips to the identity reference. Preserve original effects; add no new undead DSP.

The four current references contain 22–27 words. Short, continuous paragraphs are the casting unit. Several long pilot takes developed damaged ending words; the verified retakes are explicitly labeled excerpts. Full production dialogue still needs content checks and its own retakes. Use reference hashes as part of future audio cache keys. These auditions have not replaced the installed pack.
