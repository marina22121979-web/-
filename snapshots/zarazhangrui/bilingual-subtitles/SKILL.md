---
name: bilingual-video-subtitles
description: Burn beautiful bilingual subtitles (Chinese over English, or any CJK-over-Latin pair) into a video. Use when the user wants to add hard-coded two-language captions to an .mp4/.mov, subtitle a talk/demo/tutorial in two languages, or asks to "burn subtitles", "加双语字幕", "中英字幕". Renders styled rounded-box captions with Pillow and composites with ffmpeg overlay, so it works even when ffmpeg lacks libass.
---

# Bilingual video subtitles

Burns two-language subtitles into a video: the top language (e.g. Chinese)
in a rounded black box, the bottom language (e.g. English, bold) in a box
just below it, white text, centered or shifted to clear a corner webcam.

**Key trick:** it does NOT use ffmpeg's `subtitles=`/`ass=` filter (many
builds, including Homebrew's slim `ffmpeg`, lack libass). Instead it renders
each caption as a transparent PNG with Pillow and composites them with the
`overlay` filter every ffmpeg build has. This also gives pixel-perfect
rounded boxes and true-bold CJK that libass can't easily match.

Two scripts:

- `scripts/transcribe_align.py` — turns a raw video into word-level-timed
  caption segments (and re-syncs edited captions). Needs `faster-whisper`.
- `scripts/burn_bilingual_subs.py` — the burn engine. Needs only `Pillow` +
  `ffmpeg`/`ffprobe`. No libass, no network, no API keys.

## The workflow (do these in order)

### 1. Get accurate, word-level-timed text

Most users just have a local video with no transcript. Generate one with
accurate timing — **always word-level, never coarse segment timing**, because
segment timestamps drift late during continuous speech and captions end up
lagging the audio more and more.

If the user has a good `.srt`, you may use it, but re-time it against
word-level timestamps (step below) if sync matters.

**a) Transcribe** (auto-detects language, groups into caption units whose
start/end come straight from the first and last word):

```
python3 scripts/transcribe_align.py transcribe --video talk.mp4 --out segments.json
```

This writes `segments.json` (transcript in `bottom`, `top` empty, accurate
times) and `words.json` next to it. For CJK-audio sources, add `--side top`
so the transcript lands in the top slot. Model defaults to `medium`; use
`--model large-v3` for tougher audio, `--model small` for speed.

**b) Clean + translate — edit the TEXT, keep the TIMES.** In `segments.json`:

- Fix any transcription mis-hearings, especially product/proper names
  (e.g. "Clod Code" → "Claude Code", "lizard roe" → "Lissajous").
- Fill `top` with the translation of each `bottom` line (or vice-versa).
  Keep proper names / technical terms in their original language. Ask the
  user which terms to leave untranslated; sensible defaults: brand and
  product names, file formats, UI labels, and known-in-English jargon.
- **Do NOT change `start`/`end` or the number of segments.** Because the
  boundaries came from word-level times, leaving them alone keeps sync tight.

**c) Only if you re-segmented or heavily reworded** (merged/split lines, so
the boundaries no longer match), re-sync against the word times:

```
python3 scripts/transcribe_align.py align --subs segments.json \
    --words words.json --out segments.json --side bottom
```

(`--side` = the language that matches the transcript.) This uses sequence
alignment, so it survives paraphrasing and mis-transcribed proper nouns.

**Skip a mid-video gap** (a clip plays, a long pause): the grouping already
breaks on pauses, so a caption won't linger — just make sure no segment spans
the silent stretch.

### 2. Write the subtitles JSON

Produce a file like `segments.json`:

```json
{
  "segments": [
    {
      "start": 0.02,
      "end": 4.46,
      "top": "中文这一句…",
      "bottom": "The English line."
    },
    { "start": 4.49, "end": 6.08, "top": "下一句…", "bottom": "Next line." }
  ]
}
```

`top` = the language shown on top, `bottom` = the one below. (`zh`/`en` also
accepted.) Times are seconds. Keep segments time-ordered and non-overlapping.

### 3. Show the user the bilingual text for review

```
python3 scripts/burn_bilingual_subs.py md --subs segments.json --out review.md
```

Open `review.md` and let the user correct translations before rendering.

### 4. Choose the layout by LOOKING at the video

Sample 2-3 real frames (`ffmpeg -ss <t> -i video -frames:v 1 f.png`) to see
where on-screen elements sit. If there's a **webcam/PiP in a bottom corner**,
the centered default will overlap it on long lines. Use `--position left`
(or `right`) to shift the caption block into the clear space. Then render
real composited previews (short line + a long/wrapped line):

```
python3 scripts/burn_bilingual_subs.py preview --video V --subs segments.json \
    --position left --t 98  --out prev_long.jpg
python3 scripts/burn_bilingual_subs.py preview --video V --subs segments.json \
    --position left --t 480 --out prev_short.jpg
```

Open them, iterate on style flags until the user is happy, then **reuse the
exact same flags for the burn**. Check `stats` to confirm line counts:

```
python3 scripts/burn_bilingual_subs.py stats --video V --subs segments.json --position left
```

### 5. Burn

```
python3 scripts/burn_bilingual_subs.py burn --video V --subs segments.json \
    --position left --out "OUTPUT - subtitled.mp4"
```

Re-encodes video (libx264, crf 18, audio copied). ~6x realtime on a Mac.
For a long render, run it in the background and report progress.

### 6. Verify, then open

Extract a frame from the FINISHED output (not the source) to prove the
subtitles burned in and timed correctly, then open the file for the user:

```
ffmpeg -ss 98 -i "OUTPUT - subtitled.mp4" -frames:v 1 verify.jpg
open "OUTPUT - subtitled.mp4"
```

## Style flags (all optional; sensible 1080p defaults that scale by height)

- `--position center|left|right` — left/right clears a corner webcam (default center)
- `--reserve PX` — width on the cam side to keep clear (default ~0.255·W)
- `--center-x PX`, `--max-text-w PX` — explicit overrides if presets don't fit
- `--top-size`, `--bottom-size` — font px (default 45 / 41 at 1080p)
- `--top-stroke N` — fake-bold the top (CJK) language to match a bold Latin
  font (default 1; bump to 2 for heavier). `--bottom-stroke` likewise.
- `--box-alpha 0-255` — box opacity (default 200 ≈ 78%)
- `--top-font / --bottom-font [+ --*-font-index]` — override font files
- `--max-lines N` — never wrap past N lines per language (default 3); cues
  that would exceed it, or that would orphan a single word, are auto-split
  into shorter timed cues at a comma/clause boundary.

CJK typography is handled automatically: an embedded Latin word (Claude,
HTML, deck, Markdown…) is treated as atomic and never breaks across lines,
and punctuation never starts a line (it hangs on the previous line, 行首禁则).
The cue splitter likewise never cuts through a Latin word.

- `--min-dur S` — don't split a cue shorter than this (default 1.4s)
- `--crf`, `--preset` — x264 quality/speed for the burn

## Defaults that work well (learned from real use)

- Chinese on top (bold, via `--top-stroke 1`), English bold below.
- Fonts: Hiragino Sans GB (W6) for CJK, Arial Bold for Latin — auto-detected.
- For a talking-head screencast with a bottom-right webcam: `--position left`.
- Keep proper names in the original language inside the translated line.
- Always preview composited frames and get sign-off BEFORE the long burn.
