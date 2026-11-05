---
name: adobe-after-effects-mcp
description: Practical guide for creating, editing, animating, compositing, keying, masking, tracking, applying effects, and exporting Adobe After Effects projects through an After Effects MCP bridge. Use when Codex needs to operate Adobe After Effects via MCP tools, plan AE compositions, automate layers/keyframes/effects, troubleshoot the after-effects-mcp bridge, or translate video-editing/VFX requests into concrete After Effects actions.
---

# Adobe After Effects MCP

Use this skill to act as an After Effects operator through MCP: create compositions, build layers, animate properties, apply effects, and guide the user through manual-only AE steps when the current MCP surface cannot do them directly.

This skill is self-contained. Treat the sections below as direct operating instructions for After Effects work. Read and apply the relevant blocks from this file itself before using the After Effects MCP tools or giving AE UI instructions.

## First Move

1. Confirm the bridge is usable: After Effects must be open, the `mcp-bridge-auto.jsx` ScriptUI panel must be open, and auto-run/listening must be enabled.
2. Use `mcp__AfterEffectsMCP__.get_help` when the session state or available scripts are unclear.
3. Use `run_script` for read-only discovery first, usually `getProjectInfo`, `listCompositions`, or `getLayerInfo`.
4. After each bridge command, call `get_results` when the tool does not directly return enough detail.
5. Treat stale results, no result, or timeouts as bridge-state issues before assuming the AE operation failed.

## Operating Principles

- Build AE work as compositions first: dimensions, frame rate, duration, background/alpha intent.
- Keep projects organized: use folders such as `Footage`, `Audio`, `Comps`, `Precomps`, `Graphics`, `Solids`.
- Prefer non-destructive layer stacks: duplicate/precompose before aggressive effects, keying, rotoscope, or multi-effect treatments.
- Use keyframes as the universal animation language: position, scale, rotation/orientation, opacity, mask path, and effect parameters.
- Stack simple effects to make polished results: e.g. text + warp + drop shadow + light sweep + sound effect.
- When MCP cannot create a manual AE feature directly, either use the closest exposed MCP tool or give precise AE UI instructions for the user to complete.
- Save/check frequently. After Effects can become slow with many high-resolution clips, 3D layers, Roto Brush, Warp Stabilizer, or heavy effects.

## MCP Action Pattern

Use the exposed MCP tools directly when possible:

```json
{
  "tool": "create_composition",
  "args": {
    "name": "Main_1080p_30",
    "width": 1920,
    "height": 1080,
    "frameRate": 30,
    "duration": 10,
    "backgroundColor": { "r": 0, "g": 0, "b": 0 }
  }
}
```

Then create/query layers with `run_script` when needed, set keyframes with `setLayerKeyframe`, set expressions with `setLayerExpression`, and apply effects with `apply_effect` or `apply_effect_template`.

For robust animation, set at least two keyframes and easy-ease manually when the MCP surface cannot set interpolation. If direct interpolation is unavailable, tell the user to select keyframes in AE and use `Keyframe Assistant > Easy Ease`.

## Choosing Techniques

- Need a quick edit, title, or logo animation: use the Shapes, Text, And Animation instructions and Practical Recipes.
- Need cinematic or stylized treatment: use the Effects And Presets instructions, then stack effects conservatively.
- Need to remove green/solid backgrounds: use the Green Screen / Chroma Key workflow in Keying, Masking, Rotoscoping, Tracking.
- Need to isolate a moving subject: prefer Roto Brush for complex organic shapes; prefer animated masks for hard-edged objects or transitions.
- Need text/logo to follow footage: use the Motion Tracking workflow, then parent the target layer to a null.
- Need reusable overlays: build on transparency and export with alpha using the Export Recipes instructions.

## Quality Bar

Before finishing, verify:

- Composition settings match the delivery target or source-media intent.
- Layers are named enough to understand the stack.
- Keyframes start/end at the intended moments and the work area is trimmed with an out point.
- Visual elements stand out using contrast, shadow, glow, or color grade without looking pasted on.
- Heavy effects are previewed at lower resolution when needed, but final render settings remain correct.
- Exports use H.264 for normal video, QuickTime Animation + Alpha for transparent overlays, or PNG/JPEG sequence for still frames.

## MCP Bridge Instructions

How to apply this block:

- Apply this block at the start of any After Effects MCP session, whenever a command fails, or whenever you need to know which MCP tool/script to use.
- Use the architecture notes to reason about stale results and bridge state before diagnosing an AE operation as failed.
- Prefer the listed callable tools and effect match names exactly, because they are more reliable than display names.

# MCP Bridge

Use this block when operating the `after-effects-mcp` server or troubleshooting the connection to After Effects.

## Architecture

The server is a file-bridge integration, not a direct live AE API:

1. The MCP client sends a tool call to the Node server.
2. The server writes a JSON command into the bridge directory, typically under the user's Documents folder.
3. The `mcp-bridge-auto.jsx` panel inside After Effects polls for commands.
4. After Effects executes ExtendScript and writes a JSON result.
5. The MCP server reads the result back.

Consequences:

- After Effects must be open.
- The bridge panel must be open from `Window > mcp-bridge-auto.jsx`.
- Auto-run/listening must be enabled in the panel.
- Results can be stale if the panel did not process the latest command.
- Some operations are limited to allowlisted scripts or exposed MCP tools.

