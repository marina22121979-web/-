---
name: ae-motion-core
description: Foundation for making motion graphics in Adobe After Effects through the After Effects MCP server - how to build comps, layers, cameras and expressions with its tools, a tested expression library (springs, ballistic hops, squash and stretch, camera follow, typing, count-ups, overlap), how to check frames, and how to render drafts and finals with aerender. Load it before any other ae-* skill, or whenever you animate in After Effects with the MCP tools.
---

# After Effects motion core

The other `ae-*` skills describe *what* to make. This one is *how* to make it in After Effects with the MCP tools, so every skill builds, checks and renders the same way.

Requires the After Effects MCP server with the bridge panel open in AE (`bridge-status` reports `connected`). If it reports `busy`, AE is rendering or showing a dialog: wait, don't queue more work.

## The build model

| In a code-rendered video | In After Effects |
|---|---|
| A page that renders any frame from `t` | A comp. Keyframes and expressions are pure functions of `time`, so any frame renders on its own |
| `spring()` / `track()` helpers | Hold keyframes + the **spring-between-keyframes** expression (`reference/expressions.md`) |
| `kf()` eased keyframes | Native keyframes with eased influence (`setKeyframes` with `easeIn`/`easeOut`) |
| A camera wrapper element | A 2D camera rig (world precomp, anchor = follow target, scale = zoom) or a 3D camera |
| Baked simulations | Expressions that look back in time (`valueAtTime`), or `applyValueCurve` to write dense keyframes computed outside AE |
| Seeded random | `seedRandom(index, true)` before `random()`/`wiggle()` |
| Embedded web fonts | Installed fonts (Adobe Fonts or system), chosen by the user in the brief |
| Motion blur by sub-frames | The comp's motion blur switch + each layer's motion blur switch, shutter 180° |

### Tools you will use most

- `buildComposition` creates a comp with all its layers, effects, properties, expressions and keyframes in **one** call and one undo step. Use it for each scene.
- `batch` runs many commands in one round trip; `run-script` runs one.
- `setKeyframes`, `setExpressionByPath` (reports `expressionError`), `setPropertyValue`, `setTextProperties`, `addProperty` (text animators, shape operators), `setShapePath`, `setLayerParent`, `setLayerSwitches`, `updateCompSettings`, `precompose`, `setMarker`/`listMarkers`, `bpmMarkers`.
- Layout: `layoutTextStack`, `fitTextToBox`, `alignLayers`, `distributeLayers`, `setAnchorPoint`, `warpText`, `textOnPath`.
- Inspection: `getLayerProperties`, `searchProperties` (find a property path), `sampleProperty` (numbers at times), `getExpressionErrors`.
- `evalScript` is the escape hatch for anything else (ExtendScript, one undo group).
- `render-frame` returns a frame as an image; `start-render` / `render-status` render the comp in the background with aerender.

Address layers by **name**, and give every layer a clear unique name when you create it (`Title 01`, `Hero`, `CAM TARGET`). Comps also by unique name: duplicate names silently resolve to the first match.

## Before building

1. **Comp settings.** 1920×1080 (16:9) or 1080×1920 (9:16), the frame rate the brief or footage needs (25 or 30; 60 only if asked), duration from the beat sheet. One main comp; each scene a precomp only if it needs its own camera or reuse.
2. **Music first, then the beat grid.** Settle the music in the brief and measure its tempo before animating anything (`librosa.beat.beat_track` on the track, in the `ae-sound-effects` environment). Build the grid at *that* tempo: add `bpmMarkers` to the main comp and put every big change on a beat (one beat = 60/BPM s). A grid only 2.3 BPM off (120 against a 122.3 BPM track) was already about 180 ms off the music by 9.5 s in the Relay example. If the tempo changes after the build, don't re-key everything: put the animation in a precomp, time-stretch that layer (`stretch` = old beat ÷ new beat × 100, rounded to a whole number of frames for loops), scale the main comp's own keyframes and markers by the same factor, and make cross-comp expressions read `valueAtTime(sourceTime(time))`.
3. **Fonts are the user's choice.** Skills never name or pick typefaces; every brief asks. To offer real options, list the installed families with their styles and PostScript names:
   ```
   evalScript { script: "var fams = app.fonts.allFonts, out = []; for (var i = 0; i < fams.length; i++) { var f = fams[i]; if (f && f.length) { var st = []; for (var j = 0; j < f.length; j++) st.push(f[j].styleName + '=' + f[j].postScriptName); out.push(f[0].familyName + ': ' + st.join(', ')); } } out;" }
   ```
   Text layers take the **PostScript name** (`setTextProperties { font: "<PostScriptName>" }`). Before building, confirm each chosen font exists: `app.fonts.getFontsByPostScriptName('<PostScriptName>').length` → `0` means missing, and AE would substitute it silently. If a chosen font is missing, ask the user again (or to activate it in Adobe Fonts); don't swap in one yourself.
