---
name: video-take-geometry
description: Framing decisions - face-safe zones, zooms and punch-ins, camera resets at jump cuts, subject matte for text behind the head, face-tracked reframing to 9:16, 1:1, 4:5 or split-screen halves. Use after every cut and when the user says "zoom in", "make it vertical", "reframe", "text behind me", "split screen", or a card covers their face.
---
# take-geometry

> **Styles:** Camera & footage styles #46-75: `references/styles-camera-footage.md` · canvas sizes and safe zones: `references/canvas-safe-zones.md`.

Measures where the speaker is, once per shot, and turns it into rules: where cards may go, how the camera moves, how to
crop for other aspects without losing the face.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

## 1. Dynamic Framing per Shot

Shot changes: `ffmpeg -v error -i "$W/hyperframes/input-video.mp4" -vf "select='gt(scene,0.12)',metadata=print:file=-" -f null -`.
For each framing (watch sheets or `watch.py focus`), record in `project.json` → `geometry.framings`: face bounding box `[x, y, w, h]`, fixed objects (mic, lamp, desk), card safe zones, and camera transform origins. **All geometry values are calculated dynamically from raw video frames:**

1. **Dynamic Camera Transform Origin:**
   - Derived directly from the speaker's detected face centroid per shot:
     `origin_x = round((cx / W) * 100, 1)%`
     `origin_y = round((cy / H) * 100, 1)%` (typically on eye-line ~30-38% down the head)
   - Eliminates head-cropping during zoom-ins without hardcoded percentage guessing.

2. **Dynamic Card & Graphic Safe Zones:**
   - Measured dynamically from the speaker's detected face/torso bounding box and scene props with adaptive clearance padding (`pad_x = 0.05 * W`, `pad_y = 0.05 * H`):
     - **Speaker Offset Left (`cx < 0.45 * W`):** Graphics safe zone dynamically opens to the right (`x > cx + w/2 + pad_x`).
     - **Speaker Offset Right (`cx > 0.55 * W`):** Graphics safe zone dynamically opens to the left (`x < cx - w/2 - pad_x`).
     - **Speaker Centered (`0.45 * W <= cx <= 0.55 * W`):** Graphics safe zones sit dynamically in the lower third (below speaker chin: `y > cy + h/2 + pad_y`) or side rails.
   - **Strict Visual Clearance Rule:** A graphic card or callout never covers the speaker's face or hands. Content that exceeds available clearance automatically flows to multiple lines rather than encroaching on the speaker.

## 2. Dynamic Camera Dynamics & Motion

Camera transform operations go in the plan's `"camera"` array, anchored to phrase timestamps:

| Move | Dynamic Formulation |
|---|---|
| **Punch-in on emphasis** | `106% - 118%` scale, `0.28s - 0.35s`, `power2.out` (styled by `camera.punch` or video pace) |
| **Slow creep across a thought** | `104% - 110%` over thought duration, `power1.inOut`; resets on the next cut |
| **Zoom-out reveal** | `110% → 100%` over `0.45s` as a lower-third card enters |
| **Every shot change** | Resets cleanly to `100%`; never carry a zoom across a cut boundary |
| **Dynamic Resolution Scaling** | 1080p source: max `112%` punch to avoid pixelation; 4K source: `125% - 150%` freely |

- **Dynamic Drift Compensation:** When zooming with an off-center origin `(ox, oy)`, elements drag by `drift = (scale - 1.0) * (ox - element_pos)`. Compensate dynamically in layout coordinates so overlays stay anchored.
- Jump cuts remain clean unless narrative energy pivots: fast punch (`104% → 100%` over 0.12s) or dynamic angle snap. On long camera-only stretches, alternate subtle zoom levels between jump cuts.

## 3. Resets on the exact jump frame

