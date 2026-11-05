---
name: video-rotation-fix
description: Detect and fix videos with rotation metadata that other tools (professional NLEs via FCP XML import, browsers, non-auto-rotating players) ignore. Use when importing phone footage (especially WhatsApp received videos from iPhones), when video appears sideways in your NLE, or when user asks to fix rotation. VERIFY visually before batch processing. Tested with Adobe Premiere Pro.
allowed-tools: Bash Read Glob
---

# video-rotation-fix

Detect rotation metadata in video files (ffprobe Display Matrix) and bake the rotation into the pixel data so tools that ignore the metadata (FCP XML import in professional NLEs, browsers, some editors) display the clip correctly.

**Common trigger**: phone videos from WhatsApp show sideways in your NLE despite being oriented correctly during playback. iPhone videos often store raw pixels as landscape with a `-90°` rotation tag for display.

**Tested NLE:** Adobe Premiere Pro (confirmed to ignore Display Matrix on FCP XML import). Other NLEs that import FCP XML are likely to behave similarly but haven't been verified.

## Critical: verify before batch processing

**Never batch-normalize blindly.** Some files may have incorrect rotation metadata (raw pixels are already correctly oriented, metadata is a bug). Normalizing those would rotate them into the wrong orientation.

Workflow: detect rotated files → extract paired comparison frames → visually confirm which orientation is correct → normalize only files that need it.

## 1. Detect rotation metadata

```bash
ffprobe -v quiet -select_streams v:0 -show_streams -print_format json "clip.mp4" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('streams', []):
    for sd in s.get('side_data_list', []):
        if sd.get('side_data_type') == 'Display Matrix':
            print(sd.get('rotation'))
"
```

Returns the rotation in degrees (e.g., `-90`) if present, nothing if none.

## 2. Extract paired verification frames

For each rotated file, extract one frame WITH auto-rotation (what the file is *supposed* to look like) and one WITHOUT (the raw pixel data). View both with the Read tool and confirm which is upright.

```bash
# Auto-rotated (default ffmpeg behavior — honors Display Matrix)
ffmpeg -y -v quiet -i clip.mp4 -vf "select=eq(n\,30),scale=240:-1" -frames:v 1 autorotate.jpg

# Raw (no rotation applied)
ffmpeg -y -v quiet -noautorotate -i clip.mp4 -vf "select=eq(n\,30),scale=240:-1" -frames:v 1 raw.jpg
```

Then `Read` each `.jpg`. People upright, text readable, horizon horizontal = correct orientation.

If **auto-rotate is correct** (the usual case for WhatsApp/iPhone clips) → proceed to normalize.
If **raw is correct** → the rotation metadata is wrong; you'd use `-noautorotate` and strip the tag instead.

Use frame number `5` if the clip is very short (under 1 second), `30` otherwise.

## 3. Normalize (bake rotation in)

```bash
ffmpeg -y -i clip.mp4 \
  -c:v libx264 -crf 18 -preset fast \
  -c:a copy \
  -metadata:s:v rotate=0 \
  /path/to/normalized/clip.mp4
```

How this works: ffmpeg auto-rotates during decode by default (respects Display Matrix). Re-encoding writes the post-rotation pixels out. Audio is stream-copied (no quality loss). The `rotate=0` metadata strip prevents double-rotation later.

After normalization, the new file has matching pixel dimensions (e.g., `576x1024` instead of raw `1024x576` with `-90°` tag) and no rotation metadata.

## Workflow pattern

1. **Scan** a directory for rotated files (loop `ffprobe` check over all videos)
2. **Report** the list of rotated files to the user
3. **Extract** paired auto/raw frames for each
4. **Verify** visually (Read each pair, confirm auto is correct)
5. **Normalize** verified files into a `normalized/` subdirectory (preserve originals)
6. **Reference** the normalized files from that point on in any downstream pipeline

Keep originals around. Normalization is a re-encode — small quality loss at CRF 18 but not bit-identical.

## Integration with other skills

- Used from `/video-editing` as part of the initial source media inspection — always check rotation when encountering new footage before any editing work.
- Normalized files become the input for `/fcp-xml` (NLEs ignore Display Matrix in FCP XML import — confirmed with Premiere — so normalized files are required).
- Normalized files are also the right input for any `/ffmpeg-editing` operation to avoid compounding rotation confusion.

## Known source of rotated files

- WhatsApp received videos from iPhones: commonly `-90°` in Display Matrix
- Android/iPhone directly-recorded videos when held in portrait mode
- Some screen recorders that capture a rotated display
