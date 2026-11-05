---
name: video-outline-narration
description: Produce a presenter-led narration video from an outline of key points (no verbatim script). The presenter records demos first and narrates them in the NLE, speaks each talk section naturally, then the agent transcribes, places overlay media against the transcript, and assembles an editable FCP7 XML timeline for Premiere Pro / DaVinci Resolve. Use when the presenter prefers natural ad-lib delivery, when script-writing time isn't available, or when overlay decisions should follow what was actually said.
---

# Outline-Driven Narration Video (v3)

You (the agent) orchestrate this pipeline. The human presenter records; the
bundled scripts do deterministic work; you do the judgment steps: reading
transcripts, deciding what appears on screen when, and writing the edit files.

**The core idea: the spoken transcript is the source of truth.** There is no
script to deviate from. Media is chosen *after* hearing what the presenter
actually said.

## Prerequisites (confirm before starting)

Python 3.10+ with `faster-whisper` and `pillow`; `ffmpeg` on PATH; Chrome or
Edge (for card rendering); an NLE that imports FCP7 XML (Premiere Pro,
DaVinci Resolve). Transcription is compute-intensive: an NVIDIA GPU with
6 GB+ VRAM is recommended (RTX 3070-class ≈ 2× real time); CPU-only runs
at about real time or slower — OK for one validation segment, slow for a
full module.

## Workflow

### 1. Outline (human + agent)
Sections + key points only — never a verbatim script. Tag each section
`[TALK]` (voice leads) or `[DEMO]` (picture leads), with a rough time budget.
Budgets are ceilings, not quotas.

### 2. Demos first (human)
For each [DEMO]: capture the demo clip, then narrate it inside the NLE —
clip on V1/A1, **voice-over record onto A2** while it plays, export as one
file per demo. Setup that matters (Premiere): Preferences ▸ Audio Hardware ▸
Default Input = the mic (a greyed-out VO button means it's "No Input"); OS
mic permission for desktop apps; "Mute input during timeline recording" ON;
headphones. **Every demo is its own segment — never plan a video insert
inside a talk segment**; the builder places stills only on V2.

### 3. Talk sections (human)
One file per section (`m1-01.mp4`, `m1-02.mp4`, …), speaking naturally from
the key points. Fluff protocol: don't stop recording — pause a beat and
re-read the whole sentence. Consistent framing/lighting/mic across sections.

### 4. Transcribe (agent, scripts)
```
python scripts/asr_pass.py <talk clips...> --out analysis/asr
python scripts/repair_gaps.py analysis/asr/<clip>.json ...
```
Rules learned the hard way — do not skip:
- Use the default config (sequential + temperature fallback + **no VAD**).
  Never `--fast` here: with no script to expose gaps, dropped speech is
  invisible. VAD alone has silently eaten 30–90 s of on-camera speech.
- **Always run `repair_gaps.py`** — the decoder can return whole 30-second
  windows empty; re-decoding just the gap recovers them.
- Any remaining "NO WORDS" warning: extract frames from that window and
  LOOK before concluding it's a pause. Low word-probability text can be
  garbled real speech, not hallucination. Never cut on ASR evidence alone.
- Don't transcribe the finished demo segments (mixed demo audio → garbage;
  they need no placements anyway).

### 5. Read + place (agent)
Read every transcript (chunk by pauses, keep timestamps). Then:
- Rewrite the outline **as-built** — what was actually said, per section.
- Build a placement table per talk section: at each moment, either an
  existing asset ("have") or a described request to the human ("need").
  Get the human's veto before producing "need" media.
- Locate cue timestamps by substring-searching the ASR character stream
  (Thai and other unspaced scripts: join word tokens, search, map back).

### 6. Media (agent, scripts)
- **Every overlay is a full-frame 1920×1080 image.** Composite small
  sources (code screenshots, product photos) onto a white canvas:
  `ffmpeg -i src -vf "scale=w=1728:h=972:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white" out.png`
- Text cards: edit the `CARDS` list in `scripts/make_cards.py`, run it.
  Keyword-first, large type — the presenter says the prose.
  Optionally beautify the drafts with an image-gen agent afterward; if you
  do, protect the results with a `CARDS-EXTERNAL.md` sentinel file and
  verify text/glyphs and any depicted hardware (image-gen invents details).
- Pointer arrows (for code walkthroughs): draw onto the composite with
  PIL — line + triangle at the block being discussed, one variant per
  mention. Keep the image up the whole time it's discussed (see `hold`).
- Freeze-frames from the demo clips are free b-roll: `ffmpeg -ss T -i clip
  -frames:v 1 out.png`.

### 7. Assemble (agent, scripts)
Hand-author two JSON files (schemas in `examples/`):
- **align JSON** — one row per segment: `seg`, `title`, `source` (absolute
  path), `speech_in_s`/`speech_out_s` (from first/last real word; head/tail
  pads are added at build), `order` (explicit timeline order), `cues`
  (`{cue, visual, status, confidence, t}` — `t` in source-clip seconds),
  `coverage: 1.0`, `deviations` (notes for the human).
- **overlays manifest** — one row per visual: `{seg, cue, image, kind}` +
  optional `chars` (reading-time dwell) and `hold` (`0` = stay up until the
  next cue — use for code walkthroughs). `image: null, kind: "cam"` means
  "cut back to the presenter".

```
python scripts/build_narration_xml.py analysis/<video>-align.json \
    --out output/<video>.xml --overlays overlays/<video>
```
Validate before delivering: XML parses, every `<pathurl>` exists, segment
order correct, no dropped art in the build report.

### 8. Import + iterate
FCP7 import **always creates a new sequence** — tell the human to finish
choosing rebuilds *before* investing manual edit work, and to export their
edited sequence rather than expecting re-import to preserve it. Mid-clip
pauses are kept (builder trims only head/tail) — the human ripples them out.

**Validate the loop on ONE talk + ONE demo segment before recording the
whole video.** This catches config problems while re-recording costs
minutes, not a day.

## Interleaving talk and demo

To cut from mid-talk into a demo and back: split the talk clip into multiple
align rows sharing the same `source` with different speech spans, and order
them with the `order` key. Cut points go on sentence boundaries (from word
timestamps) — never inside a word. Content after the last span is dropped;
tell the human what was cut.
