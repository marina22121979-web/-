---
name: automating-after-effects-from-code
description: >-
  Create and revise editable After Effects animations through scripted
  composition generation, motion planning, playback review, and verified exports.
  Use for typography, explainers, walkthroughs, transitions, and ExtendScript
  automation with file-based read-back. Includes a macOS execution workflow.
license: MIT
---

# After Effects animation and automation

Deliver an editable project whose motion communicates the intended message and
whose saved state and export have been verified. Successful execution, successful
rendering, and successful communication are separate outcomes.

## Capabilities and portability

Use the host agent’s available file, terminal, application-control, and media-review
tools. This skill requires no particular model, tool name, plugin, or API provider.
Follow the user’s instructions and the host’s permission boundaries.

- To plan or generate JSX, the agent needs file access and scripting capability.
- To execute and render, it needs access to a licensed After Effects installation
  and permission to control it and write the requested project/output files.
- The automated invocation reference covers macOS AppleScript. On Windows, use
  After Effects’ Run Script File command or a separately verified local bridge.
  Do not assume macOS commands work on Windows or Linux.
- A remote or cloud agent without an After Effects host can prepare scripts and
  review supplied exports; report execution and rendering as unverified.
- For media review, use the host’s actual capabilities and disclose when only
  sampled frames, rather than normal-speed playback or audio, were assessed.

## Choose the scope

- For new animation or a substantial redesign, read
  [motion design and review](references/motion-design-and-review.md). Establish a
  motion direction, build a representative editable sequence, review its playback,
  and refine it before extending the approach across the piece.
- For a small revision, inspect the current project and requested change, preserve
  approved scenes, and review the affected interval with its neighboring cuts.
  Do not require a new motion study or redesign to fix copy or timing.
- Before executing or changing automation, read
  [the automation reference](references/automating-after-effects-from-code.md).
  Use its generate → invoke → verify-by-file architecture. Treat observations
  about versions and installed templates as observations to verify locally.

- When effects, properties, mattes, or templates fail, read
  [troubleshooting](references/troubleshooting.md) before retrying.

## Working contract

1. Establish the actual project, source assets, output version, and available
   references. Inspect current state instead of assuming the most recent filename
   or previous completion marker is authoritative. Preserve open unsaved work
   before switching projects; keep backups distinct from intended deliverables.
2. For each substantial scene, identify its message, first focal point, action,
   readable hold, and connection to the next scene. Infer a sensible direction
   from the brief and existing work; ask only for material missing information.
3. Keep text, shapes, masks, and useful controls editable. Use readable layer and
   composition names. Keep frequently adjusted copy, timing, colors, and layout
   in a clear source of truth; update it when revising generated work.
4. Choose movement by purpose. Entrances, exits, emphasis, and continuous travel
   need different timing. Do not apply the same slide/fade or symmetric zero-speed
   easing to every element and every key. Stillness is a valid design choice.
5. Review motion in playback at intended speed and viewing size. Stills support
   layout inspection but do not establish rhythm, continuity, or readability.
   If playback cannot be assessed, report that limitation explicitly.
6. Make targeted revisions from observed defects or user feedback. Preserve named
   keepers and established choices. Carry improvements across comparable scenes
   only when that serves the request; avoid unrelated restyling.

## Completion evidence

- **Project:** save to the intended version, inspect fresh error/status output,
  and read back the relevant composition, layer, text, timing, and effect state.
  Required-operation failures must not be reported as a successful build. Save
  useful partial work to a separate recovery file, never over an approved final.
- **Export:** verify fresh output, dimensions, frame rate, duration, codec, and
  full decode as appropriate. Inspect scene boundaries and changed content. For
  redacted recordings, validate the entire affected span, not selected stills.
- **Creative review:** check reading time, focus, movement, transitions, and audio
  through playback. A technically valid export can still need creative revision.
- Report what was saved, rendered, reviewed, and delivered separately. Do not
  claim sharing or upload from the existence of a local file.

## Media and providers

- Build editable text, shapes, diagrams, and transitions directly in After Effects.
  Use supplied recordings and brand assets first.
- Use the user’s chosen image, video, or speech provider when assets require
  generation. Otherwise use an available appropriate tool within the task’s
  authorization; explain any material cost or external upload before proceeding.
- If a required tool is unavailable, provide a useful asset brief or use suitable
  supplied assets. Do not silently switch providers or fabricate missing UI.
- Identify synthetic or placeholder narration and keep it on a separate,
  replaceable track. Keep provider credentials and private assets out of scripts
  intended for distribution.
