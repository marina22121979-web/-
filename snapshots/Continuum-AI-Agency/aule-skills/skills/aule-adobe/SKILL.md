---
name: aule-adobe
description: Script the person's open After Effects, Photoshop, Illustrator or Premiere Pro document through Aulë (adobe_run, adobe_frame, adobe_send), make it Forge-ready, and render its variants in the Continuum cloud. Use when asked to build or change one of these files, turn it into a template, or render versions of it; not for general Adobe how-to questions.
---

# Aulë for Adobe

Aulë's panel in each Adobe app runs your scripts in the open document. `adobe_send` brings the work into Aulë, Forge
makes it a template, and the Continuum cloud renders the variants (Photoshop, Illustrator and Premiere work is rebuilt
there as an After Effects template). Nothing delivered is rendered on this computer.

`adobe_*` tools take `app`: `"aftereffects"`, `"photoshop"`, `"illustrator"` or `"premiere"` (`adobe_install` takes
`apps`). Library and render tools take `brandId` and the ids earlier answers give you. Answers carry `message` (tell
the person) and, when there is more to do, `next`: the exact call to make.

## 1. Connect

1. The tools come from the MCP server `aule` (names may carry a prefix such as `mcp__aule__`). Missing, or Aulë not
   installed: [references/connect.md](references/connect.md).
2. `auth_status`. Not signed in to Continuum: `auth_sign_in` opens the person's browser; they finish it.
3. `adobe_status` lists the apps with `connected: true` and the selected `brandId`.
   - Your app is not connected: [references/connect.md](references/connect.md), then `adobe_status` until it is.
   - `brandId: null`: `workspaces_list`, ask which, `workspaces_select`.
   - `adobe_status {app}` reads the open document. Nothing open, or never saved: ask the person; `adobe_send` needs
     a saved file.

## 2. Edit

- Read before you write: `adobe_status {app}`, then scripts that `return` what you need.
- `adobe_run {app, script, label}`: one small change per call, with a label the person sees in Undo (`"add title
  text"`). After Effects, Photoshop and Premiere make each call one undo step; Illustrator may split a call into
  several, so keep Illustrator calls to one change. `return` plain values.
- A thrown error answers `invalid_input` with its message. Photoshop rolls the call back, and in Premiere only `edit`
  changes the document; After Effects and Illustrator keep whatever ran before the throw, so re-read before you retry.
- Read the app's reference before its first script:
  - After Effects: ES3 ExtendScript — [references/after-effects.md](references/after-effects.md)
  - Illustrator: ES3 ExtendScript — [references/illustrator.md](references/illustrator.md)
  - Photoshop: async JavaScript, `photoshop` UXP module — [references/photoshop.md](references/photoshop.md)
  - Premiere Pro: async JavaScript, `premierepro` module and `edit(...)` — [references/premiere.md](references/premiere.md)
- Never open, close or save files: `adobe_send` saves a copy. Don't delete the person's layers; rename one only to make
  it a field, and say which.
- Look at your work: `adobe_frame {app}` saves a PNG and answers its `path`; read the image. After Effects takes
  `{comp?, time?}`; Illustrator draws the active artboard. Premiere has no frame: look at a proof render after sending.

## 3. Make it Forge-ready

Build to Forge's rules from the start: [references/forge-ready.md](references/forge-ready.md). In short: After Effects
delivers `RENDER <name>` comps whose variable parts are Essential Properties; Photoshop and Illustrator deliver one
artboard per size with named layers; Premiere delivers its top-level sequences, with graphic text and clips as fields.
Use installed fonts (not Adobe Fonts) and media that exists.

## 4. Send, forge, render

Every answer and what to do next: [references/scale.md](references/scale.md).

1. `adobe_send {app}`. Tell the person its `message`, any `skipped` media and `fonts.left`.
   - `outcome: "named"`: a template already has this name. Ask, then `adobe_send {app, sameName: "revision" | "new"}`.
   - `outcome: "same"`: it is already in Aulë as it is.
   - `state: "forge_queued"`: go on. Any other `state`: do what `next` says.
   - An error: tell the person its message, and check `adobe_status` before trying again.
2. `library_wait {brandId, assetIds: [assetId], until: "review"}`. A run with questions: `library_run {brandId,
   assetId}`, then `library_forge {brandId, assetId, action: "decisions", …}`.
3. Publishing is the person's call: they promote it in Aulë, or ask you to (`library_forge {…, action: "promote"}`).
4. Proofs: 2–3 rows through `render_batch_preflight` → `render_batch_submit` → `render_wait` (scale.md §4). Submit
   only when every row is `READY`. Show the outputs; run the full batch (≤ 50 rows each) only when the person agrees.

Renders cost money. Every slow step has a `*_wait` tool: call it instead of polling.
