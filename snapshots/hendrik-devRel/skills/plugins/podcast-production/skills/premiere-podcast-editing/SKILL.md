---
name: premiere-podcast-editing
description: Edit multicamera podcasts in Adobe Premiere Pro using camera originals and isolated microphones or a shared recording mix. Use for sync, speaker-led cuts, log grading, dialogue balance, muting inactive microphones, opening trailers, screen inserts, presenter picture-in-picture, or removing ums, ems, erms and uhs with smooth audio blends and short picture dissolves. Deliver editable sequences and verified previews.
---

# Premiere Podcast Editing

Produce a reviewable Premiere project, with an edit driven by the conversation and the user's creative brief. Preserve the source recordings and keep the working project separate from an existing original. This skill records a workflow exercised on a three-camera podcast; episode-specific values are examples, not defaults for every recording.

## Establish the recording and edit brief

Confirm the actual mapping between people, microphone files, and camera angles from the current request, listening/transcription, and sampled pictures. Treat attached studio guides as reference material. A current user correction overrides an old equipment list; file metadata resolves what was actually recorded.

Inventory original camera files, isolated microphones, backup program/ISO files, sidecar metadata, and the existing project. Probe dimensions, rational frame rate, codec/bit depth, sample rate, channels, exact duration, and camera color profile. Names such as “4K,” “FX6,” or “Slog4” do not establish those facts. In Sony sidecars, Rec.709 matrix coefficients do not by themselves mean Rec.709 transfer/gamma.

For large Drive originals, read [large remote media](references/large-drive-media.md) when a connector cannot materialize the file or a streamed cache will not fit internally. Verify each original's byte count before importing it.

Use the requested originals for the edit. A processed backup can be a color reference without becoming primary picture. Disclose a material source limitation, such as one camera being HD, and make scaling explicit. Choose sequence settings from verified media and the delivery brief.

Read [the worked episode](references/recorded-case.md) only when resuming that project or when an example helps. Do not reuse its paths, identities, cut boundaries, or clock coefficients for a new recording.

## Synchronization, dialogue, and editorial decisions

Read [sync and audio](references/sync-and-audio.md) when estimating alignment, speaker turns, processing microphone tracks, or checking rendered audio.

When several people share one usable recording mix, read [shared-mix dialogue](references/shared-mix-dialogue.md) for source identification, per-turn leveling and the distinction between camera AAC alignment and native export delay. Keep the actual shared mix; do not manufacture speaker isolation from duplicate files or diarization labels.

When asked to “cut out the ems/ums,” remove hesitation sounds, or smooth filler-removal cuts, read [conservative filler cleanup](references/filler-cleanup.md). In this editing context, “M's” can mean spoken fillers; preserve /m/ sounds within words and meaningful acknowledgments. Preserve the earlier native edit, review candidates in context, and derive picture cuts and fixed-duration audio blends from one exact frame map. The [audio helper contract](references/filler-audio-config.md) describes its supported inputs and verification limits.

For an opening trailer assembled from an existing edit, read [opening trailers](references/opening-trailers.md) for contextual excerpt selection, source-clock mapping, and simple graphics fallback.

The dedicated [podcast-trailer-editing skill](../podcast-trailer-editing/SKILL.md) contains the expanded trailer workflow, native kinetic-text construction, tested local helpers, editable worked example and export verification. Use it for a complete trailer or typography production task.

For words appearing on speech with varied scale, orange highlights, or underlines, read [kinetic typography](references/kinetic-typography.md). Build the requested short pilot before extending a proposed visual formula.

For screen captures, Screen Studio exports, or gameplay overlays in an existing edit, read [screen recordings and demonstrations](references/screen-recordings.md). Match the actual demonstration and its clocks while preserving the camera and microphone edit. Use already suitable silent sources directly; export natively when the requested screen treatment requires it.

For a talking-head or presenter inset over those demonstrations, read [presenter inset](references/presenter-inset.md). Use the saved visual example when requested, validate physical scale per nest, and perform a pilot with protected audio tracks locked.

When verified independent microphones should play only during each person's speech, read [separate microphones](references/separate-microphones.md). Keep independent tracks and use sustained speaking turns to mute the listener, with editable handoff fades and narrow exceptions for genuine replies. Speech detection alone can reopen a microphone on bleed; verify the user's example and preserve manual mute automation.