Repository: https://github.com/Dakkshin/after-effects-mcp

## Setup Checklist

1. Install dependencies in the MCP repo:

```powershell
npm install
npm run build
npm run install-bridge
```

2. If bridge install fails, manually copy `build/scripts/mcp-bridge-auto.jsx` into the After Effects `Scripts/ScriptUI Panels` folder.
3. In After Effects, enable scripting permissions:
   - `Edit > Preferences > Scripting & Expressions`
   - Enable script file/network access.
4. Restart/open After Effects.
5. Open `Window > mcp-bridge-auto.jsx`.
6. Confirm the panel is checking for commands.

## Tool Surface In This Codex Session

Prefer these callable MCP tools when available:

- `mcp__AfterEffectsMCP__.get_help()`
- `mcp__AfterEffectsMCP__.get_results()`
- `mcp__AfterEffectsMCP__.run_script({ script, parameters? })`
- `mcp__AfterEffectsMCP__.create_composition({ name, width, height, frameRate?, duration?, pixelAspect?, backgroundColor? })`
- `mcp__AfterEffectsMCP__.setLayerKeyframe({ compIndex, layerIndex, propertyName, timeInSeconds, value? })`
- `mcp__AfterEffectsMCP__.setLayerExpression({ compIndex, layerIndex, propertyName, expressionString })`
- `mcp__AfterEffectsMCP__.apply_effect({ compIndex, layerIndex, effectName?, effectMatchName?, effectCategory?, effectSettings?, presetPath? })`
- `mcp__AfterEffectsMCP__.apply_effect_template({ compIndex, layerIndex, templateName, customSettings? })`

The current template names are:

- `gaussian-blur`
- `directional-blur`
- `color-balance`
- `brightness-contrast`
- `curves`
- `glow`
- `drop-shadow`
- `cinematic-look`
- `text-pop`

## Discovery Scripts

Use `run_script` for project inspection and supported operations. Common script names from the bridge help/repo include:

- `getProjectInfo`
- `listCompositions`
- `getLayerInfo`
- `createComposition`
- `createTextLayer`
- `createShapeLayer`
- `createSolidLayer`
- `setLayerProperties`
- `setLayerKeyframe`
- `setLayerExpression`
- `applyEffect`
- `applyEffectTemplate`
- `deleteLayer`
- `setLayerMask`
- `bridgeTestEffects`

Example:

```json
{
  "script": "listCompositions"
}
```

## Common Calls

Create a composition:

```json
{
  "name": "Title_Intro_1080p",
  "width": 1920,
  "height": 1080,
  "frameRate": 30,
  "duration": 8,
  "backgroundColor": { "r": 0, "g": 0, "b": 0 }
}
```

Set layer keyframes:

```json
{
  "compIndex": 1,
  "layerIndex": 1,
  "propertyName": "Opacity",
  "timeInSeconds": 0,
  "value": "0"
}
```

```json
{
  "compIndex": 1,
  "layerIndex": 1,
  "propertyName": "Opacity",
  "timeInSeconds": 0.75,
  "value": "100"
}
```

Apply a reliable effect by match name:

```json
{
  "compIndex": 1,
  "layerIndex": 1,
  "effectMatchName": "ADBE Gaussian Blur 2",
  "effectSettings": { "Blurriness": 25 }
}
```

Apply a template:

```json
{
  "compIndex": 1,
  "layerIndex": 1,
  "templateName": "text-pop"
}
```

Set an expression:

```json
{
  "compIndex": 1,
  "layerIndex": 1,
  "propertyName": "Position",
  "expressionString": "wiggle(2, 20)"
}
```

## Effect Match Names

Prefer `effectMatchName` over display names when possible:

- Gaussian Blur: `ADBE Gaussian Blur 2`
- Camera Lens Blur: `ADBE Camera Lens Blur`
- Directional Blur: `ADBE Directional Blur`
- Radial Blur: `ADBE Radial Blur`
- Unsharp Mask: `ADBE Unsharp Mask`
- Brightness & Contrast: `ADBE Brightness & Contrast 2`
- Hue/Saturation: `ADBE HUE SATURATION`
- Levels: `ADBE Pro Levels2`
- Curves: `ADBE CurvesCustom`
- Exposure: `ADBE Exposure2`
- Vibrance: `ADBE Vibrance`
- Glow: `ADBE Glow`
- Drop Shadow: `ADBE Drop Shadow`
- Bevel Alpha: `ADBE Bevel Alpha`
- Noise: `ADBE Noise`
- Fractal Noise: `ADBE Fractal Noise`
- CC Light Sweep: `CC Light Sweep`
- CC Particle World: `CC Particle World`

## Troubleshooting

If a command seems ignored:

1. Confirm After Effects is open.
2. Confirm `Window > mcp-bridge-auto.jsx` is open.
3. Confirm the bridge panel is auto-running commands.
4. Call `get_results`; if stale, the panel probably did not process the latest JSON.
5. Check scripting permissions in After Effects.
6. Check that the MCP server and AE panel use the same bridge directory.
7. Try `run_script({ "script": "getProjectInfo" })` or `bridgeTestEffects`.
8. Restart the MCP server and reopen the AE panel if file polling appears stuck.

If an operation is not exposed:

