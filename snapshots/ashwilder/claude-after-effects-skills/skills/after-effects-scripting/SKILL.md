---
name: after-effects-scripting
description: Connect Claude to Adobe After Effects on macOS (no plugin or MCP server needed) and build or edit animation directly inside the live AE session by writing ExtendScript and running it through AppleScript, then verifying the result with renders and frame sheets. Use this whenever the user wants to hook Claude up to After Effects ("connect you to my AE", "подключись к АЕ", "как подключить Claude к афтеру"), or wants Claude to make, change, or check something in AE (a scene, UI animation, kinetic text, a transition, a logo reveal, a mockup, extending comps, batch layer changes, "сделай анимацию в АЕ", "собери сцену в афтере"), even if they don't mention scripting. Prefer it over AE MCP plugins such as aftr, whose fixed command sets can't do shape paths, parenting, text keys or render control.
---

# After Effects scripting

Claude drives the user's running After Effects by writing ExtendScript (`.jsx`) and executing it with `scripts/ae_run.sh`. Nothing is clicked in the UI: a build script creates the comp, layers and keyframes, then Claude renders a preview and looks at frames to verify. The user then refines the result by hand, so what you build must be easy for a human to edit.

## Tools in this skill

| File | What it does |
|---|---|
| `scripts/ae_connect.sh` | First-time setup / connection check. Checks the AE install, the AE setting that lets scripts write files, that AE is running, and a live test script (macOS asks once for Automation permission). Also checks ffmpeg and a private Python venv (`~/.ae-bridge/venv`). Prints OK / FIX lines with the exact fix. |
| `scripts/ae_run.sh <script.jsx> [timeout]` | Runs a script in the running AE. Prepends `lib.jsx`, escapes non-ASCII, prints the result. Pass arguments with `AE_ARGS='{"comp":"X"}'`. Picks the newest installed AE (override with `AE_APP`). |
| `scripts/lib.jsx` | Helpers available in every script: `RUN`, `ARGS`, `freshComp`, `keys`/`springIn`/`springFrom`/`fadeIn`, `shapeLayer`/`rect`/`ellipse`/`strokePath`/`vp`, `txt`/`textKeys`, `place`, `cursorLayer`, `gradientBg`, `softBlur`, `setByType`. Read it once before writing a build script. |
| `scripts/list_project.jsx` | Read-only overview of comps (size, fps, 3D/collapse usage). |
| `scripts/check_comp.jsx` | Counts keyframes/expressions, expression errors, the fonts text layers really use, motion blur, 3D. |
| `scripts/render_preview.jsx` | Renders a comp or a time span to H.264 through the Render Queue (half res by default). |
| `scripts/contact_sheet.py` | Frames of a video in a labelled grid, to look at the animation frame by frame. |
| `references/example_ui_click_scene.jsx` | A complete tested build script: a square UI window where a cursor clicks checkboxes and a button. Copy its patterns. |
| `references/pitfalls.md` | ExtendScript/AE gotchas with fixes. Read it when something behaves strangely. |

## Connecting (first time, or when a run gives no output)

On the first connection, before running anything, give the user a short rundown (4-6 lines, their language, no jargon):
- how it works: Claude writes small scripts, the Mac runs them inside their open After Effects, and Claude checks the result on rendered frames; no plugin;
- what you're about to check: AE installed and open, one AE checkbox, one macOS permission pop-up, ffmpeg + a small private Python environment for looking at renders;
- what they may need to click, and that nothing is installed without asking;
- that you'll build in separate comps and never touch their main timeline unless asked.

Then run `scripts/ae_connect.sh` with After Effects open and walk the user through each `FIX` line in plain words. There are three one-time things, and none of them is a plugin:
1. In AE: **Settings → Scripting & Expressions → Allow Scripts to Write Files and Access Network** (the bridge reads results from a file).
2. macOS pops up "… wants to control Adobe After Effects" on the first run. Click **OK**. If it was denied earlier: System Settings → Privacy & Security → Automation → enable After Effects for the app running Claude.
3. For looking at renders: `brew install ffmpeg`, and a private venv: `python3 -m venv ~/.ae-bridge/venv && ~/.ae-bridge/venv/bin/pip install numpy pillow`. Ask before installing anything.

Run the Python tools with `~/.ae-bridge/venv/bin/python` (or any python3 that has numpy + pillow). On Windows the same scripts run with `AfterFX.exe -r script.jsx`; the runner here is macOS-only.

## Workflow

1. **Look before touching.** Run `list_project.jsx` to see the project. Note whether the user's comps are 3D stacks with Collapse Transformations (then set `AE_OPTS.threeD = true` so new layers match; 2D layers inside collapsed 3D stacks render in the wrong place).
2. **Build in your own comp.** Use `freshComp(name, folder, w, h, fps, dur, bg)` with a clear name in your own folder. Do not modify the user's main timeline or comps they've edited by hand unless they ask; they may be working in AE at the same time. If they ask you to extend an existing comp, change only what was asked and never "rebuild" it from scratch.
3. **Write a build script** in the working folder (e.g. `ae_scripts/scene_x.jsx`) wrapped in `RUN(function(){ ... })` and an undo group. Start from the example. Build layout first (parents at final positions), then all animation.
4. **Run it**: `~/.claude/skills/after-effects-scripting/scripts/ae_run.sh ae_scripts/scene_x.jsx`. A line starting with `ERR` gives the message and line. `WARNINGS` list font fallbacks.
5. **Verify**: `check_comp.jsx` (expect 0 expressions, 0 errors, the intended fonts), then `render_preview.jsx` to an mp4 and `contact_sheet.py` over the interesting ranges. Look at the sheet yourself: misplaced children, hidden elements and wrong timing are only visible there.
6. **Report briefly**: comp name and folder, what happens when (timings), how it's built for editing (parent layer, layer names, which property animates what), and anything you couldn't do.

## How to build (the user's defaults; follow unless told otherwise)

- **Keyframes, not expressions.** Users want to grab keys and change timing/graphs; expressions lock them out. Springs are 3-4 eased keys (`springIn`, `springFrom`), not math. Anchor points are static numbers measured once with `sourceRectAtTime`. `check_comp` should report 0 expressions.
- **No motion blur** on layers or comps unless asked.
- **Parent everything that belongs together** to one layer (e.g. a window/card) so the user can move it as a whole. Name every layer meaningfully (`check 2`, `button text`, `click ripple`).
- **Keep iterations fast.** Half-res previews of only the range you need; never loop long renders to tweak one effect. If something takes more than a minute or two, say so and ask.
- **Fonts**: `txt()` warns when AE substituted a font. Brand/display fonts often lack Cyrillic or other scripts; pick an installed font that supports the text (check with a quick `app.fonts.getFontsByPostScriptName`) and tell the user what you substituted.
- **Clicks and UI**: a click is cursor scale 115 → 98 → 115 over ~0.2 s plus a ripple ring (scale 20 → 150, opacity 70 → 0), and the target reacts 1-2 frames after the press. `cursorLayer()` has its tip at the layer origin, so its position is the click point.

## When things go wrong

- `ERR ... Object is invalid`: you kept a reference to a shape property and then added a sibling. Re-fetch with `vp()`. See pitfalls.
- An element is missing in the render: it's probably drawn behind a later group (add with `onTop`), or its opacity was never keyed up while its parent faded in (opacity is not inherited through parenting).
- Children appear in the wrong place: position them with `place()` while parents are still static; `compPos()` walks the parent chain.
- No output at all: AE is busy, a modal dialog is open, or the script has a syntax error before `RUN`. Ask the user to check AE.