`cut-map.json` times are not frame-aligned (a reset at the listed time can show a one-frame double cut). Measure, then
let the resolver add the resets:
```bash
"$PROJECT/.venv/bin/python3" "$S/jump-frames.py" --video "$W/hyperframes/input-video.mp4" --cut-map "$W/cut-map.json" --out "$W/jump-frames.json"
"$PROJECT/.venv/bin/python3" "$S/resolve-anchors.py" --plan "$W/storyboard.plan.json" --transcript "$W/transcript.json" \
  --out "$W/storyboard.json" --jump-frames "$W/jump-frames.json"
```
`weak` cuts (same framing both sides): look at the frames before trusting.

## 4. Text behind the speaker (layered-head)

`npx hyperframes remove-background "$W/hyperframes/input-video.mp4" -o "$W/hyperframes/subject-matte.webm" --quality best`
(for one moment, matte a short `ffmpeg -ss -t` excerpt). Layer order inside the camera: footage → text → matte. Check
hair edges, crossing hands and soft 1080p edges in a snapshot; a poor matte means text beside the head, not behind.

## 5. Other aspects (Shorts, feed, split-screen)

```bash
"$PROJECT/.venv/bin/python3" "$S/reframe.py" --video <flat or Short file> --aspect 9:16 --cut-map <its cut-map.json> \
  --out <dir>/reframe-9x16.json --render <dir>/hyperframes/input-9x16.mp4
```

| Need | `--aspect` | Output |
|---|---|---|
| Short / Reel / TikTok | `9:16` | 1080x1920 |
| Square / portrait feed | `1:1` / `4:5` | 1920x1920 / 1536x1920 (or `--size`) |
| Split half, side by side (16:9) / stacked (9:16) | `8:9` / `9:8` | 960x1080 / 1080x960 |

`static` (default): one crop per shot on the median face, for talking. `--mode follow`: dead zone + smoothing, never
gliding across a cut (kept a face crossing at ~275 px/s inside the crop). `--subject left|right` for two people;
`--zoom 1.3` tighter (from 1080p a 9:16 crop is only 606 px wide). It reports faces per shot and fallbacks; under half
the samples with a face, look at the frames; profiles and small faces improve with YuNet
(`face_detection_yunet_2023mar.onnx` from opencv_zoo, in `~/.config/video-skills/models/`). Needs
`pip install 'opencv-python-headless>=4.9,<5'` (OpenCV 5 removed the Haar detector). Screen recordings in a split get a
fixed ffmpeg `crop`, not face tracking. The reframed file becomes that composition's video.

Record framings, origins, matte windows and reframe plans (aspect, mode, face rate) in `project.json`; a new cut makes
`jump-frames.json` and every reframe stale.

## 6. Multi-Layout Framing Geometry & Active Backgrounds (Zero Black Voids)

- **Bottom Split Card (70% Standard):** In 9:16 vertical video, the speaker occupies the bottom ~44% of the canvas (`y = H - h`, ~1075px) with rounded top corners (`border-radius: 24px 24px 0 0`) and upward elevation drop-shadow (`0 -18px 45px rgba(0,0,0,.6)`).
- **Head-Area Focus Crop (Top & Bottom Crop):** Inside the split card, the speaker video is cropped at the top (eliminating dead ceiling headroom) and bottom (cropping out torso/lap) with 1.15x scale and vertical focus centered at 24% ($y \approx 460px$), ensuring the head, eyes, and facial expressions remain prominently visible.
- **Top Split Card (Alternative):** Used when explicitly requested (speaker occupies top 44% with rounded bottom corners `0 0 24px 24px`).
- **Floating Corner Squircle (`pip`):** The speaker is enclosed in a floating corner squircle window (`border-radius: 24px`, glass ring border `rgba(255,255,255,.92)`, drop-shadow `0 18px 50px rgba(0,0,0,.45)`).
- **Studio Mesh Backdrop:** The non-speaker canvas NEVER falls back to an empty black void. It utilizes a deep studio mesh gradient (`radial-gradient(circle at 50% 25%, #1e293b 0%, #0f172a 65%, #020617 100%)`).
- **HyperFrames Motion Canvas:** The opened graphic space above the speaker is filled with active HyperFrames motion scenes (`b_cards`, `b_drawer`, `b_block` proof components, data counters).
