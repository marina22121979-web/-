---
name: ffmpeg-editing
description: Video editing operations with ffmpeg — trim, concat, speed up / slow down, fade, scale, pad. Use when rendering a preview or final video from a cut list, chaining editing operations, or doing editing ops on individual clips. Covers common pitfalls (setpts + fps for speedup, concat filter vs concat demuxer) and the ffmpeg-full path needed for text/subtitle rendering.
allowed-tools: Bash Read Glob
---

# ffmpeg-editing

Video editing operations with ffmpeg. Inspect before you build. Use the right filter syntax — a wrong pattern silently produces broken output.

## Inspect first

```bash
ffprobe -v quiet -show_entries stream=width,height,r_frame_rate,codec_name \
  -show_entries format=duration -of json "input.mp4"
```

Always know codec, resolution, fps, duration, and rotation metadata before constructing a command. For rotation issues, use `/video-rotation-fix` first — some ffmpeg operations don't honor Display Matrix and produce sideways output.

## Trim

```bash
# Simple trim (fast — no re-encode)
ffmpeg -ss 10 -i input.mp4 -t 30 -c copy output.mp4

# Trim as a filter (needed when chaining with other filters)
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]trim=start=10:end=40,setpts=PTS-STARTPTS[v];[0:a]atrim=start=10:end=40,asetpts=PTS-STARTPTS[a]" \
  -map "[v]" -map "[a]" output.mp4
```

`setpts=PTS-STARTPTS` (and `asetpts`) reset timestamps to zero — otherwise the trimmed clip starts at its original timestamp and throws off downstream concat.

## Concat

**Use the filter, not the demuxer, when you have editing filters in the chain.** The `-f concat` demuxer combined with `-filter_complex` produces broken output.

```bash
# Correct — multi-input concat filter
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 output.mp4
```

The demuxer is fine **only** for stream-copy concat (no filters, no re-encode) of files with identical codec parameters:

```bash
# list.txt contains: file 'clip1.mp4' / file 'clip2.mp4' etc.
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

## Speed (speedup / slowdown)

**`setpts` alone does NOT work.** It changes timestamps but ffmpeg preserves the original frame rate, producing the same duration:

```bash
# WRONG — output duration unchanged
-vf "setpts=PTS/3,scale=..."

# CORRECT — actually speeds up 3x
-vf "setpts=PTS/3,fps=30,scale=..."
```

For slow-motion:
```bash
# 0.5x speed (2x duration)
-vf "setpts=PTS*2,fps=30"
```

For trim + speedup (reset PTS first):
```bash
-vf "trim=start=10:end=40,setpts=PTS-STARTPTS,setpts=PTS/3,fps=30"
```

Audio speed uses `atempo` (range 0.5x–100x per instance, chain for more):
```bash
# 3x audio speed
-af "atempo=3.0"
```

**Don't combine `-r 30` (output fps flag) with `setpts`** — use the `fps=30` filter inside the chain instead. The output flag interferes.

## Scale and pad (fit to target aspect ratio)

To place a source in a different aspect ratio sequence, either crop or letterbox/pillarbox.

```bash
# Portrait source (478x850) into 9:16 sequence (1080x1920) — scale to fill width
scale=1080:-1:flags=lanczos

# Landscape source into 9:16 — scale to fit width, pad top/bottom with dark background
scale=1080:-2:flags=lanczos,pad=1080:1920:0:(1920-ih)/2:color=0x111827

# Opposite: portrait source into 16:9 (1920x1080) — scale to fit height, pad left/right
scale=-2:1080:flags=lanczos,pad=1920:1080:(1920-iw)/2:0:color=0x111827
```

`lanczos` gives the sharpest scale. `-1` or `-2` preserves aspect ratio (`-2` rounds to even pixels, required for H.264).

## Drawbox — masking a region

Paint a solid rectangle over part of the frame — handy for masking a watermark, burnt-in chyron, or garbled AI text before captions go on top.

```bash
# Mask bottom 280px with solid black
-vf "...,drawbox=x=0:y=ih-280:w=iw:h=280:color=black:t=fill"
```

Inside `drawbox` expressions, `w` and `h` refer to the **box being drawn**, not the input frame. Use `iw`/`ih` (or `in_w`/`in_h`) whenever you need input dimensions:

```bash
# Wrong — "h" is the box height (280), so y resolves to 0 → box ends up at TOP of frame
drawbox=x=0:y=h-280:w=w:h=280:color=black:t=fill