- Use available MCP tools for the mechanical parts.
- Give the user precise AE UI steps for manual-only operations such as Roto Brush refinement, Warp Stabilizer analysis, Easy Ease, or Media Encoder export.
- Use `run_script` only with allowlisted script names.

## Workflow Basics Instructions

How to apply this block:

- Apply this block whenever creating or organizing AE projects, choosing comp settings, importing assets, trimming footage, editing to audio, or explaining manual AE fundamentals.
- Use the composition and organization rules before building layers, so the resulting project remains clear and deliverable.
- Use the keyframe patterns and shortcuts as the default manual fallback when MCP cannot expose a given UI action directly.

# Workflow Basics

Use this block for core After Effects operating patterns from the course: layout, importing, compositions, layer properties, keyframes, organization, and editing fundamentals.

## Workspace Mental Model

- Project/Media panel: imported footage, audio, graphics, compositions, precomps.
- Composition viewer: live preview of the active comp.
- Timeline/layers: layer order, trimming, keyframes, masks, transform properties.
- Effects & Presets: effects, animation presets, visual/audio processing.
- Preview panel/spacebar: playback. Use lower preview resolution (`Half`, `Third`, `Quarter`) when playback lags.

If panels get rearranged, use `Window > Workspace > Reset to Saved Layout`.

## Composition Setup

Create compositions in one of three common ways:

- `Composition > New Composition`
- New composition button in the Project panel
- Drag footage onto the new composition button to match the source settings

Common settings:

- 1920x1080, 29.97/30 fps, black background for general 1080p work.
- 1080x1080 for square social content.
- 1280x720 when intentionally editing 1080p footage in a 720p comp to gain framing room without scaling above 100%.
- Match source fps/duration when the goal is a direct edit of a clip.
- Use transparency grid when creating overlays, lower thirds, stingers, or alpha exports.

Course heuristic: when source footage is higher resolution than the delivery comp, frame by scaling down or repositioning instead of scaling above 100%. Scaling above source quality softens the image.

## Importing and Organization

Import by drag/drop or `File > Import > File`.

Keep the project panel organized early:

- `Footage`
- `Audio`
- `Comps`
- `Precomps`
- `Graphics`
- `Solids`

Rename comps from camera/file names to intent names such as `Comp_Intro_Title`, `Comp_GreenScreen_Key`, or `Main_Edit`.

## Essential Shortcuts

- `Ctrl+S`: save constantly.
- `V`: selection tool.
- `H`: hand/pan tool.
- `Z`: zoom tool.
- `W`: rotation tool.
- `Q`: shape tool.
- `G`: pen tool.
- `Ctrl+T`: text tool.
- `Ctrl+Shift+D`: split layer at playhead.
- `Ctrl+D`: duplicate selected layer.
- `Ctrl+Z`: undo.
- `S`: scale property.
- `P`: position property.
- `R`: rotation property.
- `T`: opacity property.
- `L`: audio levels.
- `LL`: waveform.
- `M`: mask properties.
- `B`: set work-area start.
- `N`: set work-area end.
- Hold `Shift` while resizing to constrain proportions or snap/lock movement.
- Hold `Y`/use Pan Behind tool to move the anchor point.

## Layer Properties

Use transform properties deliberately:

- Anchor Point: pivot for rotation/scale. Center it unless the animation needs an off-center pivot.
- Position: precise X/Y placement; use keyframes for movement.
- Scale: preserve quality by staying at or below 100% unless source resolution allows more.
- Rotation/Orientation: animate spins, tilts, 3D rotations.
- Opacity: fades, flickers, reveals.

For shapes, distinguish:

- Layer transform: transforms the whole layer.
- Shape contents transform: transforms a path/group inside the shape layer.

## Keyframe Basics

Keyframes store property values at times. AE interpolates between them.

Typical structure:

1. Move playhead to the desired end state.
2. Enable the stopwatch for a property.
3. Move to the start state.
4. Change the property.
5. Preview and adjust timing.
6. Select keyframes and apply Easy Ease when smoothness matters.

Common patterns:

- Fade in: opacity 0 -> 100.
- Fade out: opacity 100 -> 0.
- Slide in: position offscreen -> final position.
- Pop in: scale 0 -> 100 or 85 -> 105 -> 100.
- Camera shake imitation: alternating rotation/position keyframes, then Easy Ease.
- Effect pulse: animate brightness/contrast, glow intensity, lens size, light sweep intensity.

## Editing To Audio

Use `LL` to open waveform. For beat cuts:

1. Import video and music.
2. Open audio waveform.
3. Split video on waveform peaks with `Ctrl+Shift+D`.
4. Delete middle sections.
5. Hold `Shift` while dragging clips together to snap.
6. Add text or title at the final beat if useful.

This creates perceived sync even when beats are subtle, because cuts align with repeated waveform events.

## Preview Performance

Use these before blaming the project:

- Drop viewer resolution to `Half`, `Third`, or `Quarter`.
- Trim work area to the active section with `B`/`N`.
- Precompose heavy sub-stacks.
- Work in a fresh project for very heavy Roto Brush/glow/3D tests.
- Render previews before judging timing.

## Shapes, Text, And Animation Instructions

How to apply this block:

- Apply this block for shape layers, solids, custom paths, text design, title animation, 3D shape/text work, lower thirds, and intro stingers.
- Use the selection rules before drawing, because the same tool can create a shape or a mask depending on what is selected.
- For reusable motion graphics, combine shape/text construction with alpha export instructions from the Export Recipes block.

