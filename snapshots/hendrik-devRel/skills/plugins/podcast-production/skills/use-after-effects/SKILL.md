---
name: use-after-effects
description: Set up and use the local Higgsfield use After Effects MCP when the user asks to connect After Effects, install its local integration, or create and edit native AE projects.
---

# Higgsfield use After Effects

Connect the desktop MCP client to the local Node server, which runs bundled ExtendScript inside After Effects through OS scripting and a local file mailbox. No cloud bridge, Higgsfield login, or installed AE panel is required. Adobe licensing and OS Automation permissions remain separate requirements.

Use **Higgsfield use After Effects** as the user-facing integration name. `fnf-after-effects-mcp` and `fnf-after-effects` are package/CLI identifiers, not display names. Register the server as `higgsfield-use-after-effects`. When migrating an existing `fnf-after-effects` registration, preserve its command, arguments, environment and other client settings before replacing it; refresh the connection afterward.

## Setup

1. Locate the `fnf-local-pluging-bridge-mcp` checkout (or the legacy `fnf-after-effects-mcp` checkout) from the current workspace or user-provided path. Do not assume another user's home directory. Require Node 24+ and macOS or Windows with After Effects installed.
2. In that checkout run `npm ci --ignore-scripts`, then `npm run build` and `node dist/cli.js doctor`. This checks files and installation without launching AE; it does not prove live connectivity.
3. For Codex, run `node dist/cli.js install-codex`. It registers the absolute Node and server paths as `higgsfield-use-after-effects`; a conflicting existing entry must be resolved explicitly. For another desktop MCP client, use the configuration printed by `node dist/cli.js config`. A remote web client cannot directly launch this local stdio process.
4. Refresh the client's MCP connection if needed. Call `ae_get_skill` with no arguments, then with `name: "ae-clean-rig"`. These calls work even with AE closed.
5. Call `ae_project_info` to test real communication. Let the OS present any Automation permission prompt. If AE reports file/network scripting disabled, enable the corresponding AE Scripting & Expressions preference as part of the requested installation. Do not silently modify unrelated preferences or close an unsaved project.
6. Only report connected after a successful live response. Distinguish missing app, permission denial, startup timeout and a working MCP with disconnected AE.

## Work

Discover categories with `ae_catalog`, inspect the current project, load only relevant companion skills through `ae_get_skill`, and execute documented operations through `ae_do`. Preserve existing work. Use a small isolated comp for a user-authorized smoke test. Check returned errors and rendered frames before claiming success. A skill supplies instructions; it cannot create an unavailable MCP tool in the current session.
