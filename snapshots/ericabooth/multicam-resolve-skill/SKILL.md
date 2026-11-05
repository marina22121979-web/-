---
name: multicam-resolve-build
description: >
  Build a synced, mastered, graded 4K multicam timeline in DaVinci Resolve from a
  folder of camera clips + a master audio recorder file. Use when the user has
  multi-camera footage plus a separate audio recording and wants an auto-synced,
  audio-mastered, marker-annotated Resolve timeline. Deterministic audio-waveform
  sync via ffmpeg; project assembly via the Resolve scripting API.
---

# Multicam Resolve Build

Turn a shoot folder into a ready-to-edit 4K multicam timeline. No manual clapping,
no GUI waveform-sync roulette — offsets are computed by cross-correlation and the
timeline is assembled programmatically.

## When to use
A multi-camera event (concert, panel, service, interview) recorded with a separate
audio recorder (Zoom/Tascam/lav mixer). Each camera may have split clips from
battery/card swaps. You want everything synced to the recorder, the recorder audio
mastered, camera audio muted, angle markers dropped, and a grade template applied.

## Prerequisites
- DaVinci Resolve **Studio** running, Preferences ▸ System ▸ General ▸
  *External scripting using* = **Local**.
- Python 3.11–3.12 (NOT 3.14 — Resolve's `fusionscript.so` ABI; 3.11+ needed for stdlib `tomllib`).
- `ffmpeg`/`ffprobe` on PATH.
- Deps: `numpy soundfile librosa`.

## Configure
Copy `config.example.toml` and edit for the new shoot:
- `media_dir`, `project_name`, `timeline_name`, `width/height/fps`
- `master_audio` = the recorder file
- one `[[cameras]]` block per camera (→ one video track). List split clips in
  record order inside `clips`.
- loudness/compression targets; `analysis_rate` & `min_confidence` for sync;
  `[autocut]` for the beat-synced rough cut; `[effects]` for the framing pass.

## Run (in order)
```bash
PY=python   # a 3.11/3.12 interpreter with numpy soundfile librosa installed
$PY step1_prep_audio.py     config.toml   # master the recorder (ffmpeg loudnorm+comp)
$PY step2_compute_sync.py   config.toml   # GCC-PHAT sync -> work_dir/offsets.json
$PY step3_build_timeline.py config.toml   # build project/timeline/markers in Resolve
$PY step4_apply_grade.py    config.toml   # scriptable CDL/LUT pass (optional)
$PY step5_auto_cut.py       config.toml   # beat-synced rough-cut timeline (optional)
$PY step6_effects.py        config.toml   # zoom mvi* clips + flag Dynamic Zoom subset (optional)
```
`step2` is inspectable — check `offsets.json` and the PSR column before building.
Anything below `min_confidence` (PSR ~8) is flagged; point the recorder at a louder
passage and re-run.

## What each layer can and can't do (be honest with the user)
| Step | Mechanism | Fully automated? |
|------|-----------|------------------|
| Audio master | ffmpeg EBU R128 + acompressor | ✅ |
| Sync | ffmpeg + GCC-PHAT cross-correlation (numpy) | ✅ (frame-accurate) |
| Project/timeline/tracks/placement | Resolve API `AppendToTimeline(recordFrame)` | ✅ |
| Mute camera audio | video-only import (camera audio never added) | ✅ |
| Markers (IN/OUT/battery/switch) | `Timeline.AddMarker` | ✅ |
| Beat-synced rough cut | librosa beats + LRU angle rotation | ✅ |
| Static zoom on mvi* clips | `TimelineItem.SetProperty ZoomX/ZoomY` | ✅ |
| Contrast/shadow/color-match base | `TimelineItem.SetCDL` / `SetLUT` | ✅ (approx) |
| **Dynamic Zoom enable** | not in the API (only `DynamicZoomEase`) | ⚠️ ease + color-flag scripted; toggle on in GUI |
| **Noise reduction + sharpen nodes** | node graph — **not scriptable** | ⚠️ one-time GUI template + "Apply Grade to All Clips" |

## The color template (one-time manual, then reused forever)
1. Color page → pick a clean, well-lit clip from each camera.
2. Build the reference grade on one clip: shadows +10%, contrast +10%, a
   **Sharpen** node, and a **Spatial/Temporal NR** node at a light setting
   (Studio only). Balance the cameras to it (use the scopes / a shot match).
3. Right-click the clip → **Grab Still** (save as a PowerGrade), and/or select all
   clips and **Apply Grade to All Clips** from the reference.
4. Re-run `step4` if you also want the scripted CDL top-up.
Save that PowerGrade — next shoot, apply the same look in two clicks.

## Reusing this as a Claude Code skill
This folder IS the skill. To register it: drop it under
`~/.claude/skills/multicam-resolve-build/` (this `SKILL.md` is the entry). Then
"build a multicam timeline from <folder>" will trigger it. The steps are plain
scripts, so they also run standalone or from cron for hands-off batch builds.
