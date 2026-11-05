---
name: after-effects
description: Safely inspect and control Adobe After Effects through the MAHI After Effects MCP server. Use for opening or saving AEP projects, importing footage, creating compositions, adding text/solid/footage layers, setting keyframes, applying an effect, attaching or removing expressions, rendering a composition, or determining whether a requested After Effects operation is unsupported by the current MCP.
---

# After Effects MCP Router

## Purpose

Control After Effects through real `mahi-afterfx` tools with explicit comp/layer targeting, save-aware rendering, and conservative validation.

## Scope

Support project inspection/open/save, media import, composition creation, text/solid/footage layer creation, keyframe setting, effect addition, expression assignment/removal, headless render, and restricted ExtendScript fallback.

## Non-goals

Do not imply named-tool support for layer/property inspection, masks, keying, tracking, cameras, 3D setup, effect parameter editing, easing, keyframe deletion, render-queue management, undo, or checkpoints.

## Required MCP server

Require `mahi-afterfx` from `/Users/sinatorabi/Documents/MAHI/mcp-servers/afterfx/index.mjs`. After Effects must allow scripts to write files and access the network.

## Capability summary

- Inspect/open/save/import: `ae_project_info`, `ae_open_project`, `ae_save_project`, `ae_import`
- Create comp/layers: `ae_create_comp`, `ae_add_layer`
- Animate: `ae_set_keyframes`, `ae_set_expression`
- Add effect: `ae_apply_effect`
- Render: `ae_render`
- Escape hatch: `ae_run_script`

## General operating procedure

1. Read the routed reference.
2. Inspect with `ae_project_info`.
3. Resolve exact comp, project-item, and layer names; reject ambiguity.
4. Protect or save the project before high-impact changes.
5. Execute one logical mutation.
6. Reinspect available project state and validate returned data.
7. Render only after project and output requirements are confirmed.

## State inspection rules

- `ae_project_info` reports project path, item inventory, comp dimensions/duration/frame rate/layer count, and render-queue count.
- It does not expose layer names, property values, keyframes, expressions, effects, masks, or render settings.
- Do not guess layer/property names. Obtain them from explicit user input or a trusted external inspection.

## Planning rules

- Prefer named tools over `ae_run_script`.
- Use unique comp/layer/item names because named tools resolve by name.
- Validate keyframe value shape against the intended property: scalar versus array.
- Treat effect display names as version/localization-sensitive; prefer verified match names when available.

## Safe execution rules

- Treat open/save, keyframe changes, effects, expressions, render, and arbitrary scripting as high impact.
- Never retry a timed-out mutation without reinspecting.
- Remember `ae_render` saves the project before invoking `aerender`.
- Do not overwrite output files without explicit acceptance.

## Validation rules

- Re-run `ae_project_info` after open/save/import/create-comp/add-layer.
- For keyframes/effects/expressions, validate returned property/effect state but acknowledge missing independent inspection.
- For render, verify output existence, nonzero bytes, and media integrity when probing is available.

## Failure and recovery rules

- Stop mutations after errors or uncertain timeouts.
- Verify scripting permission, app state, exact names, and project path.
- No undo/checkpoint MCP tool exists; require an external copy or explicit risk acceptance.

## Reference routing table

| Request | Read |
|---|---|
| Project/open/save/import | [project-and-assets](references/project-and-assets.md) |
| Comp or layer creation | [compositions-and-layers](references/compositions-and-layers.md) |
| Keyframes/animation | [animation-and-keyframes](references/animation-and-keyframes.md) |
| Effects/expressions | [effects-and-expressions](references/effects-and-expressions.md) |
| Render/output | [rendering](references/rendering.md) |
| Arbitrary scripting | [custom-scripting](references/custom-scripting.md) |
| Failure/ambiguity | [troubleshooting](references/troubleshooting.md) |

## Workflow routing table

| Goal | Read |
|---|---|
| Import, animate, render | [import-animate-render](workflows/import-animate-render.md) |
| Open, inspect, modify, save | [open-inspect-modify-save](workflows/open-inspect-modify-save.md) |

## Extension points

Let motion-graphics or VFX skills supply design, timing, easing, compositing, and quality criteria. Keep this skill responsible for After Effects capability routing and safe execution.

## Known unsupported capabilities

Read [unsupported capabilities](docs/unsupported-capabilities.md) before promising masks, tracking, keying, 3D, cameras, effect parameters, easing, detailed inspection, render-queue control, undo, or checkpoints.