- Establish one recorder clock. Do not trust unrelated camera timecodes or folder dates. Align scratch audio against the verified recorder source and measure drift across the recording, with separate holdout windows.
- Record the mapping explicitly: `recorder_seconds = a * camera_seconds + b`. Source placement uses `(recorder_seconds - b) / a`. Recompute source in-points at cuts, or apply a verified continuous retime when needed.
- Identify sustained speaking turns using the available audio evidence and context. Relative microphone levels help only when independent microphones exist. Mic bleed, laughter, and short acknowledgments should not produce rapid switching. Thresholds and minimum holds are starting points to tune against this recording.
- Use a wide shot for an opening, shared reaction, transition, or relief during a long answer when the picture supports it. A rigid timer is only a first-pass aid.
- Use transcripts to locate the formal opening, wrap, setup chatter, and demo references. Review words and boundaries before cutting; quiet time can be a meaningful demonstration. Keep substantial pre-show conversation separately when its value is uncertain.
- Process dialogue without moving its source clock. Keep adjustable stems and raw recordings available. Choose loudness and peak targets for the delivery; measure the exported result as well as the intermediate master.

## Construct an editable Premiere project

Read [Premiere operations](references/premiere-operations.md) for the tested MCP/UI workflow, version-specific failures, and native verification. Use callable Premiere tools when available. If the installed `premiere-pro-mcp` skill is available, use it for connection/setup; this skill does not require reinstalling a working bridge.

Use a small representative import test when a new Premiere version or XML representation is unverified. Include each camera, continuous microphone audio, and any HD-to-UHD scaling. Confirm the native result before building the whole edit.

A useful structure is one full-source, video-only sequence per angle, with grading applied once inside it. The editorial sequence nests those angles, while continuous recorder-based audio remains independent of camera cuts. This supports global camera matching and later editorial changes. For a human-editor handoff, also retain the synchronized alternatives in a clearly named camera assembly or native multicam source covering the retained conversation wherever sources exist. Selected fragments and full-source handles alone can still make changing shots cumbersome. Keep an optional bonus sequence when useful.

For an XML-driven build, read [the configuration contract](references/xml-config.md), then use `scripts/build_podcast_xml.py`. It creates FCP7/XMEML and a validation report from explicit media, sync, keep-range, turn, and marker data. It does not import, grade, or export in Premiere. Generated XML is a reconstruction artifact; the native project is canonical once effects or further edits are applied.

For three separately adjustable camera tracks, read [separate camera tracks](references/separate-camera-tracks.md) and use `scripts/restructure_podcast_xml.py` on the untouched builder XML and matching manifest. Its selected-shot reconstruction does not create a native multicam source or a complete synchronized alternative-angle assembly. Preserve full-angle handles and the existing visible edit; audio preservation remains valid when isolation is unavailable.

When a registered MCP server is not exposed as callable tools in the current task, `scripts/mcp_call.py` can make explicit stdio requests to an already installed server. Supply its local server path. Use `tools/list`, then `search_tools`/`get_tool_schema`, then `invoke_tool`; inspect actual results. The helper does not install/configure a server or retry uncertain mutations.

## Grade the actual footage

Determine whether Premiere has already converted the camera input before adding a LUT. Apply the correct camera-space transform once, then compare aligned original/backup frames and camera-to-camera skin tones. Do not add contrast or saturation merely to make a grade feel more substantial.

Verify the LUT in actual Lumetri controls or serialized effect data and in rendered pixels. A response saying “LUT applied” is insufficient. Adjust backlit faces carefully while protecting windows and practical lights. Inspect samples early, mid-recording, and late enough to reveal lighting changes. Leave the grade editable.

## Verify and hand over

For delivery to another editor, read [human-editor handoff](references/human-editor-handoff.md). Make the native project navigable, verify practical camera/title changes, and identify the approved audio and review versions.

Verify native sequence duration, source bounds, camera ordering, audio routing, gap/offline state, and representative scaling and color. After a local correction, check its interval and that adjacent audio remains unchanged. Keep verification proportional; a short preview is not a complete editorial review of an hour-long episode.

Export a review excerpt through Premiere to exercise actual nests, effects, and mixer. If Media Encoder is absent, Premiere's direct export can still work. Verify the resulting file, not just a queued/export-success message. Check picture against the cut plan, audio against the intended master, loudness/peaks, and meaningful sync points. Investigate a measured AAC priming offset before any container correction.

For long exports or a measured native AAC delay, read [streaming export-audio verification](references/streaming-export-audio.md). Its helper compares both channels with the matching native PCM, checks complete sequential audio/tail coverage, and can publish a verified separate AAC replacement while preserving compressed picture.

Save the project on the main edit sequence. Report the project path, duration, preview, substantial choices, source limitations, and remaining work. Mark missing screen captures or graphics rather than fabricating them. Do not claim full playback review, a completed full-length render, or publication unless it occurred.

This skill is installed locally. For another computer, copy this entire folder into that computer's configured skills directory and verify the local media paths, tools, Premiere version, and connection there.
