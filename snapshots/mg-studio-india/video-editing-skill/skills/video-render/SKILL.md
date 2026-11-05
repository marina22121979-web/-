---
name: video-render
description: Renders a checked composition to the delivery file - HyperFrames render at the platform's resolution and bitrate, BT.709 tags, audio master, structural verify; assembles long-form sections. Use when the user says "render", "export", "make the final", "4K", "assemble", or after notes for a new version.
---

# render

> **Styles:** Canvas sizes and safe zones: `video-take-geometry/references/canvas-safe-zones.md`.

Rendering is the slow, expensive step, so nothing reaches it unchecked, and nothing leaves it unverified.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

## Before rendering

- `npx hyperframes check "$W/hyperframes"` passes and the snapshots were read (the `video-format` skill). A snapshot is seconds; a
  render is minutes.
- The user saw the snapshot sheet at gate 1 or approved a previous version with the same layout.
- Free disk: about 2 x minutes x 0.34 GB for 4K; HyperFrames' frame cache lives in the temp folder.

## One command

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: ALWAYS run `render.py` using the project's virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python.

```bash
"$PROJECT/.venv/bin/python3" "$S/render.py" --public "$W/hyperframes" --out "$W/processed/<project>-v<N>.mp4" \
  --resolution portrait --audio-preset shorts [--denoise auto|strong|neural|off] [--music "$W/music/bed.wav"] [--gpu]
```

It renders with HyperFrames in the most compatible format: **Standard Dynamic Range (SDR) with `--sdr` enabled by default** and adds lossless BT.709 color tags. Never render in HDR by default as HDR triggers gamma shifts, excessive disk consumption, and playback incompatibilities on mobile and web platforms. Masters the audio (`audio-chain.py`: loudness to the
preset, true-peak limit, adaptive/neural noise filtering, ducked music), and runs `verify-render.py` (resolution, tags, bitrate, duration against the
composition, A/V offset, black frames and one-frame flashes) into `$W/processed/<project>-v<N>-VERIFY.md`. Exit 1 means do not
deliver. `--raw FILE` finishes a render made elsewhere. `--denoise auto` (default) automatically applies adaptive multi-band
denoising (`afftdn` + `arnndn`) when background noise exceeds -50 dBFS; `--denoise neural` engages DeepFilterNet3 for car/road noise.

| Platform | `--resolution` | Bitrate | `--audio-preset` |
|---|---|---|---|
| Shorts / Reels / TikTok | `portrait` (or `portrait-4k` from 4K sources) | 12M (45M at 4K) | `shorts` |
| YouTube long-form | `landscape-4k` | 45M | `youtube` |
| Podcast-style long talk | `landscape-4k` | 45M | `longform` |
| Square feed | `square` | 10M | `shorts` |

The composition stays at its authored size; HyperFrames renders at a higher device scale for 4K, so the aspect must
match the preset.

## Long renders

Over about 2 minutes, compose per section and join with `assemble.py` (one master, each section loudness-normalised,
chapters listed); over about 5 minutes of 4K, use segmented capture. The traps that cost renders (black footage under
parallel workers, frame-cache disk use, GPU ignoring CRF) are in `video-motion-graphics/references/kit-motion.md`. A note on a
long render costs a patch, not a re-render: `window-patch.py` renders only the changed window.

## After

Hand the file to `video-review-gate` before the user sees it. Versions keep counting (v2, v3); keep each version's VERIFY,
audio report and ledger. Never hand-edit a master; change the source and render again.
