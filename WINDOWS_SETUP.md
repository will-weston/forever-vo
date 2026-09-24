# Local Forever voiceovers on this PC

The addon folders in `C:\Program Files (x86)\World of Warcraft\_classic_beta_\Interface\AddOns` are junctions to this checkout's `ForeverVO` and `ForeverVO_Data`. Code and generated audio here are therefore the files the client loads.

## Start playing

Fully exit and restart WoW Forever after installation or generating new audio. At character selection, enable Forever Voiceover and Forever Voiceover Data in AddOns. In game, `/fvo status` should report one loaded pack, and `/fvo` opens settings. Speak with the Deathknell quest NPCs; the generated pack starts with early undead quests, including Rude Awakening and Tainted Scroll. The quest log also offers a Play button for voiced quest offers.

The initial source is Classic quest dialogue. Forever-specific additions/rewrites need to be captured in game; this is not a complete Forever voice pack. Only generated MP3s are playable, regardless of how much quest text is in the database. This setup generates audio before playback, not live during conversations.

The September 24 upstream sync also imports the shared community corpus in
`tools/data/capture.json`. The local generator reads that corpus alongside
`.local-state` automatically; local captures keep precedence. The versioned
upstream sound index is not substituted for `.local-state/sound_index.json`,
which records the approved local performances. Importing quest text does not
generate or download new audio. Pack tables are rebuilt from the files actually
installed, preserving the 187 quests / 483 recordings in the current pack.

Upstream also supplies `pyproject.toml` and `uv.lock` for its Chatterbox toolchain.
`Run-Local.ps1` launches the existing Windows environment through uv with
`--no-project --offline --python`; it does not sync or replace the approved GPU
dependencies. Helpers use `tools.*` package imports, and direct Windows helper
invocations remain supported. The separate IndexTTS environment is unchanged.

## Add more Tirisfal dialogue

Run in PowerShell:

```powershell
cd C:\repos\forever-vo
.\Run-Local.ps1 tirisfal --limit 20
```

Each run generates up to 20 missing offer/turn-in files for Deathknell, Tirisfal, and the included undead warlock class quests, then rebuilds the pack. Existing unchanged files are skipped. Increase the limit for a larger batch. Keep the game closed during generation for better GPU performance, and restart it afterward. Run only one generator at a time.

To see upcoming lines without synthesizing them:

```powershell
.\Run-Local.ps1 tirisfal --dry-run --limit 20
```

Male and female undead reference voices were built from Blizzard greetings. Later quests may need other voice families; generate those with, for example, `Run-Local.ps1 build_voice_references human`. Missing references fall back to another available voice or Chatterbox's default, so check the dry-run output before expanding.

## Approved undead voice and pacing

The local undead male reference is the concatenation of "I am Forsaken" (563151)
and "Victory for Sylvanas" (563154), saved as `tools/voices/scourge-male.wav`.
Audition B's settings are saved in `.local-state/tts_settings.json`: CFG 0.3,
exaggeration 0.3, seed 42, and a 0.25-second pause between generated chunks.
Double hyphens become commas for speech. Female undead use the same pacing
settings with their own reference voice. Other voice families keep the defaults.
These settings also apply to future local generation through `Run-Local.ps1`.
Changing settings or reference recordings requires `--force` to replace existing audio.

Regenerate the five undead starter class quests through the level-10 voidwalker:

```powershell
.\Run-Local.ps1 generate --quest 3099 --quest 1470 --quest 1478 --quest 1473 --quest 1471 --progress --force --narrator-voices none
```

The prior pack and male reference were backed up under
`.local-state/backups/before-warlock-b-20260922-115055`.

## Capture Forever-specific text

Play with the addon enabled, then log out or `/reload` to write SavedVariables. Before another session overwrites them:

```powershell
.\Run-Local.ps1 ingest
.\Run-Local.ps1 generate --captured --limit 20 --narrator-voices none
```

Ingest also reads the repository's community captures. Everything stays on this PC unless you independently share or publish it. Character metadata is stored locally in `.local-state`, which Git ignores. Do not use `daily.sh`, `ingest.sh`, `install-timer.sh`, or `release_pack.py --upload` for this local workflow.

## Installed runtime

### IndexTTS trial pack

IndexTTS 2.5 is installed separately in `C:\repos\index-tts`, with its own `.venv`
and cached model files. The first nine undead/warlock starter quests can be
regenerated and installed with:

```powershell
cd C:\repos\index-tts
.\.venv\Scripts\python.exe -u C:\repos\forever-vo\tools\index_quest_batch.py --quest 363 --quest 364 --quest 3099 --quest 376 --quest 3901 --quest 3902 --quest 1470 --quest 380 --quest 6395 --install
```