4. **Background.** Always put a solid (or gradient) layer at the bottom. `render-frame` output is transparent wherever nothing is drawn, which makes white-on-dark designs look empty.

## Building

- For anything bigger than a few layers, write the build as one ExtendScript file in the project (a `build.jsx` with the beat sheet as a comment at the top) and run it with `evalScript { script: "var DIR = '<folder>'; $.evalFile(new File(DIR + '/build.jsx'))" }`. Make it rebuild from scratch (delete its own project folder first) so every fix is a quick edit and rebuild, and have it return the expression errors it collected. Keep imported assets (footage, the sound mix) **outside** the folder the build deletes. `examples/relay-engaging/` in the MCP repository is a complete example.
- Set expressions that read **other layers** only after those layers exist: an expression that references a missing layer errors, and AE disables it. In a build script, queue those and apply them at the end.
- Put the beat sheet in the main comp as comp markers (`setMarker`), one per moment, comment `scene: …` or `sfx: <type> | <what happens>` (the sound pass reads these).
- Animate with **keyframes for intent, expressions for physics**: keyframes say *where and when*, the expression says *how it moves*. The user can then retime everything in the timeline.
- Every expression from `reference/expressions.md` is tested. Copy it, change only the parameters at its top, and read back `expressionError`.
- Verify motion with numbers before looking at pixels: `sampleProperty` at the beat times (did it land where and when it should? does the overshoot stay in frame?).
- Motion blur: `updateCompSettings { motionBlurSwitch: true, shutterAngle: 180 }` and `setLayerSwitches { motionBlur: true }` on moving layers. It slows renders, so check stills without it and turn it on for the final.
- Text: size it with `layoutTextStack` / `fitTextToBox` instead of guessing font sizes; text is only finished when it fits its box at every frame.
- Keep heavy effects (blurs, glows, Fractal Noise) on as few layers as possible, ideally on precomps or adjustment layers.

## Checking

1. **Stills at the beat times.** `render-frame { compName, time }` for each row of the beat sheet: one time where each state has settled, and a few mid-move. Look at every one. Fix anything clipped, overlapping, unreadable, off-brand, badly framed or empty, and check again.
2. **Contact sheet for motion.** `renderFrames { compName, outputDir, times: [...] }` writes PNGs (they finish writing a moment after the call returns), then `python3 <mcp-repo>/tools/frame_tools.py sheet sheet.png <frames...>` (the `tools/` folder of the After Effects MCP repository; needs Pillow) and look at the sheet. Use it for arcs, spacing and anything that moves fast.
3. **Numbers for timing.** `sampleProperty` around each contact or cue (landed on the beat? settled before the next change?).
4. **Loops**: see the seam check in `reference/expressions.md`.

Claude cannot watch motion in real time, so never say a sequence "looks smooth". Say what you checked (which frames, which numbers) and give the user 3–5 timestamps to watch.

## Rendering

1. **Draft** (review copy). `addToRenderQueue { compName, renderSettingsTemplate: "Draft Settings", outputModuleTemplate: <an H.264 template>, outputPath: ".../draft.mp4" }`, then `start-render`. Draft Settings renders at draft quality, half resolution and without motion blur, so it is fast. `listRenderQueue` lists the output module templates available on this machine (H.264 templates are named like `H.264 - Match Render Settings - 15 Mbps`).
2. **Final.** `Best Settings`, motion blur on, H.264 for delivery or ProRes (`High Quality`, `High Quality with Alpha` for transparent clips) for editing. Tell the user roughly how long it will take before starting long renders.
3. `start-render` renders the **saved project file**: save first (`saveProject`, or pass `saveProject: true`). Poll `render-status` with the job id. AE stays responsive meanwhile, but don't edit and save the project mid-render.
4. Sound: render the final silent, then run `ae-sound-effects` on it.

## Deliver

The AE project (saved, organised: one folder per scene, layers named, markers for every beat), the MP4(s), and a short note: the beat sheet, what is placeholder or illustrative, the fonts used, and one idea for a second version.

## Credits

The video styles in the `ae-explainer-*`, `ae-motion-broll`, `ae-sound-effects` and `ae-object-separation` skills are adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) skills (MIT; see `skills/LICENSE-motion-graphics.md`).
