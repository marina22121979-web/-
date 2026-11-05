---
name: ae-sound-effects
description: Add a measured sound pass to a video made in Adobe After Effects through the After Effects MCP server. Reads the sound cues from the comp's markers, renders a silent master with aerender, checks the music's beat grid against the kick drums, lands cuts on the beat, places one real sound effect per cue from a CC0 library, mixes to -16 LUFS with true peaks below -4 dBFS measured on the exported MP4, and brings the final mix back into the After Effects project. Use when someone wants sound effects, sound design or music added to an After Effects animation, or says it sounds like cheap beeps.
---

# Sound effects (After Effects)

Claude can't hear. So this skill never judges sound by feel: it measures every step and hands the user 5 timestamps to check with headphones. It never says "it sounds good".

This is an After Effects front and back end for Bart's `sound-effects` skill, which does the measuring, the library and the mix. The method is Vox's sound-pass prompt (@Voxyz_ai, https://x.com/Voxyz_ai/status/2109358372873183564); keep that credit. **Load `ae-motion-core` first** for rendering.

## 0. Install the sound library (first run only)

The sound library, `sound_pass.py` and the licence rules live in Bart's skill. Install it once:

```bash
npx skills add Barty-Bart/motion-graphics        # pick "sound-effects"
```

or without npm:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Barty-Bart/motion-graphics.git ~/.claude/skills-src/motion-graphics
git -C ~/.claude/skills-src/motion-graphics sparse-checkout set skills/sound-effects
```

Below, `$SFX` means that `sound-effects` folder (it contains `scripts/sound_pass.py`, `sfx/manifest.json`, `MUSIC.md`, `LICENSES.md`). **Read its `SKILL.md` once**: its rules on licences, music sources and the swap report apply here unchanged. In short: never synthesise music or effects, use the bundled CC0 sounds first, download Mixkit sounds only into the user's project and never commit them, and check every licence for the user's use case before the final export.

Set up the Python environment in the user's project (needs ffmpeg and **Python 3.10+**; macOS ships 3.9 as `python3`, so check `python3 --version` and use a newer one, e.g. Homebrew's `/opt/homebrew/bin/python3.11`):

```bash
python3.11 -m venv .sound-effects
.sound-effects/bin/pip install librosa soundfile numpy scipy matplotlib
```

## 1. Cues come from the comp's markers

While building, every moment that needs a sound gets a **comp marker** on the main comp (`setMarker`):

- comment `sfx: <type> | <what happens>`, e.g. `sfx: whoosh | camera glides to feature 2`, `sfx: impact | logo slams`
- for long sounds the marker's **duration** is the sound's length: typing (how long it types), a riser (it *ends* on the next hit)
- `<type>`: `whoosh` (movement; starts 2 frames early), `cut` (scene cut), `pop` (something appears), `click`, `typing`, `riser` (build-up), `impact` (the reveal, the loudest), `tick` (small UI, very quiet), `ding` (success), `glitch` (error/tech), `ambience` (a bed under everything)

One sound per cue; the script varies takes within a category so repeats don't sound robotic. If markers are missing, derive them from the animation: contacts are Position keyframes, camera moves are the camera's keyframes, typing starts and ends where the typing expression does.

Export them:

1. `listMarkers { compName: "<main comp>" }` and save the returned JSON to `sound/markers.json`.
2. `python3 <this skill>/scripts/markers_to_cues.py sound/markers.json sound/cues.json` (add `--offset <s>` if the render starts later than comp time 0, e.g. at the work area start). It prints any marker it couldn't use.

## 2. Render a silent master

Mute any music or audio layers in the comp first (the script adds the music itself), save the project, then render the comp with Best Settings to an H.264 `.mp4` (see `ae-motion-core`: `addToRenderQueue` + `start-render`, poll `render-status`). This is `silent.mp4`. Its frame rate and length must match the comp.

## 3. Music

The user's track, or one from `$SFX/MUSIC.md` (suggest 2–3 that fit; downloaded at runtime into the project, never committed). Ask where it came from and what licence it has; pass both to the script. Without them the run marks the music LICENCE NOT CONFIRMED; say so plainly. Mixkit's licence page renders its terms with JavaScript, so a web fetch can't read them: ask the user to open https://mixkit.co/license/#musicFree in their browser, and until someone has, record the licence as not re-checked today.

## 4. Run the sound pass

```bash
.sound-effects/bin/python $SFX/scripts/sound_pass.py --video sound/silent.mp4 --cues sound/cues.json \
  --music <track> --manifest $SFX/sfx/manifest.json --out sound/out \
  --use-case "YouTube" --music-source "track, artist, link" --music-license "..."
```

It checks the beat grid (librosa sometimes locks onto the off-beat; the script compares against the kick drums and shifts the grid), places the sounds, mixes (voiceover > SFX > music, music about −12 dB under the SFX), measures the **exported** MP4 and adjusts until it is about **−16 LUFS integrated** with **true peak below −4 dBFS**, then writes `after.mp4`, `report.html`, `SOUND.md`, `CREDITS.txt`, `beatgrid.png` and `checks/`. Read its log; fix anything over target. Show the user `beatgrid.png`.

**Every cue on the beat.** The log reports the beat error only for cuts and reveals. In animation driven by contacts (bounces, key presses, impacts) check **every** cue:

```bash
.sound-effects/bin/python <this skill>/scripts/cue_beat_check.py --music <track> --cues sound/cues.json --sound-md sound/out/SOUND.md
```

It flags cues more than 40 ms from a beat. Errors that **grow** through the video mean the animation's tempo doesn't match the track (fix the tempo, see `ae-motion-core`, "Music first"); a **constant** offset means the music should start a little earlier or later.

**Big moves on the beat.** The log reports each cut's distance from the nearest beat in ms. In After Effects the timeline is yours to change, so prefer fixing the **animation**: shift the scene's layers and keyframes (and their marker) onto the beat, re-render the silent master and run again. If you can't move the animation, move where the music starts instead (the script searches offsets).

## 5. Bring the mix back into After Effects

So the project matches the delivered video:

```bash
ffmpeg -y -i sound/out/after.mp4 -vn -c:a pcm_s16le sound/out/mix.wav
```

then `importFootage { path: ".../mix.wav", folderName: "Sound" }` and `addFootageToComp { compName: "<main comp>", itemId: <id>, startTime: 0, layerName: "MIX (sound pass)" }`, and leave the original music layer muted. Import it into its own folder: a build script that rebuilds its folder would delete it.

If you change only visuals afterwards (no timing), you don't need a new pass: re-render the silent master and put the measured mix back on it with `ffmpeg -i silent.mp4 -i sound/out/after.mp4 -map 0:v -map 1:a -c copy -shortest final.mp4`, then re-measure the loudness on `final.mp4`.

## 6. Swap report

`report.html` lists every cue with its sound (with a play button), source, licence and alternatives. Open it for the user. They choose, download `swaps.json`, and you re-run with `--swaps swaps.json` (`"auto"` = pick another from the alternatives). Keep cue indices stable between runs: don't reorder or delete markers between runs, add new ones at the end of a pass.

## Report to the user

Report the licence check (all known, or each unknown sound by name), the use case and whether it is allowed, the music source and licence (or that it is not confirmed), that `CREDITS.txt` is there if they want it, the beat-grid result (shifted or not, and by how much), the cut-to-beat errors (and which you fixed in the animation), final LUFS and true peak (stereo and mono), and the 5 timestamps to check with headphones. Don't tell them it sounds good.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `sound-effects` skill (MIT; its sounds are CC0, see its `LICENSES.md`).