# Shapes, Text, And Animation

Use this block for shape layers, solids, custom paths, 3D layers, text/title work, intro stingers, and lower thirds.

## Shapes And Solids

Shape tool behavior depends on selection:

- If no layer is selected, drawing creates a new shape layer.
- If a footage/solid layer is selected, drawing creates a mask on that layer.
- If a shape layer is selected, drawing adds another shape inside the same layer.

Basic shape tools:

- Rectangle / rounded rectangle
- Ellipse / circle when holding `Shift`
- Polygon
- Star

Use fill/stroke controls to style shapes. Stroke is an outline; fill is the interior. For clean motion graphics, keep fill/stroke choices simple and add depth with shadows, glow, or light sweep only when needed.

## Custom Shapes

Use the Pen tool (`G`) for custom shapes:

1. Deselect all layers if you want a new shape layer.
2. Click points around the intended object.
3. Hold `Shift` for straight or constrained lines.
4. Close the path by clicking the first point.
5. Adjust points after drawing.

Use custom shape layers instead of masked solids when you need fill/stroke color to remain easily editable.

## Shape Effects

Open shape layer `Contents`, select the shape/group, then use `Add`:

- Repeater: duplicate arrows, hazard marks, pattern rows.
- Trim Paths: reveal outlines over time.
- Twist: twist path geometry.
- Zig Zag: jagged or wavy outline.
- Pucker & Bloat: curve or flower-like deformation.
- Round Corners: soften hard paths.

Repeater recipe:

1. Draw one arrow/mark.
2. Add `Repeater`.
3. Set copies to the desired count.
4. Adjust repeater transform position/offset.
5. Edit the original path; repeated copies update automatically.

## 3D Shapes

For real 3D shape/text extrusion:

1. Set the comp renderer to Cinema 4D when extrusion is needed.
2. Create a shape/text layer.
3. Enable the 3D layer switch.
4. Open `Geometry Options`.
5. Increase `Extrusion Depth`.
6. Add `Layer > New > Light` so depth/shadows are visible.
7. Rotate with 3D orientation/rotation properties.

Use lower preview resolution while working. Extruded 3D is heavier than normal 2D layers.

Fake 3D:

- Use `CC Sphere` on a flat map/image to create a globe.
- Use `CC Cylinder` for wrapped cylinder-like media.
- Animate effect rotation/radius instead of true 3D geometry when speed matters.

## Text Basics

Create text with:

- `Ctrl+T`, click in comp, type.
- `Layer > New > Text`.
- Right-click timeline > `New > Text`.

Style in Character/Paragraph panels:

- Font and style family
- Fill and stroke color
- Font size
- Tracking/letter spacing
- Horizontal/vertical scaling
- Faux bold/italic, all caps, small caps, superscript/subscript
- Paragraph alignment

Set the text anchor point to the visual center before scaling/rotating.

## Animated Titles

Manual title animation:

1. Press `P`, `S`, `R`, or `T` depending on desired motion.
2. Set the final state first.
3. Set the start state offscreen, smaller, rotated, or transparent.
4. Easy Ease the keyframes.
5. Add a subtle ongoing scale movement if the title would otherwise feel static.

Animation presets:

- `Animation > Apply Animation Preset`
- Useful folders: text animate-in/out, movement transitions, behaviors, backgrounds.
- Presets save time but reduce precision. Use manual keyframes when the exact path/timing matters.

Common title stack:

- Main title uses preset such as slow fade on.
- Subtitle uses manual opacity fade.
- Both layers share a slow scale-up.
- Both fade out near the end.

## Text Effects

Text animator effects:

1. Open text layer.
2. Use `Animate`.
3. Add Fill Color, Stroke Color, Skew, Tracking, Position, Scale, etc.
4. Keyframe animator values.

Color pulse recipe:

- Add Fill Color RGB and Stroke Color RGB.
- Start with fill A / stroke B.
- At 2s swap to fill B / stroke A.
- Copy/paste alternating keyframes.

Video inside text:

1. Put video layer below text.
2. Set the video layer Track Matte to Alpha Matte using the text layer.
3. Precompose the video+text pair if applying shadows to the combined result.
4. Apply Drop Shadow to the precomp for a solid shadow.
5. Keep text large/bold so the video is readable inside letters.

Write-on text:

1. Create text.
2. Apply `Write-on`.
3. Set brush size large enough to cover each letter stroke.
4. Set paint style to reveal original image.
5. Keyframe brush position along the letter paths.
6. For video-inside-text write-on, precompose the matte result and apply Write-on to the precomp.

## Lower Third Recipe

1. Create rounded/rectangular shape bars in the lower third.
2. Precompose shape bars if masking them as a unit.
3. Use a diagonal mask with feather to wipe bars on.
4. Add name and secondary line text.
5. Precompose text and mask it on from the opposite direction.
6. Add Drop Shadow to the shape/text group.
7. Copy/paste and reverse mask keyframes to animate out.
8. Export with alpha if the lower third must be reused.

## Intro Stinger Recipe

1. Decide final frame first: logo/name plus backing shape.
2. Build shape elements around the logo/name.
3. Animate shape scale from 0 and rotation into final state.
4. Animate text with a preset or manual scale/opacity.
5. Add subtle wiggle/rotation only if it fits the brand.
6. Add shadows/glow sparingly.
7. Trim work area to the stinger length.
8. Export with alpha for reuse over video.

