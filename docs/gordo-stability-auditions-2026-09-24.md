# Gordo stability auditions — September 24, 2026

The user liked the original Gordo opening but reported that the ending went off the rails. After reviewing these auditions, the user selected B and requested installation. **B is now installed as 5481-accept**, with its 19.730-second playback duration.

The approved audio was copied without regeneration. The installed MP3 matches B's hash through the active game-addon junction. Lua 5.1 lookup/duration checks passed, all 482 other recordings were preserved, and Holland's progress/completion records are unchanged. [Installation record](C:/repos/forever-vo/.local-state/profile-packs/gordo-selected-20260924/installation.json) · [Backup](C:/repos/forever-vo/.local-state/backups/before-gordo-profiles-20260924-092603/rollback.json). Use `/reload` in game.

## Finding

The original 5481-accept take uses the native six-second, nine-word abomination reference and one continuous generation. Its transcript check recognized the final sentence, but did not assess whether the performance stayed in character.

Waveform inspection found substantially more hard-limited samples after approximately seven seconds: 0.115% in the first seven seconds versus 6.783% from 7–16.17 seconds. The local BigVGAN configuration has `use_tanh_at_final: false`; its forward method clamps its final convolution to [-1, 1]. Our existing hook captured the output after this clamp. Reducing that captured signal to a 0.75 peak cannot recover the already flattened peaks. This is a concrete clipping fault; it does not prove that clipping explains all perceived character or pacing drift.

## Controlled comparison

First render fresh seed-45 continuous and two-paragraph takes with the original pipeline. Then render the same inputs and seed while capturing `bigvgan.conv_post` before the clamp. Keep the same native reference, temperature 0.65, duration factor 1.0, complete source words, and one constant gain across each event. Add no effects, compression, pitch change, or time stretching.

The opt-in `--capture-before-clamp` renderer flag requires the hard-clamp vocoder configuration. The default renderer behavior and existing pack are unchanged. Separate fingerprints and per-file capture-mode records distinguish this audition from production takes.

| Audition | Speech structure | Raw peak before clamp | Constant gain | Old ceiling samples | New ceiling samples |
|---|---|---:|---:|---:|---:|
| A | Continuous | 2.0438 | 0.3670 | 11,649 | 1 |
| B | Original two paragraphs, same reference for each | 1.5204 | 0.4933 | 1,020 | 1 |

The new raw capture can reconstruct the corresponding old clipped take within 0.00000027 sample amplitude. Durations are identical. This confirms a controlled signal-capture change rather than an unrelated performance comparison. The single new ceiling sample is the natural maximum after constant gain, not a flattened plateau.

## Review limits

Both audition encodes and masters pass finite-sample, headroom, tail, duration, and hash checks. ASR still has pronunciation ambiguities. A has more wording differences, including the opening and an omitted "and"; B has want/ward, need/neat, and gloom/groom ambiguities. The user listened and approved B; this does not establish a perfect transcript. The original installed file was preserved during the comparison and backed up before the approved replacement.

- [B — two paragraphs](C:/repos/forever-vo/.local-state/profile-packs/gordo-preclamp-20260924/B-paragraphs.wav)
- [A — continuous comparison](C:/repos/forever-vo/.local-state/profile-packs/gordo-preclamp-20260924/A-continuous.wav)
- [Waveform verification](C:/repos/forever-vo/.local-state/profile-packs/gordo-preclamp-20260924/waveform-check.json)
- [Transcript checks](C:/repos/forever-vo/.local-state/profile-packs/gordo-preclamp-20260924/speech-check.json)
- [Original diagnostic](C:/repos/forever-vo/.local-state/profile-packs/gordo-retakes-20260924/original-diagnostic.json)
