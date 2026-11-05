---
name: ae-object-separation
description: Separate a person, product or hand from the background in video footage on the user's own computer with SAM 2, and bring the result into Adobe After Effects through the After Effects MCP server as a frame-accurate track matte - for text or graphics behind the subject, background replacement, outlines and glows. Scans the machine first to pick the right model size. Use when someone wants to separate, isolate, cut out or rotoscope something in footage for an After Effects comp.
---

# Object separation (After Effects)

Separate one subject from the background in a piece of footage, then use it in After Effects: the masks become a matte sequence, and the matte cuts the subject out of the footage on its own layer, so anything can go **behind the subject** (a title, a graphic, a new background) or around it (an outline, a glow). Everything runs on the user's computer; nothing is uploaded. **Load `ae-motion-core` first.**

You write and run the Python as you go. The separation code below is Bart's tested code; adapt it rather than starting from scratch.

## 1. Set up in a folder that can be deleted

Needs Python 3.10+ and ffmpeg. Install into a virtual environment in the project folder, so removing that one folder removes it all:

```
python3 -m venv .object-separation
.object-separation/bin/pip install torch transformers opencv-python-headless pillow numpy
```

On Windows use `.object-separation\Scripts\pip`. With an NVIDIA card on Windows, install the CUDA build of torch from pytorch.org first. Run all the Python below with the venv's python.

**The footage**: find its file path in the AE project with `listFootage` (or `listProjectItems { type: "footage" }`), and its frame rate. The video must be constant frame rate; if not, convert a copy first (`ffmpeg -i in.mp4 -vsync cfr -r 30 out.mp4`) and replace the footage in AE with `replaceFootageFile`.

## 2. Scan the computer and pick the model

Run the scan first and tell the user what it found: the device, the model, the download size, and what speed to expect.

| Machine | Model | Download |
|---|---|---|
| NVIDIA GPU with 12 GB+ | `facebook/sam2.1-hiera-large` | 898 MB |
| NVIDIA GPU under 12 GB, or Apple Silicon | `facebook/sam2.1-hiera-base-plus` | 323 MB |
| No GPU (CPU only) | `facebook/sam2.1-hiera-tiny` | 156 MB |

