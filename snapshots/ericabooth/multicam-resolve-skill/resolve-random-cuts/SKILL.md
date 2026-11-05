---
name: resolve-random-cuts
description: >
  Razor every clip on every video track of a DaVinci Resolve timeline at
  randomized marks (gaps uniform between a min and max, default 6-12 s) without
  flattening the stack — each layer keeps its own clips, just pre-broken at the
  same global cut points. Use whenever the user wants to add random cuts,
  breaks, or razor points across a Resolve timeline or multicam stack — e.g.
  "cut all my camera clips every 6-12 seconds", "pre-slice the timeline",
  "add random edit points to all tracks" — even if they don't say "razor".
  Runs via the Resolve scripting API (same connection pattern as
  davinci-resolve-mcp and multicam-resolve-build).
---

# Resolve Random Cuts

Slice the whole timeline stack at random marks so every clip is already a
trimmable, swappable edit — the manual "razor across all tracks every ~10s"
pass, automated. Gap widths are drawn uniformly from `[min-gap, max-gap]`
seconds (default 6–12, average 9), so cuts are never closer than `min-gap`
and never rhythmically even.

## Why it rebuilds instead of razoring

The Resolve scripting API (checked through v21) has **no razor/split call** —
davinci-resolve-mcp doesn't expose one either, because it can't. The reliable
equivalent is a rebuild: read every item's placement (`GetStart/GetEnd`) and
source in-point (`GetSourceStartFrame`), then re-append each clip as ranged
segments split at the global marks (`AppendToTimeline` with
`startFrame/endFrame/trackIndex/recordFrame`). Output goes to a **new
timeline `<name>_CUTS`**; the source timeline is never modified, so a bad run
costs nothing — delete the copy and re-run.

## Prerequisites
- DaVinci Resolve **Studio** running, with the project open and
  Preferences ▸ System ▸ General ▸ *External scripting using* = **Local**.
- Python 3.11–3.12 (NOT 3.14 — Resolve's `fusionscript.so` ABI). No third-party deps.

## Run
```bash
python random_cuts.py --dry-run              # preview marks on the current timeline
python random_cuts.py                        # build <current>_CUTS, 6-12s gaps
python random_cuts.py --timeline "ATX_MAIN" --min-gap 4 --max-gap 9 --seed 42
python random_cuts.py --cut-audio            # razor audio at the same marks too
```

Flags: `--timeline` (default: current), `--min-gap`/`--max-gap` seconds,
`--min-segment` (default 1.0 s — a mark is skipped *on a given clip* if it
would leave a sliver shorter than this), `--seed` (reproducible pattern; the
seed used is always printed), `--suffix` (default `_CUTS`), `--cut-audio`
(default: audio copied whole), `--dry-run`.

Always start with `--dry-run` and show the user the mark count and span
before building.

## What survives the rebuild (be honest with the user)
| Thing | Carried over? |
|-------|---------------|
| Track layout, clip positions, source ranges | ✅ exact |
| Gaps between clips on a track | ✅ preserved |
| Enabled/disabled state, clip color | ✅ |
| Inspector properties (zoom, pan, opacity…) | ✅ copied per segment |
| Color grades | ✅ via `CopyGrades` (18.5+) |
| Transitions | ❌ not in the API — re-add in GUI |
| Titles/generators with no media pool item | ❌ skipped, warned by name |
| Retimed clips (speed ≠ 100%) | ⚠️ appended, but source range math assumes 100% — warned by name, verify in GUI |

## Failure modes
- "Could not connect" → Resolve not running, or scripting pref not Local,
  or Python 3.14 (ABI mismatch).
- `recordFrame offset detected … compensating` is informational: the script
  probes one segment first and self-corrects if this Resolve build interprets
  `recordFrame` relative to the start timecode instead of absolutely.
- Individual `append failed` warnings name the clip and timecode; everything
  else still lands. Common cause: audio track channel-count mismatch — re-run
  without `--cut-audio` if it's audio-only.
