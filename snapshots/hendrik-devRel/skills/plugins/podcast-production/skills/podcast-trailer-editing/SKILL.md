---
name: podcast-trailer-editing
description: Build podcast opening trailers from existing episode edits, select compelling teaser excerpts, and animate speech-timed kinetic typography in Adobe Premiere Pro and After Effects. Use for trailer hooks, word reveals, varied text sizes, orange highlights, underlines, and short style pilots. Preserve editable camera and microphone tracks and deliver checked previews. Standalone social clips belong in podcast-shorts-editing.
---

# Podcast Trailer Editing

Turn an existing edited conversation into a compelling opening trailer and a repeatable, editable graphics treatment. Use the current saved native edit as the source of truth. This skill covers excerpt selection through delivery; full-episode synchronization and grading belong in the available `premiere-podcast-editing` skill when needed.

## Start at the requested stage

- **Standalone Shorts or a portfolio of social clips:** use the separate [podcast-shorts-editing skill](../podcast-shorts-editing/SKILL.md) for complete-idea selection, portrait architecture, speaking-turn audio and standalone review exports. Keep episode-opening teasers here.
- **Reference research or several trailer variants:** read [reference-led trailer studies](references/reference-led-variants.md) for timestamped browser screenshots, distinct content edits, editable multi-camera AE studies and source-edge audio checks.
- **New trailer:** read [trailer production](references/trailer-production.md) for excerpt selection, context, source clocks, and timeline structure.
- **Kinetic words on an existing trailer:** read [native kinetic workflow](references/native-kinetic-workflow.md). Analyze supplied references, export the current pilot audio, measure real fonts, build native text and shapes, and integrate a silent alpha overlay.
- **Continue an accepted pilot:** read [continuation and body-clear layout](references/continuation-body-clear.md) for fresh source clocks, layouts that change at camera cuts, measured accents, source-time placement and every-frame alpha bounds QA.
- **Refine an approved trailer:** read [fixed-timing refinements](references/continuation-body-clear.md#refine-an-approved-trailer-without-retiming) for larger type, speech-cued logo replacements, restrained motion, end-card changes and local vocal-reaction cleanup.
- **Generate reusable operation plans or check preview audio:** read [helper contracts](references/helper-contracts.md) before using `scripts/`. These helpers prepare local artifacts; they do not give permission to mutate an open Adobe project.
- **Review/export:** read [verification and delivery](references/verification-delivery.md). Distinguish editable source, rendered overlay, native timeline, and preview evidence.
- **Upload an approved trailer and prepend it to the episode:** read [trailer-to-episode assembly](references/trailer-to-episode.md) for native project import, verified clip/marker offsets, separate audio routing and music carryover.
- **Memory pressure, cache-space warnings or shared-machine rendering:** read [Adobe resource checks](references/adobe-resource-checks.md) for bounded measurements, one-owner coordination and cache recovery between completed renders.
- **Reproduce or inspect the CodeRabbit example:** read [the complete worked pilot](references/worked-astra-fable-pilot.md) and [example assets](references/example-assets.md). Its timings, names, fonts and paths describe one episode; do not apply those source clocks to new footage.

## Operating principles

1. Inspect the active project, sequence IDs, current clip/source bounds, dimensions, rational frame rate, camera identities and microphone routing. The user may continue editing while the agent works; address sequences by verified IDs and re-read before mutations.
2. Preserve the latest edit and approved camera grades. Duplicate for an alternate trailer or short visual experiment. Keep source recordings untouched.
3. Keep dialogue faithful to its context. A dramatic trailer must not manufacture a claim, strip a material qualification, or attach an answer to a different question.
4. Match the requested scope. When the user asks for the first ten seconds, finish and present that pilot before expanding the treatment. Once the user accepts it, continue within their requested scope without inventing another approval step.
5. Keep camera angles separately adjustable, and keep independent microphones separate when they actually exist. For a shared recording mix, preserve that mix and its gain automation; speaker labels do not create microphone isolation. Typography belongs above those picture tracks and should not introduce another copy of the dialogue.
6. Reveal words into a prepared layout at measured speech onsets. Type hierarchy, timing and holds create the effect; extra bounce or motion is a creative choice supported by the reference, not a default.
7. Prefer actual native text, shapes, sparse keyframes and an editable AEP. A rendered MOV in Premiere is adjustable as an overlay but is not individually editable word text there. Explain where each control lives.
8. Tool success is not visual proof. Inspect native frames, check exported audio against the current PCM, and test source text editability. Describe sampled checks and numerical timing accurately; do not claim a full listening review that did not occur.

## Tools and boundaries

Use the callable Premiere MCP catalog and the installed Premiere connection skill when available. For After Effects, follow the installed `use-after-effects` skill, load its clean-rig guidance and relevant references, then inspect `ae_catalog` schemas. Reuse functioning installations. Do not bypass a disabled eval operation or a bridge validator.

Batch independent reads and bounded AE operations; inspect both results and warnings. A batch is not transactional. Native-app dependencies and edits whose success controls the next step should run sequentially, stopping on failure and checking partial state before retries. If a connector reports a required user action or a stop condition, follow that result; preserve completed artifacts and describe the precise remaining check.

Coordinate one writer at a time for a shared native Adobe application. Parallel research and offline media analysis may continue, but another task must not switch projects, edit or render in that application until ownership is handed over. Save the current project first; hand over its path, relevant composition/sequence IDs and any active render state. The next writer should re-read native state before acting.

## Deliverables

Leave a versioned native trailer/pilot sequence, editable AEP when animated, silent transparent overlay, preview with sound, current-source timing map, and a concise handoff index. For an editor handoff, verify that a phrase and its native controls can be found and revised using [the practical delivery checks](references/verification-delivery.md#packaging-and-iteration). Save the evidence needed to regenerate and verify the result. Link the preview and editable source in the response, name the Premiere sequence, and state substantial limitations.

This is a local skill. A copy of this folder carries its instructions, helpers and worked-example files to another machine; it does not install Adobe apps, synchronize account skills, activate fonts, or make the current episode's external media paths available there.
