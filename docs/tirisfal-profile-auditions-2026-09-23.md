> Historical snapshot: the subsequent [Tirisfal rollout](C:/repos/forever-vo/docs/tirisfal-profile-rollout-2026-09-23.md) imported additional source text and installed the approved native-profile pack. Counts and installation status below describe this earlier research/audition stage.

# Tirisfal: native voice profiles and auditions

September 23, 2026. IndexTTS 2.5. These are casting auditions; the installed game audio has not been replaced.

The pilot covers Rude Awakening, The Mindless Ones, Tainted Scroll, The Damned, Rattling the Rattlecages, Scavenging Deathknell, and Piercing the Veil. It maps 21 stage/variant records across those seven quests, and renders their offers plus a Maximillion turn-in excerpt. Two additional auditions use Forever quest text: A Difficult Path and Patience.

**Casting**

| Native profile | NPCs verified on Wowhead | Reference |
| --- | --- | --- |
| UndeadMaleStandard | [Undertaker Mordo](https://www.wowhead.com/classic/npc=1568/undertaker-mordo#sounds) | 22 words / 13.66 seconds |
| UndeadMaleDark | [Shadow Priest Sarvis](https://www.wowhead.com/classic/npc=1569/shadow-priest-sarvis#sounds), [Maximillion](https://www.wowhead.com/classic/npc=2126/maximillion#sounds) | 23 words / 14.41 seconds |
| UndeadFemaleStandard | [Novice Elreth](https://www.wowhead.com/classic/npc=1661/novice-elreth#sounds), [Venya Marthand](https://www.wowhead.com/classic/npc=5667/venya-marthand#sounds) | 24 words / 14.27 seconds |
| UndeadMaleWarrior | [Deathguard Saltain](https://www.wowhead.com/classic/npc=1740/deathguard-saltain#sounds), [Executor Zygand](https://www.wowhead.com/classic/npc=1515/executor-zygand#sounds) | 27 words / 14.49 seconds |

**Selection formula**

NPC ID → verified greeting/farewell sound kits → one reusable identity reference. The recording suffix (such as Greeting03) identifies a line, not a distinct actor.

Select complete phrases by total words and lexical variety, with a 14.8-second budget below the model’s 15-second truncation point. Target up to 30 words, but accept fewer rather than cutting or speeding up speech. Prefer at least three words per clip; order greetings before farewells; preserve each original recording and insert an 80 ms gap. The four selected references contain 22–27 words. Word diversity is a practical proxy, not a measured phoneme-coverage guarantee.

Keep the Dark set’s “I am Forsaken” and “Victory for Sylvanas” anchors. Other families retain their own actors. Angry lines stay out of identity references; they can be separately auditioned for a specific performance later.

Render a continuous utterance at normal speed. This comparison uses the speaker reference without a separate emotion reference. Editorial tone notes guide text selection and punctuation; they are not an unsupported natural-language style prompt sent to IndexTTS.

Preserve float vocoder output, apply a single headroom gain if needed, write native-rate PCM24, and append 0.5 seconds of silence. No added reverb, EQ, pitch change, dynamic compression, or sentence stitching.

**Listen: source on the left, generated quest speech on the right**

Several first-pass long takes lost or mangled ending words. Their retakes below use coherent opening paragraphs, labeled as excerpts. Earlier failed takes remain archived under previous-takes and are not linked as candidates.

| Quest / speaker | Assembled original reference | IndexTTS audition |
| --- | --- | --- |
| **Rude Awakening** — Undertaker Mordo<br>full offer, 22.1s | ![undead-male-standard source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-standard-source.wav) | ![Rude Awakening audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/363-accept.wav) |
| **The Mindless Ones** — Shadow Priest Sarvis<br>full offer, 27.0s | ![undead-male-dark source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-dark-source.wav) | ![The Mindless Ones audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/364-accept.wav) |
| **Tainted Scroll** — Shadow Priest Sarvis<br>full offer, 16.7s | ![undead-male-dark source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-dark-source.wav) | ![Tainted Scroll audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/3099-accept.wav) |
| **Tainted Scroll** — Maximillion<br>excerpt, 17.4s | ![undead-male-dark source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-dark-source.wav) | ![Tainted Scroll audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/3099-complete.wav) |
| **The Damned** — Novice Elreth<br>excerpt, 20.7s | ![undead-female-standard source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-female-standard-source.wav) | ![The Damned audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/376-accept.wav) |
| **Rattling the Rattlecages** — Shadow Priest Sarvis<br>full offer, 25.1s | ![undead-male-dark source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-dark-source.wav) | ![Rattling the Rattlecages audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/3901-accept.wav) |
| **Scavenging Deathknell** — Deathguard Saltain<br>excerpt, 18.1s | ![undead-male-warrior source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-warrior-source.wav) | ![Scavenging Deathknell audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/3902-accept.wav) |
| **Piercing the Veil** — Venya Marthand<br>excerpt, 20.2s | ![undead-female-standard source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-female-standard-source.wav) | ![Piercing the Veil audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/1470-accept.wav) |
| **A Difficult Path** — Shadow Priest Sarvis<br>full offer, 20.1s | ![undead-male-dark source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-dark-source.wav) | ![A Difficult Path audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/98601-accept.wav) |
| **Patience** — Executor Zygand<br>excerpt, 21.5s | ![undead-male-warrior source](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/undead-male-warrior-source.wav) | ![Patience audition](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/99141-accept.wav) |

**Forever data imported**

Collected available evidence for 58 Tirisfal/Deathknell quest IDs, including 22 IDs absent from our Classic snapshot. Twenty-one of those Forever IDs, with 26 observed dialogue stages, are now in the active local input files. Whispering Horror Residue is preserved separately pending verification of its non-NPC starter. Missing stages remain missing; this is not a complete Forever database.

[Preserved source variants and hashes](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/tirisfal-corpus.json) · [Import audit](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/forever-import-audit.json) · [Verified additional quest speakers](C:/repos/forever-vo/tools/voice_profiles/forever-tirisfal-quest-speakers.json)

The active loader was checked against every imported text and NPC ID. Same-title Classic recordings were not reassigned to new IDs. The native-profile mapping currently drives this audition plan; the installed pack still uses its previously generated audio.

Aramis Hammerhand’s inspected Forever page exposes no sound list. His dialogue is preserved, but no native voice-set identity has been invented for him. New speakers need the same mapping verification before they enter this profile-based rendering workflow.

**Next decision**

Choose the best reference/voice family before generating full dialogue. Reuse it for NPCs sharing that native set, then vary performance through quest-specific intent and punctuation. Keep short auditions for casting; long final speeches require their own content checks and retakes. Reference hashes belong in generation cache keys so a revised voice cannot silently reuse old audio.

[Profile registry](C:/repos/forever-vo/tools/voice_profiles/tirisfal.json) · [Reference provenance](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/reference-manifest.json) · [Performance plan](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/performance-plan.json) · [Audio checks](C:/repos/forever-vo/tools/samples/tirisfal-stock-profiles/audio-verification.json)

Audio checks cover finite samples, peak headroom, the silent tail, and local speech-to-text comparisons. ASR is not a listening-quality score; proper names and small word ambiguities are retained in the diagnostic file for review.