On a CPU it works but slowly: about 5 seconds per frame, so a 10 s clip at 30 fps takes around half an hour. If the clip is long and there is no GPU, suggest separating only the part the comp actually uses (the layer's in/out range in AE).

```python
# Set these from the user's request. Frame numbers start at 0 (frames of the source file).
VIDEO = "clip.mp4"
START, END = 0, 89              # frames to separate. Click points are picked on the START frame.
PTS = [[480, 270], [100, 60]]   # click points in 960-wide pixels: on the subject first, then on things to leave out
LBL = [1, 0]                    # 1 = this is the subject, 0 = this is NOT the subject
```

```python
import os, platform, subprocess, numpy as np, torch, cv2
from transformers import Sam2VideoModel, Sam2VideoProcessor

print("system:", platform.system(), platform.machine())
if torch.cuda.is_available():
    gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("gpu:", torch.cuda.get_device_name(0), f"{gb:.0f} GB")
    dev, MODEL = "cuda", "facebook/sam2.1-hiera-" + ("large" if gb >= 12 else "base-plus")
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    dev, MODEL = "mps", "facebook/sam2.1-hiera-base-plus"
else:
    dev, MODEL = "cpu", "facebook/sam2.1-hiera-tiny"
print("device:", dev, "| model:", MODEL)
model = Sam2VideoModel.from_pretrained(MODEL).to(dev).eval()     # downloads on first run
proc = Sam2VideoProcessor.from_pretrained(MODEL)
W = 960   # working width. SAM 2 resizes to 1024 itself, so a smaller width is NOT faster.
```

## 3. Pick the click points

Save frame START with a coordinate grid and look at it. Choose two or three points on the subject and add label-0 points on anything that must be left out (fingers holding it, packaging, the table). Show the user what you picked if it is not obvious.

```python
def read_frames(video, a, b):
    cap = cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_FRAMES, a); out = []
    for _ in range(a, b + 1):
        ok, im = cap.read()
        if not ok: break
        out.append(cv2.cvtColor(cv2.resize(im, (W, int(im.shape[0] * W / im.shape[1]))), cv2.COLOR_BGR2RGB))
    return out

def preview(frame, path="work/preview.jpg"):       # frame with a labelled grid, to pick click points
    os.makedirs("work", exist_ok=True)
    im = cv2.cvtColor(read_frames(VIDEO, frame, frame)[0], cv2.COLOR_RGB2BGR)
    for x in range(0, im.shape[1], 80):
        cv2.line(im, (x, 0), (x, im.shape[0]), (0, 255, 255), 1); cv2.putText(im, str(x), (x + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for y in range(0, im.shape[0], 60):
        cv2.line(im, (0, y), (im.shape[1], y), (0, 255, 255), 1); cv2.putText(im, str(y), (2, y - 2), 0, 0.4, (0, 255, 255), 1)
    cv2.imwrite(path, im); return path
```

## 4. Separate the subject

Processed in chunks of 60 frames so memory stays low; each chunk starts from the last mask of the one before. Try a short range first (about 20 frames), check it, then run the full range.

```python
def separate_chunk(frames, points=None, labels=None, mask=None):
    H = frames[0].shape[0]
    s = proc.init_video_session(video=frames, inference_device=dev, video_storage_device="cpu",
                                inference_state_device="cpu", dtype=torch.float32)
    if mask is None:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_points=[[points]], input_labels=[[labels]])
    else:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_masks=mask.astype(np.uint8))
    res = {}
    with torch.inference_mode():
        model(inference_session=s, frame_idx=0)
        for o in model.propagate_in_video_iterator(s, start_frame_idx=0):
            m = proc.post_process_masks([o.pred_masks], original_sizes=[[H, W]], binarize=True)[0]
            res[o.frame_idx] = m.squeeze().cpu().numpy().astype(bool)
    return res

def separate(start, end, pts, lbl, ch=60):
    out, a, seed = {}, start, None
    while a < end:
        b = min(end, a + ch)
        fr = read_frames(VIDEO, a, b)
        r = separate_chunk(fr, points=pts, labels=lbl) if seed is None else separate_chunk(fr, mask=seed)
        for k, m in r.items():
            out[a + k] = m
        seed, a = r[len(fr) - 1], b
    return out

masks = separate(START, END, PTS, LBL)
```

Check a few masks before going on: the start, the middle, and any moment where a hand or object passes in front (overlay the mask on the frame and look). Spill onto something that isn't the subject → add a label-0 point there and run again; part of the subject missing → add a label-1 point.

## 5. Write the matte sequence for After Effects

Full source resolution, soft edge, one PNG per source frame, named so AE imports them as a sequence (white = subject):

```python
def export_mattes(masks, out_dir="work/matte", feather=1.5, grow=0):
    cap = cv2.VideoCapture(VIDEO); w, h = int(cap.get(3)), int(cap.get(4)); fps = cap.get(cv2.CAP_PROP_FPS)
    os.makedirs(out_dir, exist_ok=True)
    for f, m in sorted(masks.items()):
        a = cv2.resize(m.astype(np.uint8) * 255, (w, h), interpolation=cv2.INTER_LINEAR)
        if grow: a = cv2.dilate(a, np.ones((grow, grow), np.uint8)) if grow > 0 else cv2.erode(a, np.ones((-grow, -grow), np.uint8))
        if feather: a = cv2.GaussianBlur(a, (0, 0), feather)
        cv2.imwrite(f"{out_dir}/matte_{f:05d}.png", a)
    return {"dir": os.path.abspath(out_dir), "first": min(masks), "fps": fps, "size": [w, h]}

info = export_mattes(masks); print(info)
```

Masks are hard-edged from SAM 2: very clean on objects and hands, less so on soft hair. `feather` softens the edge in pixels; `grow` (±px) expands or chokes it.

## 6. Use it in After Effects

1. **Import** the first matte file as a sequence: `importFootage { path: ".../matte_00000.png", sequence: true, folderName: "Mattes" }` (use the actual first file name). AE names the item after the prefix (`matte`) and interprets it at 30 fps, so use the `id` from the import result and conform it to the footage's frame rate: `setFootageInterpretation { itemId: <id>, conformFrameRate: <fps> }` (tested: 3 frames at 25 fps → 0.12 s).
2. **Line it up.** In the comp, duplicate the footage layer (`duplicateLayer`, name the copy `<Subject> (cut out)`) and put it above the original. Add the matte sequence (`addFootageToComp`) so its frame `first` lines up with the same source frame: `startTime` = footage layer's start time + `first / fps`. Verify on two frames far apart with `render-frame` (edges sit on the subject, no drift).
3. **Matte it** (AE 2023+): `evalScript` with `cutout.setTrackMatte(matteLayer, TrackMatteType.LUMA)`. The matte layer is hidden automatically and can sit anywhere in the stack (tested on AE 26.5).
4. **Use the cut-out:**
   - **Text or graphics behind the subject**: place the title between the original footage and the cut-out copy. The classic "title behind the speaker".
   - **Background replacement**: hide the original footage and put the new background under the cut-out.
   - **Outline or glow**: on the cut-out layer add Stroke-like outlines with Glow (`ADBE Glo2`) or a duplicate with Fill (`ADBE Fill`) + Simple Choker (`ADBE Simple Choker`, negative choke) + Gaussian Blur underneath.
   - **Highlight like the original skill**: a Fill effect in green at 35 % over the cut-out, plus a thin bright edge.
5. **Check** `render-frame` at the start, the middle and any fast or occluded moment. Hair and motion blur are where a matte shows; a little `feather` helps, a choke of 1–2 px hides halos.

## 7. Clean up (optional)

- the virtual environment: delete `.object-separation`
- the model: delete `~/.cache/huggingface/hub/models--facebook--sam2.1-hiera-*`
- the matte PNGs stay in `work/matte/` (the AE project references them); keep them as long as the project needs them

## Notes

- Anything attached to the subject counts as part of it (packaging, peel-off film): add a label-0 point on it.
- AE's own Roto Brush is the alternative for hair-heavy shots, but it can't be driven by script; SAM 2 can, and gives a reusable matte sequence.
- Only the first run needs the internet, to download the model.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `object-separation` skill (MIT); the separation code in steps 2–4 is his.
