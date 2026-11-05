---
name: video-demo-overlay
description: Assemble a short no-narration demo video (1-3 min) from raw screen/hands-on footage, with bilingual text-overlay captions. The agent reads sampled frames to decide what to show; local computer vision (motion-diff, audio onset) finds frame-exact cut points; output is an editable FCP7 XML timeline for Premiere Pro / DaVinci Resolve. Use for product demos, workbook activity clips, tutorial b-roll — anything where captions replace a voice track.
---

# Action-Anchored Demo Video (v1)

No narration track: the *on-screen action* is the timeline's spine. You (the
agent) understand *what* to show by reading sampled frames; the CV scripts
find *exactly where* to cut; captions carry the explanation.

## Prerequisites

Python 3.10+ with `opencv-python`, `numpy`, `pillow`; `ffmpeg` on PATH; an
NLE that imports FCP7 XML (Premiere Pro, DaVinci Resolve).

## Workflow

### 1. Footage in (human)
Raw clips into a `footage/` folder. A shot list (what the video must show,
in order) helps but the agent can propose one from the footage.

### 2. Sample frames (agent)
```
python scripts/sample_frames.py footage/<clip>.mp4
```
Extracts 1 fps frames plus scene-change frames. Read them (as images) to
understand each clip: what happens, when, what's worth showing.

### 3. Draft the edit (agent)
Write an edit-decision JSON: an ordered list of shots — source clip, rough
in/out seconds, caption text (one caption per beat; EN/TH or your
languages), and an *anchor description* of the on-screen action the cut
should snap to ("the moment the LED lights", "first keypress"). The precise
schema is documented at the top of `scripts/build_xml.py` — read it and the
reference comments in `scripts/edit_common.py` before writing.

Show the human the shot list (thumbnails + captions) for a veto before
rendering anything — this is the one review checkpoint.

### 4. Refine timing (agent)
```
python scripts/refine_timing.py <edit.json>
```
Motion-diff and audio-onset detection snap each rough anchor to the exact
frame. Calibrate on one shot first (thresholds are footage-dependent);
verify by extracting the anchor frame and looking at it.

### 5. Render captions (agent)
```
python scripts/render_overlays.py <edit.json>
```
Caption PNGs (bundled fonts in `../assets/fonts`, SIL OFL — swap for your
brand). Keep captions short; two languages = two stacked lines or two
passes, per the edit JSON.

### 6. Assemble + import
```
python scripts/build_xml.py <edit.json> --out output/<video>.xml
```
Validates every path/duration before writing. Import into the NLE (creates
a new sequence), human does the taste pass, exports. After manual edits
start, deliver changes as patch XMLs, not full re-imports.

## Notes

- This approach has no voice track by design. If the human wants narration
  over the demo afterward, the simplest upgrade is the voice-over-record
  method in `video-outline-narration` (clip on V1/A1, VO onto A2).
- Music beds are added manually in the NLE (A2) — not generated here.