## Effects And Presets Instructions

How to apply this block:

- Apply this block when choosing, stacking, animating, or troubleshooting effects, color correction, distortion, generated backgrounds, audio effects, visualizers, and stylized looks.
- Use effect stacks instead of relying on one effect to finish the shot.
- Use adjustment layers and precomps when an effect must affect multiple clips or a combined result.

# Effects And Presets

Use this block for effect selection, effect stacking, color correction, audio effects, visualizers, light effects, generated backgrounds, and distortions.

## General Effect Strategy

- Effects are rarely final by themselves. Stack simple effects until the shot feels integrated.
- Animate effect parameters with keyframes for transitions and pulses.
- Use adjustment layers for effects that should apply to multiple clips.
- Precompose when a shadow/glow/matte should apply to a combined result instead of individual child layers.
- Use preview at lower resolution while tuning heavy effects.

## Animation Presets

Access through:

- `Animation > Apply Animation Preset`
- Effects & Presets > `Animation Presets`

Useful folders:

- `Text`: animate-in/out, behaviors, fades, optical effects.
- `Transitions - Movement`: stretch/blur, slide, zoom spiral, swoop.
- `Behaviors`: wiggle position, wiggle scale, wiggle rotation, opacity flashes.
- `Backgrounds`: generated animated backgrounds from solid layers.

Presets can be copied/reversed by copying generated keyframes and swapping their order.

## Blur And Sharpen

Common uses:

- Gaussian Blur: simple softening, background defocus.
- Directional Blur: motion blur feel.
- Radial Blur: spin/zoom blur.
- Vector Blur: aggressive stylized smear/liquid effect.
- Unsharp Mask: sharpen detail.

MCP match names:

- `ADBE Gaussian Blur 2`
- `ADBE Directional Blur`
- `ADBE Radial Blur`
- `ADBE Unsharp Mask`

## Color Correction

Basic controls:

- Brightness & Contrast: quick exposure/contrast adjustment.
- Vibrance: boost color or reduce saturation to black-and-white.
- Levels: adjust blacks/whites and recover over/under exposure.
- Lumetri Color: preferred all-in-one grade, including LUTs/creative looks.

Adjustment layer workflow:

1. Add `Layer > New > Adjustment Layer`.
2. Apply Lumetri/Curves/Levels to the adjustment layer.
3. Place above all clips that should share the grade.
4. Lower adjustment layer opacity if the look is too strong.

Change-color workflows:

- `Hue/Saturation`: good for single-color graphics/shapes.
- `Change to Color`: better when changing a specific sampled color in footage.
- `Colorama`: very stylized; use mainly for music videos, glitch, sci-fi, or surreal looks.
- `CC Toner`: vintage/sepia/western-like looks.

## Distort Effects

Mirror:

- Apply `Mirror`.
- Move Reflection Center.
- Rotate Reflection Angle.
- Use for music-video symmetry or stylized reflection.

Fisheye:

- Use `Spherize` or `CC Lens`.
- Increase radius/size carefully.
- Works best with footage that has extra resolution/work area.

Warp:

- Excellent for text.
- Use Arc, Bulge, Flag, Rise, Squeeze, Twist, etc.
- Animate Bend for living title motion.

Environment distortion:

- `CC Smear`: pull/stretch an area.
- `Twirl`: swirl a region; animate angle as a character turns or a beat hits.
- `Bulge`: big-head effect; keyframe center to follow the face/head.
- `Magnify`: similar but more obvious edges; feather if used.

Warp Stabilizer:

- Use when handheld footage is shaky.
- Apply and let analysis complete.
- It can take time, especially with 4K.
- If edges crop strangely, adjust stabilization options manually in AE.

## Light Effects

CC Light Sweep:

- Use behind or on text/logos for shine.
- Animate Direction for a sweep across the object.
- Animate Intensity/Width for pulse.
- Match light color to the text/logo color when integrating it.

CC Light Rays:

- Place center at an existing light source such as a window.
- Keyframe the center to remain attached to that source as the camera moves.
- Keep intensity believable unless intentionally supernatural.

Lens Flare:

- Use only when a real/credible light source exists.
- Keyframe flare center and brightness.
- Use Blend with Original to fade it in/out.
- Avoid floating flares that do not track with the source.

Glow:

- Use for neon, eyes, logos, titles, energy effects.
- Combine with rotoscoped eyes/objects for superhero-style looks.
- Glow threshold/radius/intensity interact strongly; tune gently.

## Generate Effects

Use Generate when creating visual elements from a solid:

- Advanced Lightning: lightning arcs.
- Beam: laser-like start/end line.
- Circle: useful with invert for old-cartoon iris close/open.
- Lens Flare: generated flare.
- Audio Spectrum / Audio Waveform: visualizers.
- Fractal Noise: animated texture/background base.

Generated backgrounds:

1. Create a solid.
2. Apply a background preset or generate effect.
3. Animate parameters if static.
4. Lower opacity or blend if using as atmosphere over footage.

## Audio Effects

Use Audio effects when AE is already the active environment:

- Delay: repeated echo effect.
- Flange & Chorus: robotic/alien voice.
- High-Low Pass: radio/walkie-talkie filtered voice.
- Reverb: large room/cave/hall sound.

