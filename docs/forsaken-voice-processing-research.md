# Forsaken voice processing research

Research date: 2026-09-22. Target: the hollow character of Undertaker Mordo's original Classic NPC greeting/farewell recordings, especially the perceived distant voice around 400–500 ms later.

## Finding

No source found in this research identifies the original Forsaken NPC processing chain, plugin, preset, or delay settings. Blizzard production material supports layered and processed character voices in general. It does not establish which effects were used on Mordo.

The most useful reconstruction candidates are short comb filtering, a quiet detuned or pitch-shifted voice layer, and filtered diffuse reflections. These are hypotheses to audition individually, not a recovered Blizzard recipe. A 450 ms shifted echo remains worth a separate test because it addresses the listener's description directly.

## What the primary sources actually establish

1. **Blizzard, The Sounds of Koprulu.** Glenn Stafford explicitly describes original Protoss voices made with pitch shifting and multiple pitch-shifted voices stacked together. This is direct evidence of an older Blizzard character-voice technique. It is about StarCraft; applying it to Forsaken would be an inference. [Official article](https://news.blizzard.com/en-us/article/20722027/the-sounds-of-koprulu).

2. **Blizzard, Under the Hood: Anatomy of Sound Design (2013).** The team breaks down a Zandalari Battlesaur voice into an actor's edited performances, animal layers, and final processing/mastering. This establishes the layering workflow, not the Forsaken effect. [Official breakdown](https://worldofwarcraft.blizzard.com/en-us/news/9135372).

3. **Rhonda Cox interview (2016).** WoW's audio producer describes overseeing recorded dialogue through processing and implementation. Useful confirmation of the production pipeline, but no individual effect chain. [Interview](https://designingsound.org/2016/07/27/a-decade-in-the-world-of-audiocraft-an-interview-with-rhonda-cox/).

4. **Blizzard audio team interview (2014).** Joseph Lawrence says his Diablo team tends to avoid conspicuous chorus/flange because it can distract from believable sound. This is a useful counterweight to assuming every supernatural Blizzard voice uses an obvious chorus. The remarks are about Diablo, not a prohibition on WoW effects. Andrea Toyias also emphasizes casting and vocal performance. [Interview](https://speakhertz.com/6716/interview-blizzard-entertainment-audio-team).

5. **Julian Kwasneski, StarCraft: Ghost interview (2004).** He describes processing edited voice batches differently for character groups, using Pro Tools and Bias Peak with tools including Waves and Pitch'n Time. This provides period context only. Owning those tools is not evidence that any particular one made Mordo's sound. [Interview](https://www.blizzplanet.com/blog/comments/starcraft-ghost-interview-julian-kwasneski).

## Effects that can account for parts of the description

| Mechanism | What it changes | Relevance and limits |
| --- | --- | --- |
| Short comb filtering | Mixing a voice with a copy delayed a few milliseconds creates recurring spectral peaks and dips. | A strong candidate to test for the hollow tone itself. It does not create a distinct half-second repeat. |
| Quiet detuned/pitched duplicate | Adds a second vocal texture with slightly different pitch and timing. | Fits a layered or ghostly character; historically documented for Protoss, unconfirmed for Forsaken. |
| Filtered reverb / diffuse delay | Spreads vocal energy across many reflections; filtering controls which parts linger. | Could explain a distant tail emerging between words. A tail is not proof of any particular reverb algorithm. |
| Frequency-shifted delay | Moves frequency components by a fixed number of hertz; different from musical pitch transposition. | A candidate for an uncanny, phase-like quality. Larger shifts can turn metallic or robotic. |
| Long delayed voice, optionally pitch shifted | Places a recognizable secondary phrase later. | Directly tests the reported 400–500 ms impression. The earlier test weakens only the simple fixed-copy version. |

The acoustic mechanisms above are documented by effect developers:

- **iZotope:** very short delayed copies produce comb filtering and a hollow sound; the article includes a vocal demonstration. This is the closest explicit technical match to the word "hollow." [Comb filtering](https://www.izotope.com/community/blog/what-is-comb-filtering).
- **iZotope:** chorus commonly uses 15–35 ms delays; flanging uses shorter delays and moving cancellations. Our existing ~22 ms double is in the chorus/doubling range, so a short fixed comb test would be a materially different experiment. [Modulation effects](https://www.izotope.com/community/blog/understanding-chorus-flangers-and-phasers-in-audio-production).
- **Eventide:** MicroPitch combines detuned voices and delays, allowing subtle thickening through more obvious echoes. This documents a mechanism, not evidence that Blizzard used this product. [MicroPitch](https://www.eventideaudio.com/plug-ins/micropitch/).
- **Valhalla DSP:** Ghost mode combines delay, frequency shifting, and diffusion; Pitch mode separately offers pitch shifting and detuning. The algorithm description helps define independent tests. The plugin was introduced in 2019 and therefore cannot be the original 2004 tool. [Algorithm descriptions](https://valhalladsp.com/2019/04/16/valhalladelay-the-mode-control/).
- **Ableton:** small frequency shifts mixed with the original can create phasing; large shifts can create dissonant metallic results. Ring modulation and pitch shifting are distinct operations. [Shifter documentation](https://www.ableton.com/en/manual/live-audio-effect-reference/#shifter).

## Relationship to our waveform analysis

The previous analysis used 16 byte-verified Wowhead recordings and a 450 ms delayed-copy positive control. It found no consistent 400–500 ms fixed-copy signature. That result does not establish comb filtering, exclude every long echo, or identify Blizzard's studio chain.

The test was aimed at long delays. Speech has its own periodic structure at short lags, making blind identification of a few-millisecond effect difficult. A cepstral bump in that range can be the actor's fundamental period rather than an effect. Do not label a short-lag feature as processing without stronger evidence.

Our audition's added reverb begins at 16 ms and has a nominal 400 ms decay. Its double varies between 20.5 and 23.5 ms. Those are known properties of our script, not estimates of the original recordings.

See the local [analysis report](../tools/samples/mordo-delay-analysis/analysis.json) and [figure](../tools/samples/mordo-delay-analysis/waveform-and-delay-analysis.png).

## Proposed controlled auditions

These are deliberately chosen starting values, not measurements or sourced Blizzard settings. Reuse the exact same clean Mordo take for every version.

| Audition | Initial settings | Question answered |
| --- | --- | --- |
| Dry control | Existing clean take, level matched. | What is already in the generated voice? |
| Hollow tone | One fixed 4–7 ms copy, approximately -15 to -10 dB relative to dry, no feedback, reverb, or modulation. | Does spectral hollowing supply the missing character? |
| Detuned layer | One copy shifted down 10–20 cents, delayed 15–25 ms, approximately -18 dB. | Does a restrained second voice supply the missing texture? |
| Late shadow | One 450 ms copy, lowered 1–2 semitones, filtered to about 250–3500 Hz, approximately -20 dB, no feedback. | Is the listener describing a distinct lower voice arriving later? |
| Diffuse tail | Quiet filtered reflections with approximately 0.35–0.5 s decay, no pitched double. | Does the relevant impression come from lingering ambience? |

Render separate variants first, level match using a constant gain, retain headroom and complete tails, and compare in mono as well as normal playback. Only combine components after identifying which single component moves toward the reference. Strong flange sweeps, aggressive saturation, heavy compression, and large cathedral reverbs are not justified by this research.

## Search scope and unresolved questions

Searched original WoW/Forsaken/Undertaker Mordo production terms, Blizzard sound-team interviews and panels, early staff/voice-credit leads, StarCraft/Warcraft character processing, and effect-developer documentation. Many results concern Lich King fan recreations, runtime Death Knight effects, newer Blizzard games, or unrelated games named Forsaken. None establish the Classic Mordo chain.

Exact attribution would require an original session, unprocessed/processed pair, or a statement from someone who made these particular NPC recordings. No such source was located. No addon audio was changed during this research.
