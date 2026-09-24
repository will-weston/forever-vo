# Mordo processing: measurements from original audio

Date: 2026-09-22. Source: [Undertaker Mordo's Wowhead sound set](https://www.wowhead.com/classic/npc=1568/undertaker-mordo#sounds).

## Result

The strongest supported reconstruction target is a **dark, low-frequency reverberant/resonant tail with an apparent decay time around 0.8–0.9 seconds**. This is an estimate of the tail's level envelope, not a recovered plugin preset or impulse response.

The original recordings have a clear low-frequency continuation after the brighter speech has faded. The same descriptive measurement is much shorter in the ten cached human NPC clips and substantial in the two approved Sarvis anchors. This supports a shared undead-style tail in the recordings examined. It does not establish that every undead voice has an identical effect or that all differences between actors come from processing.

## Material and provenance

- 16 Mordo greeting, farewell and angry OGGs, previously downloaded from the exact Wowhead sound URLs and verified byte/sample identical to the cached source files. See [source verification](../tools/samples/mordo-delay-analysis/source-check.json).
- 10 cached human NPC OGGs under `tools/voices/raw/human-male` for a descriptive comparison. Different actors and phrases; not a paired studio control.
- The two approved Sarvis voice anchors, file IDs 563151 and 563154. This is a small corroborating sample, not a survey of all undead voices.
- Full paths, excluded measurements and individual fits are recorded in [decay-fit.json](../tools/samples/mordo-forensic-analysis/decay-fit.json).

## 1. The apparent half-second continuation

For each recording, measure energy in a lower band (100–700 Hz) and an upper band (1800–5500 Hz), using third-order Butterworth filters and 7.5 ms Gaussian smoothing. Normalize each band to its own peak. Find the last upper-band crossing of -25 dB and the last lower-band crossing of -40 dB. Their difference describes how much longer the low sound remains.

| Recording group | Number | Median continuation | Interquartile range |
| --- | ---: | ---: | ---: |
| Mordo | 16 | 417 ms | 379–560 ms |
| Human NPCs | 10 | 22 ms | 1–56 ms |
| Sarvis anchors | 2 | 347 ms | 332–362 ms |

Changing the upper-band threshold to -20 or -30 dB moves Mordo's median to 501 or 394 ms, respectively. The human medians become 66 or 14 ms. The group difference therefore survives these threshold changes.

This is **not an echo-onset estimate**. The thresholds are deliberately different between bands; phonetics, pitch and noise can influence the metric. The values describe spectral persistence, not an unbiased estimate of time since the actor physically stopped speaking.

## 2. Fitting the decay mathematically

In inspected ending regions that avoid obvious speech and the sharp final edit, fit a straight line to band energy in decibels:

`L_b(t) = a_b + m_b t`

For a negative slope, the equivalent 60 dB decay is:

`T60_b = -60 / m_b`

The corresponding amplitude envelope is proportional to:

`10^(-3 t / T60_b)`

This estimates decay speed. It does not solve the unknown dry voice, absolute wet level, or phase of the effect.

Thirteen clips had candidate fitting windows; three were excluded because their ending speech/noise made clean tail selection unreliable. A band fit was retained only with at least 150 ms of usable data, at least a 12 dB fitted drop, and R-squared of at least 0.85. All attempted fits and manual time bounds are retained. Not every candidate window qualified in every band.

| Frequency band | Accepted clips | Median apparent T60 | Interquartile range |
| --- | ---: | ---: | ---: |
| 100–250 Hz | 3 | 0.91 s | 0.78–0.92 s |
| 250–500 Hz | 5 | 0.82 s | 0.80–1.00 s |
| 500–1000 Hz | 6 | 0.76 s | 0.68–0.90 s |
| 1000–2000 Hz | 5 | 0.89 s | 0.79–1.06 s |

Moving each fit window by +/-30 ms gives pooled medians of approximately 0.86, 0.82, 0.76 and 0.89 seconds. These are sensitivity checks, not independent observations or confidence intervals.

The late spectra are strongly weighted toward low frequencies. The fits do **not** show a reliably shorter T60 at every higher frequency; low treble level and different decay rate are separate properties. Do not turn the spectral balance into an exact low-pass cutoff without additional evidence.

Speech-based decay estimation remains sensitive to trailing vowels, codec noise and editing. These values are not standardized impulse-response RT60 measurements. [Subband estimation from free-decaying speech regions](https://pubmed.ncbi.nlm.nih.gov/22501059/) and [the decay-slope/T60 convention](https://www.mathworks.com/help/audio/ref/rt60.html) provide the methodological context.

## 3. Searching for literal and shifted echoes

The earlier real-cepstrum scan found no consistent 400–500 ms fixed-copy echo. A new exploratory scan covered spectral periodicity from 1–700 ms. Short-lag structure is present but cannot be separated confidently from the speaker's pitch and spectral envelope, so it does not justify claiming a specific short delay.

A separate diagnostic compared changing harmonic patterns across time lags of roughly 80–700 ms and pitch offsets of -6 to +6 semitones. It used log-frequency magnitude features, broad spectral-envelope removal, temporal differencing and a median across clips.

Positive control: add a duration-preserving copy shifted -2 semitones, delayed 450 ms, at 0.25 amplitude. Its combined correlation peak was 0.196 near 459 ms/-2 semitones. The original recordings' strongest 400–500 ms point was only 0.021, near 449 ms/-4 semitones. Splitting the originals into odd/even subsets moved the preferred pitch to -6 versus +5.75 semitones. Both control subsets retained the expected -2 semitone peak near 449–459 ms.

This gives no stable support for a distinct strongly shifted half-second repeat at this detector's resolution. It cannot exclude a quiet/filtered repeat, variable effects, or microdetuning smaller than its quarter-semitone grid. It is a diagnostic with one injected control strength, not a calibrated detection-limit experiment. See [scan data](../tools/samples/mordo-forensic-analysis/shifted-echo-scan.json).

## 4. What this changes for the addon auditions

Our first synthetic reverb used a 0.4 second nominal decay and filtered its effect layer to 240–3400 Hz. The original tail measurements instead favor approximately twice that decay, with substantial energy in the low region that the earlier bandpass attenuated.

The next reconstruction should preserve the clean voice and use a separate low-frequency-weighted tail targeting approximately 0.85 seconds of decay. The wet level, exact pre-delay, resonance structure and any pitch modulation remain unresolved. They must be labeled tuning choices, not measured Blizzard settings. The hollow and detuned auditions were controlled hypotheses, not inverse solutions.

For a simplified stationary model, `y_i = x_i * h`: observed clip, unknown dry performance, unknown shared response. Multiple utterances help estimate recurring properties of `h`, but the factorization is not unique without further constraints or a dry reference. A minimum-phase curve or synthetic reverb matched to these measurements would still be a reconstruction.

## Artifacts and reproduction

- [Original spectrograms](../tools/samples/mordo-forensic-analysis/original-spectrograms.png)
- [Decay comparison figure](../tools/samples/mordo-forensic-analysis/decay-measurements.png)
- [Tail spectra](../tools/samples/mordo-forensic-analysis/tail-spectra-probe.png)
- [Shifted echo diagnostic](../tools/samples/mordo-forensic-analysis/shifted-echo-scan.png)
- [Amplified excerpts of original tails](../tools/samples/mordo-forensic-analysis/original-tail-excerpts-amplified.wav): three short crops from the selected ending windows, with one constant gain and 6 ms edge fades. They may include residual vocal sound; they are not separated effect stems.

Scripts in `.local-state`: `probe_mordo_processing.py`, `probe_mordo_tails.py`, `fit_mordo_decay.py`, and `scan_mordo_shifted_echo.py`. Run with the `index-tts` Python environment, which has NumPy, SciPy, SoundFile and Matplotlib. The pitch-control generation uses the installed FFmpeg rubberband filter. No installed addon audio was modified.