For precise audio mixing, prefer dedicated audio tools or Premiere/Audition, but AE effects are useful for synced VFX moments.

## Audio Spectrum Visualizer

1. Import audio.
2. Create a solid.
3. Apply `Audio Spectrum` to the solid.
4. Set Audio Layer to the imported audio.
5. Increase Maximum Height.
6. Increase Frequency Bands for density.
7. Choose Digital, Analog Lines, or Analog Dots.
8. Use Side A, Side B, or Side A & B.
9. Adjust Start/End points to position horizontal, vertical, diagonal, or border visualizers.
10. Extend solid duration to cover full audio.

Use `Audio Waveform` for heart-monitor style line; use `Audio Spectrum` for common podcast/music visualizers.

## Polished Effect Stack Example

For a text annotation over footage:

1. Warp text into a playful arc.
2. Animate it in with `CC Lens` size.
3. Add Drop Shadow.
4. Add CC Light Sweep behind it on the footage or directly on the text.
5. Add a short shine sound effect.
6. Keyframe out by reversing the CC Lens animation.

For a light-rich room shot:

1. Warp Stabilizer on footage.
2. CC Light Rays from a window.
3. Lens Flare only while the window/light source is visible.
4. Text callout with Drop Shadow.
5. Light Sweep on text for shine.

## Keying, Masking, Rotoscoping, Tracking Instructions

How to apply this block:

- Apply this block for green screen, alpha matte, video-in-text, masks, mask transitions, Roto Brush isolation, and motion tracking.
- Choose the technique by object type: Keylight for chroma, alpha mattes for text/media reveals, masks for hard-edged short shots, Roto Brush for complex organic motion, tracking for attaching graphics to footage.
- When MCP cannot perform Roto Brush, tracking analysis, or detailed mask refinement directly, provide exact AE UI steps from this block.

# Keying, Masking, Rotoscoping, Tracking

Use this block for green screens, alpha mattes, masks, mask transitions, Roto Brush, and motion tracking.

## Green Screen / Chroma Key

Basic Keylight workflow:

1. Put green-screen footage in a comp.
2. Apply `Keylight 1.2`.
3. Use the eyedropper to sample the green background.
4. Toggle transparency grid to inspect the key.
5. Increase Screen Gain to remove wrinkles/uneven green.
6. Duplicate the keyed layer if blue/near-green subject regions become too transparent.
7. Place the new background below.
8. Add Drop Shadow to subject for separation.
9. Use an adjustment layer with a shared color grade to tie subject and background together.
10. Add subtle background/subject scale animation so the composite feels alive.

Notes:

- Wrinkled green screens require higher Screen Gain or extra cleanup.
- Blue clothing/hair can become semi-transparent because blue is close enough to green for some key settings.
- A static background often makes the subject look pasted on; add slight motion or grade.

## Artificial Green Screens

Artificial green screens are motion graphics rendered over green instead of alpha.

To create:

1. Build text/shape animation.
2. Add a bright green solid below.
3. Export or import into another comp.
4. Apply Keylight and sample green.
5. Replace the background.

In AE-only workflows, prefer alpha exports over artificial green screens when possible. Use green only when a target workflow expects chroma key.

## Alpha Matte / Video In Text

1. Put text layer above the video.
2. Set video Track Matte to Alpha Matte using the text.
3. Precompose text+video if applying global shadow/glow.
4. Use Drop Shadow on the precomp to make the filled text stand out.
5. Optional: animate text with Write-on or opacity/scale.

## Masks

Mask rules:

- Pen/shape tool on selected footage/solid creates a mask.
- Pen/shape tool with nothing selected creates a new shape.
- Press `M` to reveal mask properties.
- Mask Path can be keyframed.
- Feather softens edges.
- Masks are crops, not new vector artwork.

Still-image masking:

1. Select the image.
2. Use Pen tool.
3. Trace object edges.
4. Close path.
5. Adjust points while zoomed in.
6. Toggle transparency grid to inspect isolation.

Moving-object masking:

1. Draw the initial mask around the object.
2. Enable Mask Path stopwatch.
3. Move forward a few frames.
4. Adjust points to match the object.
5. Repeat until done.
6. Use more frequent keyframes when motion is fast or perspective changes.

Use masks for hard-edged objects, graphic transitions, and short shots. Avoid long organic masks unless necessary.

## Mask Transitions

A masking transition uses an existing object in footage to reveal the next clip.

Workflow:

1. Choose clip A where an object crosses the full frame or enough of the frame.
2. Place clip B below clip A.
3. At the first frame where the object starts revealing the background, draw a mask on clip A over the revealed region.
4. Enable Mask Path.
5. Move frame by frame or every few frames.
6. Adjust the mask edge to follow the moving object.
7. Add Mask Feather to hide a hard seam.
8. Trim/scale clip B so it begins at the reveal.
9. If the moving object slows, scale or cut clip A to keep the transition feeling smooth.

Best sources:

- Poles, doors, walls, foreground pass-bys, signs, people crossing camera, camera wipes.

Quality target:

- Viewer should feel the next shot was naturally carried in by the object.
- Use tight masks; visible background leaks break the illusion.

## Rotoscoping / Roto Brush

Use Roto Brush when isolating complex organic or moving shapes that would be tedious to mask manually.

Workflow:

1. Double-click footage layer to open Layer panel.
2. Select Roto Brush.
3. Adjust brush size with `Ctrl` + drag.
4. Paint green strokes over subject/object to include.
5. Hold `Alt` and paint red strokes to exclude unwanted areas.
6. Step forward frames and correct edge drift.
7. Reassign strokes when AE asks/when propagation stops.
8. Duplicate the original layer below if you need the original background to fade back in.
9. Replace the background below the roto layer.
10. Add transitions via opacity, blur, glow, or background animation.

Tips:

- Roto Brush is heavy. Work in short segments.
- Motion blur makes edges harder to track.
- It is best for seconds, not minutes.
- Use a fresh project or precomp for very heavy roto/glow work.

Common roto recipes:

- Object isolation: roto hands/product, put animated liquify/background behind, fade original background back in.
- Screen replacement: roto screen, invert foreground/background, place new clip underneath, scale/rotate new clip into screen, then zoom through.
- Glowing eyes: roto both eyes, duplicate original below, apply CC Light Rays and Glow to eye layer, keyframe intensity/radius up and down.

## Motion Tracking

Motion tracking attaches a layer to movement in footage.

Basic position track:

1. Select footage.
2. `Animation > Track Motion`.
3. Place Track Point over a feature that clearly contrasts with surroundings.
4. Inner box: feature to track.
5. Outer box: search area.
6. Analyze forward.
7. Create `Layer > New > Null Object`.
8. Set tracker target to the null.
9. Apply X/Y.
10. Parent text/logo/graphic to the null.

Good track points:

- High contrast marks.
- Corners.
- Logos.
- Colored objects against neutral backgrounds.
- Tree/sign edges if clear enough.

Poor track points:

- Flat colors.
- Motion blur.
- Repeating textures.
- Features that leave frame.
- Areas with changing reflections.

Scale/rotation track:

1. Enable Scale and/or Rotation in the tracker.
2. Use two track points on features that move relative to camera.
3. Analyze.
4. Apply to null.
5. Parent target layer.

If tracking drifts:

- Pick a more contrasty feature.
- Analyze shorter sections.
- Manually correct the null or target layer with extra keyframes.
- Avoid pretending a rough track is perfect; trim the shot or hide drift with motion.

## Integration Tricks

To make inserted text/logo feel in-scene:

- Add Drop Shadow.
- Match blur/sharpness to footage.
- Match color temperature with Lumetri/Curves.
- Add slight opacity/fade.
- Use scale/rotation track when the plane moves toward camera.
- Trim the tracked layer to only the section where the track is reliable.

## Export Recipes Instructions

How to apply this block:

- Apply this block whenever the user asks for final delivery, preview renders, alpha overlays, still frames, or export troubleshooting.
- Choose H.264 MP4 for ordinary web/social video, QuickTime Animation RGB+Alpha for transparent overlays, and PNG for still frames or transparency.
- Before rendering, always verify the active comp, work area, alpha intent, audio intent, frame rate, duration, and delivery format.

# Export Recipes

Use this block for render/export choices from After Effects.

## Normal Video Export

Preferred course workflow:

1. Set work area with `B` and `N`.
2. `Composition > Add to Adobe Media Encoder Queue`.
3. Use Format: `H.264`.
4. Output as `.mp4`.
5. Render from Media Encoder.

Why:

- Much smaller file sizes than QuickTime.
- Good quality for web/social delivery.
- Faster and more practical for normal videos.

Avoid using AE Render Queue QuickTime for normal delivery unless a specific post-production workflow requires it. It can produce huge files.

## Faster AE Render Queue Preview

If rendering inside AE Render Queue:

- Press `Caps Lock` before rendering to disable live preview updates.
- This can speed renders and reduce crash risk on heavy comps.

This is most helpful on slower machines or heavy effects such as Roto Brush, Glow, 3D, and Warp Stabilizer.

## Transparent Background / Alpha Export

Use this for lower thirds, intro stingers, isolated green-screen characters, animated shapes, and overlay assets.

1. Toggle transparency grid and ensure no background layer is visible.
2. Set work area.
3. Add to Adobe Media Encoder Queue or Render Queue.
4. Format: `QuickTime`.
5. Video Codec: `Animation`.
6. Depth/Channels: `RGB + Alpha` or equivalent `8 bpc + Alpha`.
7. Render.
8. Reimport and test over a colored solid or footage layer.

Normal H.264 does not preserve alpha.

## Still Frame Export

Best simple method:

1. Park playhead on desired frame.
2. `Composition > Save Frame As > File`.
3. Output Module: PNG Sequence or JPEG Sequence.
4. PNG is preferred for quality/transparency.
5. Render the queued still.

Alternative:

- Set work area start/end to a single frame with `B` and `N`, then render a PNG/JPEG sequence.
- This is more awkward than `Save Frame As`.

## Export Checks

Before rendering:

- Confirm active composition is the intended one.
- Confirm work area length.
- Confirm preview-only resolution does not affect final settings.
- Confirm alpha intent: background visible for normal video, transparency grid for overlays.
- Confirm audio is enabled only when needed.
- Confirm frame rate and duration match delivery.

## Practical Presets

- YouTube/social normal video: H.264 MP4, 1920x1080, 30 fps unless source/project says otherwise.
- Transparent overlay: QuickTime Animation RGB+Alpha.
- Screenshot/promo still: PNG.
- Intermediate high-quality video without alpha: QuickTime/ProRes if available, only when the downstream workflow needs it.