This includes available offer, progress, and completion text, plus both player
gender variants where needed. It stages all recordings before installing them,
backs up affected existing files and tables, and rebuilds playback durations.
Omit `--install` to generate previews only. The latest installed manifest is
`.local-state/latest-index-batch.json`; WAVs, MP3s and per-run manifests live in
`.local-state/index-batches/`. Existing unrelated quest audio is preserved.

This trial keeps the successful two-line undead male reference fixed for male
NPCs and Elreth's four-line female reference for female NPCs. The 10-second rule
does not override the approved male reference. Settings match the IndexTTS
audition: BF16, seed 42, normal duration factor, no emotion override or reference
mixing. Chatterbox CFG/exaggeration settings do not apply to IndexTTS.

The older `Run-Local.ps1 generate` command still uses Chatterbox. Use the command
above to regenerate these quests with IndexTTS. Fully restart WoW after cutover.

### Tirisfal expansion

The local selection covers 50 Tirisfal/Deathknell leveling quests and the undead
warlock starter chain, with 142 available dialogue variants including progress.
It excludes the obsolete collector's-edition pet voucher and two level-55
Plaguelands quests tagged with Tirisfal in the source database. Text comes from
the Classic snapshot and available local captures; Forever-specific rewrites
still need in-game capture.

```powershell
cd C:\repos\index-tts
.\.venv\Scripts\python.exe -u C:\repos\forever-vo\tools\index_quest_batch.py --quest-file C:\repos\forever-vo\.local-state\tirisfal-index-selection.json --extra-references C:\repos\forever-vo\.local-state\tirisfal-index-references.json --skip-current --install
```

The extra-reference manifest records human and dwarf prisoner references,
Gordo's own sound set, and the human narrator used for object dialogue. Short
stock greetings are kept complete and joined with 0.1-second gaps; none are
stretched to reach ten seconds. Undead references remain the approved male
two-line sample and Elreth's female sample. Speeches longer than 450 characters
are generated in sentence-aligned chunks of about 220 characters with 0.2-second
joins to reduce missing endings. No angry-reference mixing is applied.

`--skip-current` reuses matching installed IndexTTS text/voice entries. It does
not compare reference hashes; omit it when intentionally changing references.
Generation manifests retain reference and output hashes for verification.

### Mulgore expansion

The Mulgore selection adds 54 quests and 146 available dialogue recordings:
36 regular Mulgore/Red Cloud Mesa quests, four starter class notes, and nearby
shaman, hunter, and druid starter chains (including the bear-form chain).
The database's unused quest 774 is excluded. This is Classic-source coverage;
Forever-specific additions and rewrites still require capture.

```powershell
cd C:\repos\index-tts
.\.venv\Scripts\python.exe -u C:\repos\forever-vo\tools\index_quest_batch.py --quest-file C:\repos\forever-vo\.local-state\mulgore-index-selection.json --extra-references C:\repos\forever-vo\.local-state\mulgore-index-references.json --skip-current --install
```

Mulgore references follow each NPC's client sound set, including Cairne's named
voice. Complete greeting/farewell clips are joined with 0.1-second gaps toward
a ten-second target; short available sets stay shorter. No angry or combat
clips are mixed in. Silent Ancestral Spirit dialogue borrows the Tauren male
standard set, while objects and the earth manifestation use narration.
Source clip IDs, durations, and NPC mappings are in the reference manifest.

- Isolated Python 3.11.16 in `.venv`.
- Chatterbox 0.1.6; PyTorch/torchaudio 2.8.0 with CUDA 12.8 for the RTX 5080. These two packages intentionally override upstream's older 2.6.0 requirement. CUDA computation and actual speech generation were tested.
- Exact dependency versions and package hashes: `tools/requirements-windows.lock`.
- Local FFmpeg 9.0.2, downloaded from Gyan's GitHub release with its SHA256 digest verified; provenance in `.local-tools/ffmpeg-source.json`.
- Downloaded Chatterbox model revision recorded in `.local-state/model-revisions.json`. The runner sets Hugging Face offline mode to reuse the cached model. Cache is under the Windows user's `.cache/huggingface` directory.
- Classic text snapshot and local captures live in `.local-state`. Audio is in `ForeverVO_Data/Sounds`; reference clips in `tools/voices`.
- No publishing credentials, scheduled tasks, automatic Git pulls/pushes, or inference server were configured.

The normal entry point is `Run-Local.ps1`, which selects the environment, local FFmpeg and game folder. It temporarily changes environment variables only in its process and restores them afterward.

## Reinstall Python packages if needed

```powershell
.\.bootstrap\Scripts\uv.exe pip sync --python .venv\Scripts\python.exe tools\requirements-windows.lock --index https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match --require-hashes
```

The full runtime and external models are separate from the earlier source-only security review. Local safety changes reject invalid quest events, confine generated audio paths, and bound compressed imports. Verify those with `.venv\Scripts\python.exe tools\test_local_safety.py`.

To remove the addon later, unlink the two junctions in the game's AddOns directory only; do not recursively delete their targets. This repository and the model cache can remain for later use.
