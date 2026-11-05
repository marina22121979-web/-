---
name: fcp-frame-hotkey
description: Configure, update, troubleshoot, or remove a macOS Hammerspoon hotkey that opens Final Cut Pro's Share → Save Current Frame workflow. Use when the user wants an FCP-only key to export the playhead frame, with either manual confirmation or automated saving. Do not confuse it with Comparison Viewer Store Frame.
---

# FCP Frame Hotkey

Use Hammerspoon as the preferred implementation when it is installed and trusted. Do not modify Final Cut Pro command sets and do not click screen coordinates.

## Required behavior

- Scope the trigger to Final Cut Pro bundle ID `com.apple.FinalCut`; every other application must receive the key normally.
- Detect both Chinese and English menu paths at runtime:
  - `文件 → 共享 → 存储当前帧…`
  - `File → Share → Save Current Frame…`
- Verify that Save Current Frame exists as an FCP Share destination before installing the hotkey. Add it through FCP Destinations settings only when missing.
- Set the destination image format to PNG when the user requests PNG. Preserve project resolution and color space unless explicitly asked otherwise.
- Treat Comparison Viewer `Store Frame` as the wrong feature.

## Modes

Choose the mode from the user's request:

- **Manual-save mode:** invoke Save Current Frame, activate `Next…`, then stop at the macOS Save dialog. Do not type a filename, choose a directory, or press Save.
- **Automatic-save mode:** only when explicitly requested, fill the filename and destination and confirm Save. Use collision-resistant names and wait for FCP media preparation before claiming success.

The bundled [assets/init.lua](assets/init.lua) implements manual-save mode with `1` for both the ANSI number row and numeric keypad. Adapt constants rather than rewriting the event filtering.

## Installation and updates

1. Inspect existing `~/.hammerspoon/init.lua`; preserve unrelated user automation.
2. If the existing file is dedicated to this workflow, replace it with the adapted asset. Otherwise integrate this workflow without clobbering other bindings.
3. Ask for the smallest filesystem permission needed to write `~/.hammerspoon`.
4. Reload Hammerspoon after changes. Keep login launch enabled when the user wants persistence.
5. Hammerspoon requires Accessibility; raw key monitoring may also require Input Monitoring. Identify Hammerspoon—not Terminal or Codex—as the app to enable.

## Verification

- Confirm the configured mode appears in `/Users/xin/FCPFrameHotkey.log`.
- With FCP frontmost, press the trigger and verify the Save Current Frame dialog flow.
- In manual mode, verify the Save dialog remains open and no file is created until the user confirms.
- In another application, verify the trigger remains normal input.
- Never report an exported file until it exists and its format/dimensions are inspected.

## Cleanup

Remove only obsolete implementations after resolving exact paths. Preserve Hammerspoon and `~/.hammerspoon/init.lua` when they provide the active workflow. Prefer moving old apps and launch agents to Trash so recovery remains possible.