## Practical Recipes Instructions

How to apply this block:

- Apply this block when the user asks for a concrete outcome and you need a ready sequence of AE actions.
- Combine recipes with the technique blocks above rather than treating recipes as isolated commands.
- Use the recipes as production checklists: first build timing and structure, then add effects, then verify export settings.

# Practical Recipes

Use this block when the user asks for a concrete After Effects outcome. Combine with the technique instruction blocks as needed.

## Mini Lesson: Slow-Motion Clip With Preset Transition

1. Import clip.
2. Create comp from footage to match source.
3. Disable audio if not needed.
4. Trim start/end with `Ctrl+Shift+D`.
5. Set preview resolution lower if playback lags.
6. Apply `Animation > Apply Animation Preset > Transitions - Movement > Stretch and Blur`.
7. Copy/paste transition keyframes near the end and reverse order for transition-out.
8. Set work area end with `N`.

## Beat-Synced Edit

1. Import video and audio.
2. Create comp from video or target delivery settings.
3. Add audio to timeline.
4. Press `LL` to show waveform.
5. Play and split video at beat peaks.
6. Delete middle sections and snap remaining clips.
7. Add final text such as `FIN` or a title card.
8. Trim work area.

## Framed Shot Without Quality Loss

1. Inspect footage resolution.
2. If source is 1080p and comp is 1080p, avoid scaling above 100%.
3. If reframing is needed, reduce comp to 720p or use higher-res source.
4. Reposition and rotate at 100% scale.
5. Use 4K source in 1080p comps for safer reframing.

## Hazard Warning Arrows

1. Import/reference arrow graphic if tracing.
2. Create one custom arrow with Pen tool.
3. Set fill to yellow/orange and optional stroke.
4. Open shape contents.
5. Add `Repeater`.
6. Set copies to 3.
7. Adjust repeater transform position/offset.
8. Refine original path; repeats update.

## 3D Globe With Stars

1. Import flat world map.
2. Apply `CC Sphere`.
3. Increase radius.
4. Keyframe sphere rotation over 10 seconds.
5. Create star shape layers.
6. Enable 3D switch on stars.
7. Add light.
8. Keyframe orientation/rotation of stars.
9. Duplicate stars at varied scales/extrusion depths.
10. Optional: animate globe radius larger and stars smaller for depth.

## Animated Course Title

1. Create main title.
2. Create subtitle.
3. Style main title bold, subtitle italic/smaller.
4. Apply text preset such as slow fade-on to main title.
5. Keyframe subtitle opacity from 0 to 100 as main title appears.
6. Keyframe both scales subtly upward.
7. Fade both out.

## Video-In-Text Write-On

1. Place video below text.
2. Alpha matte video to text.
3. Precompose result.
4. Apply `Write-on` to precomp.
5. Keyframe brush path across the letters.
6. Add Drop Shadow to precomp.
7. Optional: add Vibrance and Brightness/Contrast to source video inside precomp.
8. Keyframe precomp scale for subtle motion.

## Stabilized Annotation Shot

1. Apply Warp Stabilizer to shaky footage and let analysis finish.
2. Add annotation text near subject.
3. Apply `Warp` to make text playful.
4. Animate text in with `CC Lens`.
5. Add Drop Shadow.
6. Add CC Light Sweep or shine if appropriate.
7. Reverse the CC Lens animation to animate out.

## Green-Screen Composite

1. Apply Keylight to green-screen footage.
2. Sample green.
3. Increase Screen Gain until wrinkles vanish.
4. Duplicate keyed layer if subject becomes transparent.
5. Add background layer below.
6. Add Drop Shadow to subject.
7. Add adjustment layer with shared Lumetri look.
8. Keyframe subtle background/subject scale.

## Masking Transition

1. Pick footage with a foreground object crossing frame.
2. Place next shot below.
3. Draw a mask on top layer where object reveals next shot.
4. Feather mask.
5. Keyframe mask path frame by frame as object crosses.
6. Start next shot at reveal.
7. Trim and optionally scale top layer if the wipe slows.

## Roto Screen Transition

1. Use Roto Brush to isolate screen region.
2. Invert foreground/background so screen is removed.
3. Duplicate original below and fade screen removal in.
4. Place replacement video below.
5. Scale/rotate replacement to fit the screen.
6. Keyframe all layers to zoom through the screen.
7. Cut away once replacement fills frame.

## Glowing Eyes

1. Open close-up eye clip.
2. Roto Brush both eyes.
3. Duplicate original layer below.
4. On roto eye layer, apply CC Light Rays centered on each eye.
5. Apply Glow.
6. Keyframe light/glow intensity up, hold briefly, then down.
7. Keep the effect short; it is render-heavy.

## Logo/Text Motion Track

1. Track high-contrast feature in footage.
2. Apply tracker to a null.
3. Parent logo/text to null.
4. Add Drop Shadow.
5. Trim target layer to reliable tracking section.
6. If scale/rotation is needed, use two track points.

## Full Short Edit

1. Import clips and audio.
2. Build skeleton edit first: trims, speed ramps, rough order.
3. Add titles and motion tracking.
4. Add adjustment-layer color grade.
5. Add transitions/effects only after timing works.
6. Precompose if speeding entire edit or applying global effects.
7. Export H.264 for review.
