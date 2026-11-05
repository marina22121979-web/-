---
name: video-editor
description: Cut, caption, and assemble vertical video with ffmpeg
version: 1.0.0
---

## What it does
Takes a source video and produces a vertical (9:16) cut with burned-in
captions. Output is a single H.264/AAC file ready for short-form platforms.

## Prerequisites
- `ffmpeg` and `ffprobe` on `PATH`
- Read access to `~/workspace/input`
- Write access to `~/workspace/output`

## Verify environment
Run this before anything else:

    command -v ffmpeg && command -v ffprobe

If either is missing, stop and report: `MISSING_DEP: ffmpeg`. Do not attempt a
fallback encoder.

## Steps
1. Confirm the source exists:

       test -f ~/workspace/input/source.mp4

   If it does not exist, report `MISSING_INPUT: ~/workspace/input/source.mp4`.

2. Probe the dimensions before touching the file:

       ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
         -of csv=p=0 ~/workspace/input/source.mp4

3. Ensure the output directory exists:

       mkdir -p ~/workspace/output

4. Run the cut:

       bash scripts/cut.sh ~/workspace/input/source.mp4 ~/workspace/output/final.mp4

5. Confirm the result is a real file and report its path and size:

       ls -lh ~/workspace/output/final.mp4

## Never assume
- Never assume the input is already 9:16 — always probe first.
- Never assume `~/workspace/output` exists — `mkdir -p` it.
- Never overwrite an existing output without confirming with the user first.
- Never assume the source has an audio track — check with
  `ffprobe -select_streams a -show_entries stream=codec_type -of csv=p=0`.

## Output
`~/workspace/output/final.mp4` — H.264, 1080x1920, AAC audio, `-crf 20`.

## Failure handling
- `ffprobe` fails → the file is not valid video. Report `BAD_INPUT`.
- `cut.sh` exits non-zero → surface its stderr verbatim. Do not retry blindly.
- Output is 0 bytes → report `EMPTY_OUTPUT` and stop.