# Right
drawbox=x=0:y=ih-280:w=iw:h=280:color=black:t=fill
```

Worse: depending on filter-chain parsing, the wrong expression can make ffmpeg write 0 frames while returning exit 0 (see Silent failures in the Verify section).

`t=fill` fills the rectangle; otherwise `t` is edge thickness in pixels.

## Fade transitions between clips

```bash
# Apply fade-out at end of clip 0, fade-in at start of clip 1:
[0:v]fade=t=out:st=9.5:d=0.5[v0];
[1:v]fade=t=in:st=0:d=0.3,fade=t=out:st=11.5:d=0.5[v1];
[v0][v1]concat=n=2:v=1:a=0[vout]
```

`st` is start time, `d` is duration. Combine with `trim` + `setpts` if you're also cutting.

For **crossfade between clips** (not fade-to-black), use `xfade`:
```bash
-filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=9.5[v]"
```

## ffmpeg-full (extended build)

The standard Homebrew `ffmpeg` is missing text/subtitle filters. For operations requiring `drawtext`, `subtitles`, or `ass` filters (Hebrew subtitle rendering, burned-in captions, text overlays), use the full build at:

```bash
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
```

It's keg-only — won't replace the standard `ffmpeg` in PATH. Includes libass, libfreetype, libharfbuzz, libfontconfig, whisper-cpp.

For Hebrew RTL subtitles, use `ass` filter with `shaping=complex`:
```bash
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -i input.mp4 \
  -vf "ass=subtitles.ass:shaping=complex" output.mp4
```

Note: the `subtitles` filter has a confirmed bug forcing "simple" shaping which breaks Hebrew — use `ass` instead.

## Rendering a preview from an OTIO/FCP XML timeline

When iterating with a timeline destined for an NLE (see `/fcp-xml`), you often want a fast ffmpeg preview without opening the NLE. Approach:

1. Read the OTIO timeline (or parse the FCP XML) to get the clip list with source paths, in/out points, speed values, and any scale adjustments.
2. Generate one ffmpeg command that trims each source, applies per-clip effects, and concats.
3. Render at lower resolution / faster preset for speed (`-s 540x960 -preset ultrafast`).

Example pattern for a cut list:

```bash
ffmpeg \
  -ss 0 -t 3 -i clip1.mp4 \
  -ss 1 -t 3 -i clip2.mp4 \
  -ss 40 -t 8 -i clip3.mp4 \
  -filter_complex "
    [0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[v0];
    [1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[v1];
    [2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[v2];
    [v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]
  " -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 23 \
  preview.mp4
```

`-ss` before `-i` is input seek (fast); `-ss` after `-i` is output seek (accurate but slow). For previews, input seek is fine.

## Verify after every operation

```bash
ffprobe -v quiet -show_entries format=duration,size \
  -show_entries stream=width,height,r_frame_rate -of json output.mp4

# Preview frame
ffmpeg -v quiet -i output.mp4 -vf "select=eq(n\,0)" -vsync vfr -q:v 3 /tmp/preview.jpg
```

Read the preview frame with the Read tool to visually confirm the content.

For long renders, test on a 5-second segment first (`-t 5`).

### Silent failures

ffmpeg can return exit 0 while writing 0 frames — typically when a filter expression is invalid in a way the parser tolerates. Checking `returncode == 0` alone is not enough. Also confirm the output is non-empty and has a real duration:

```bash
test -s output.mp4 && \
  ffprobe -v quiet -show_entries format=duration -of csv=p=0 output.mp4
```

Tell-tale signs in stderr after a "successful" run:
- `Nothing was written into output file, because at least one of its streams received no packets.`
- `Terminating thread with return code -22 (Invalid argument)`

Common culprits: `drawbox`, `drawtext`, and other expression-heavy filters where the parser is lenient about invalid variable references.

## Related skills

- **`/video-rotation-fix`** — normalize rotated source files before editing. ffmpeg's auto-rotate is default ON during decode, but some workflows get confused; normalizing to baked-rotation files avoids ambiguity.
- **`/fcp-xml`** — when ffmpeg previews aren't enough, hand off the same cut list to a professional NLE (Premiere, Resolve, etc.) via FCP XML.
- **`/ffmpeg-gif`** — standalone GIF generation with palette optimization (not for editing).
- **`/video-editing`** — high-level workflow, when to render with ffmpeg vs generate FCP XML, content analysis, platform output specs.
