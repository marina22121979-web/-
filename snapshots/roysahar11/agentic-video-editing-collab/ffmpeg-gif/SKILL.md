---
name: ffmpeg-gif
description: Generate optimized GIFs from video files using ffmpeg palette optimization. Use for creating GIFs from screen recordings, clips, or animations for documentation, chat, issue attachments, or README embeds. Covers two-pass palette generation for quality and small file size.
allowed-tools: Bash Read
---

# ffmpeg-gif

Convert video to GIF with palette optimization. Two-pass approach (palettegen + paletteuse) produces much better quality and smaller file sizes than direct GIF encoding.

## Single command (two-pass via filter_complex)

```bash
ffmpeg -i input.mp4 \
  -vf "fps=8,scale=400:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  output.gif
```

Key params:
- **`fps=8`** — GIF frame rate. 8-12 is plenty for most documentation. 15+ bloats the file for negligible visual gain.
- **`scale=400:-1`** — width in pixels, preserves aspect ratio (`-1` auto). For README/issue embeds, 400-600px is typical.
- **`max_colors=192`** — palette size. 192 is a good default; drop to 128 for smaller files at some quality loss.
- **`stats_mode=diff`** — palettize based on frame differences (better for screen recordings where most of the frame is static).
- **`dither=bayer:bayer_scale=4`** — Bayer dithering reduces banding. `bayer_scale=3` is sharper but noisier; `5` is smoother but softer.

## Smaller files

For the smallest reasonable GIF:
```bash
ffmpeg -i input.mp4 \
  -vf "fps=6,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  output.gif
```

## Higher quality

For screen recordings with fine text:
```bash
ffmpeg -i input.mp4 \
  -vf "fps=10,scale=600:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
  output.gif
```

## Trim to a segment first

Chain with `trim` or use `-ss`/`-t`:
```bash
ffmpeg -ss 5 -i input.mp4 -t 10 \
  -vf "fps=8,scale=400:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  output.gif
```

## Check file size

```bash
ls -lh output.gif
```

Target: under 5MB for GitHub embeds (hard limit 10MB), under 1MB for Slack/chat pastes.

If too large: reduce `fps`, `scale`, or `max_colors`. Every halving of width quarters the file size approximately.

## When NOT to use GIF

- Video with audio → use MP4 or WebM, not GIF (GIF has no audio)
- Long clips (>15 seconds) → file size explodes; consider MP4
- High-detail footage → GIF's 256-color palette is too limited; use MP4
- Modern platforms that accept video attachments → just send the MP4

## Not for editing workflows

This skill is for **standalone GIF generation** — converting an existing clip or recording to a GIF output. For video editing operations (trim, concat, speed, fade, scale, pad), use `/ffmpeg-editing` instead.
