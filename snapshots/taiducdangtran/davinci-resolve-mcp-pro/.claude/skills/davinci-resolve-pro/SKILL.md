---
name: davinci-resolve-pro
description: >
  Control DaVinci Resolve Studio through the davinci-resolve-mcp-pro server. Use whenever the user
  asks to work with DaVinci Resolve: projects, timelines, media pool, editing/conform, color grading
  and nodes, Fusion compositions, Fairlight audio, captions/subtitles, rendering/delivery, stills, or
  source-safe media analysis. Triggers: "Resolve", "DaVinci", "timeline", "color grade", "node",
  "render", "media pool", "Fusion comp", "subtitles", "conform", "deliver". Default surface is 33
  guarded compound tools; run the server with `--full` for the 341-tool granular API. Pro extras add
  screenshot vision, ffprobe media_inspect, and Fusion node chains.
---

# DaVinci Resolve MCP — Pro

Drive DaVinci Resolve Studio via its official Scripting API. This server merges the proven
samuelgursky base (100% API coverage, source-media safety, control panel, local Whisper) with a
small additive pro layer (screenshot, media_inspect, fusion_node_chain, HTTP/SSE transport).

```
You  <->  MCP  <->  davinci-resolve-mcp-pro  <->  DaVinciResolveScript  <->  DaVinci Resolve Studio
```

## Before you start
- **Resolve Studio** must be installed (the free edition has no external scripting).
- **Preferences → System → General → "External scripting using" = Local**.
- The server auto-launches Resolve if it is not running — the first call can take up to ~60s.
- If a tool returns a connection error, Resolve isn't installed or scripting is disabled.

## Two tool surfaces
- **Compound (default, 33 tools).** Each tool takes an `action` + `params` and dispatches many
  operations, with **guarded workflows**: `*_capabilities` → `probe_*` → `safe_*`/`validate_*` →
  boundary report. Destructive actions are version-on-mutate protected and may require a
  `confirm_token` (preview first, then re-call with the token). Prefer this surface.
- **Granular (`--full`, 341 tools).** One tool per Resolve API method. Use when you need a specific
  low-level call. The reference tables below use these names.

## Core concepts
- **Response shape:** tools return JSON; treat `success: false` / an `error` field as a failure and
  recover, don't retry blindly.
- **Object handles / registry:** Resolve objects aren't serializable. Get a parent → it returns an
  id/handle → pass that to child calls. If a handle goes stale, re-fetch from the parent.
- **Page prerequisites:** some operations require the right page — Color page for grading/stills,
  Fairlight for audio, Fusion for comps. Switch pages first.
- **Source-media safety:** the server never transcodes/overwrites your camera originals; analysis
  writes only to sidecars/reports, and project/timeline mutations are archived before the change.

## Pro tools (additive)
- **`screenshot`** — capture the Resolve UI so you can *see* current state. Call before/after visual
  changes or when the user describes something on screen. Image goes to the AI provider — use when a
  visual check is genuinely needed. (macOS targets the Resolve window; other OSes capture full screen.)
- **`media_inspect(path)`** — fast ffprobe probe: codec, resolution, exact fps (+ integer timebase),
  duration, embedded start timecode (+ frame count), audio layout. Use before importing/conforming or
  to verify a delivery spec. Needs `ffprobe` (ffmpeg) on PATH.
- **`fusion_node_chain(nodes, connect_sequentially=True)`** — build & wire a Fusion node graph on the
  current timeline item's comp in one call. For fine control use the granular Fusion/graph tools.

## Remote transport
The server is stdio by default. For remote/phone control run it with `--transport sse` or
`--transport http` (binds 127.0.0.1 by default). It has **no auth** — only expose it via an
authenticated tunnel/reverse proxy, never raw on an untrusted network.

## Reference material (read when relevant)
- `references/render_settings.md` — render/export keys, format/codec, timeline-item transform/retime enums.
- `references/fusion_tools.md` — Fusion node types + input tables + wiring patterns (lower-third, etc.).
- `references/workflows.md` — end-to-end id-chaining recipes (import→build→render, captions, color, Fusion title).
- `references/ffmpeg_workflows.md` — ffmpeg recipes that complement Resolve (silence cut, normalize, stream map).
- `scripts/find_sounds_fast.py` — numpy FFT cross-correlation sound-match helper (`pip install '.[audio]'`).

## Gotchas
- Always confirm the active project/timeline before mutating; never assume.
- For destructive compound actions, do the preview call, surface what will change, then re-call with
  the `confirm_token`.
- Lua `print()` output isn't captured by the bridge — it goes to Resolve's Console.
- `media_inspect` reads the file header, independent of what Resolve thinks — trust it over guesses.
