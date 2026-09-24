> Historical snapshot: the subsequent [Tirisfal rollout](C:/repos/forever-vo/docs/tirisfal-profile-rollout-2026-09-23.md) imported additional source text and installed the approved native-profile pack. Counts and installation status below describe this earlier research/audition stage.

**Forever quest data and the missing-voice gaps**

Research date: September 23, 2026. Companion to the [NPC voice strategy report](C:/repos/forever-vo/docs/undead-npc-voice-strategy-2026-09-23.md).

**Yes: usable Forever-specific quest text exists.** Wowhead has some new quests, upstream ForeverVO has a growing machine-readable collection of actual dialogue, and your own client cache contains additional offer text. I did not find a verified, complete public database containing every Forever quest’s offer, progress, completion, gossip, and correct speaker.

The most actionable discovery is in our configuration: the Index batch tool selects `.local-state` as its data directory. That directory currently has the Classic snapshot, but no `capture.json` or `bulk/questcache.json`. The repository has both under `tools/data`, where this generation path does not read them. This accounts for a real source-data gap in our batches; acquiring another database alone would not connect that text to generation. [Batch configuration](C:/repos/forever-vo/tools/index_quest_batch.py:21); [source loader](C:/repos/forever-vo/tools/generate.py:181)

| Source | What I verified | Use for our project |
| --- | --- | --- |
| **Wowhead Forever** | Actual descriptions exist for new IDs such as [Tomb Weed, 99142](https://www.wowhead.com/forever/quest=99142/tomb-weed) and [Hides for the Forsaken, 97558](https://www.wowhead.com/forever/quest=97558/hides-for-the-forsaken). Their wording agrees with the descriptions in your current cache. The inspected pages do not supply progress/completion dialogue. | Useful lookup and cross-check source. Use the Forever section and exact quest ID. I have not verified a complete downloadable export. |
| **Upstream ForeverVO captures** | The inspected snapshot has **565 quest-stage records for 289 distinct quests**, plus **260 gossip lines**. Stages: 264 offers, 97 progress lines, 204 completions. There are 45 community export JSON files, compared with 3 in our checkout. These totals include original Classic quests encountered in Forever. [Captured dialogue](https://github.com/quinn-dougherty/forever-vo/blob/600a37d4e08b1b3a8d27fbfa00c8c685f4d014f7/tools/data/capture.json) | Best immediately usable structured source for dialogue plus speaker metadata. Import selectively with provenance and placeholder checks. |
| **Upstream ForeverVO quest cache export** | **257 offer records**, without captured NPC metadata or event-specific progress/completion dialogue. [Cache export](https://github.com/quinn-dougherty/forever-vo/blob/600a37d4e08b1b3a8d27fbfa00c8c685f4d014f7/tools/data/bulk/questcache.json) | Additional offer text; join to independently verified speakers before casting. |
| **Your current client cache** | Build **69977**; the existing parser decoded **80 quests**, including **24 IDs absent from our Classic snapshot**. The latter is a candidate classification, not proof all 24 are wholly new quest designs. | Immediate additional text, preserved in a research snapshot. It includes several Tirisfal quests missing from the installed pack. |
| **WoW Forever Talents** | Its quest index lists 75 quests, including 15 it classifies as new, with individual description pages. Examples: [A Frightened Request](https://wowforevertalents.com/quests/a-frightened-request-92401/) and [The New Plague](https://wowforevertalents.com/quests/the-new-plague-95216/). It documents cache-derived text and distinguishes observed NPCs from names inferred from wording. [Index](https://wowforevertalents.com/quests/) | Useful partial dungeon corpus. Its blanket statement that Wowhead has no Forever-added quests is contradicted by the live Wowhead pages above; check each quest directly. |
| **QuestieDB / Everything Quests** | QuestieDB has Forever-specific files, but its schema primarily contains titles, starters/finishers, requirements, objectives, and chains. Its initial adoption documents an Era seed and coordinate conversion. Everything Quests documents 25 newly gathered Forever quests, mainly Zephras Isle and Elwynn. [Schema](https://github.com/Questie/QuestieDB/blob/b6f5b07b0acf1c820993cbb0ce2521c912bb4c92/data/Forever/foreverQuestDB.lua); [adoption record](https://github.com/Questie/QuestieDB/blob/b6f5b07b0acf1c820993cbb0ce2521c912bb4c92/docs/forever-data.md); [Everything Quests](https://www.curseforge.com/wow/addons/everything-quests) | Helpful metadata. A quest-helper database is not automatically a full dialogue database, and converted Era coordinates do not establish new-content coverage. |
| **Forever Wiki** | A small set of documented new quest pages, with evidence and explicit gaps. [Quest index](https://wowfwiki.com/wiki/Quests) | Useful corroboration; not a complete generation corpus. |

Our local repository capture snapshot contains 326 quest stages for 156 quests and 170 gossip lines. The newer upstream snapshot has substantially more material. Of its 289 quest IDs, 155 are absent from our local Classic snapshot; this is an audit result, not a definitive count of newly designed Forever quests.

**Concrete Tirisfal material we can work from**

| Quest | ID | Available evidence inspected | Remaining gap |
| --- | ---: | --- | --- |
| Tomb Weed | 99142 | Current local offer and Wowhead description | Confirm speaker ID; collect progress/completion as applicable |
| That Shadowvale Green Elixir | 95314 | Current local offer | Confirm speaker and remaining stages |
| Sticks and Bones | 86784 | Current local offer | Confirm speaker and remaining stages |
| Hides for the Forsaken | 97558 | Local cache, Wowhead, community offer attributed to Shelene Rhobart, NPC 3549 | Progress/completion absent from inspected community record |
| A Difficult Path | 98601 | Community offer, progress, completion; stage records reference NPCs 1569 and 244808 | Review speaker per stage and cast the additional NPC |
| The Argent Emissary | 96895 | Community offer and completion | Review speaker per stage; progress coverage unknown |
| The Cult of the Damned | 96897 | Community offer | Remaining stages |
| Remnants of War | 96898 | Community offer | Remaining stages |
| The Wrath of Rath’mael | 92422 | Community offer and completion; current cache entry | Speaker/reference review and remaining stages |

Community evidence is in the [coverage audit](C:/repos/wow-voice-research/forever-quest-coverage-2026-09-23.json). The table describes data availability, not generated audio or a complete quest-chain order. A missing progress record does not prove a quest has a distinct progress speech.

The current cache also has **Rear Guard Patrol, 99156**. Our Classic snapshot has ID 356 with the same title and a different offer. We already have audio for 356. Copying that MP3 onto the new ID would give the wrong speech. Preserve exact IDs, text, and stage-specific speakers.

The local parser targets build 69913 and reported zero unrecognized records on this build 69977 cache. I manually inspected several decoded offers and cross-checked Tomb Weed and Hides for the Forsaken against Wowhead. Hides also matches the community offer after normalizing player-name placeholder case. This supports using the extraction for review, but does not validate every field of all 80 records.

**Recommended next steps**

1. Connect community captures and cache input to the active local data workflow. Record source, build, retrieval date, quest ID, stage, speaker ID, and text hash. Retain conflicting versions for review; an old capture should not silently replace a newer observed rewrite.
2. Combine the latest community data with the saved local cache. Community captures provide progress/completion and NPC information the offer cache lacks. Keep cache-only entries with unknown speakers pending instead of guessing a voice.
3. Prioritize the Tirisfal entries above. Use the character registry proposed in the earlier report, retaining each NPC’s identity across stages.
4. Generate reviewed missing or changed lines with our selected local renderer. Importing JSON alone will not make the NPC speak.
5. Preserve local captures after sessions. Current saved-variable files contain six quest stages across four quests; inspected backups contain no additional captured quest stages. Dialogue seen since the last disk save may remain in game memory. Reloading the UI or logging out normally writes SavedVariables. Progress/completion still requires encountering that dialogue. Local ingestion can use these files without uploading them.

I saved the [80 extracted offer records](C:/repos/wow-voice-research/forever-local-quest-offers-2026-09-23.json) and a byte-for-byte cache snapshot under `C:/repos/wow-voice-research`. The extraction includes its source and parser hashes. The fresh [upstream checkout](C:/repos/wow-voice-research/forever-vo-upstream) is pinned to `600a37d4e08b1b3a8d27fbfa00c8c685f4d014f7`; QuestieDB is pinned to `b6f5b07b0acf1c820993cbb0ce2521c912bb4c92`.

This research produced snapshots and an audit. It has not imported them into the active generation corpus or installed replacement audio.
