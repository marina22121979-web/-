---
name: soundbite-editor
metadata:
  author: Christos Konteos
description: >
  AI-powered video editing assistant that reads a Premiere Pro JSON transcript,
  uses a natural-language prompt to intelligently find the best matching soundbites, presents
  them for user review, then exports a fully valid XMEML XML file importable into Adobe Premiere
  Pro or Final Cut Pro 7.

  USE THIS SKILL whenever the user:
  - Uploads or pastes a video transcript (JSON) and wants to find highlights or soundbites
  - Asks to "find clips", "pick soundbites", "cut highlights", "make a highlights reel", or similar
  - Mentions exporting or generating XML
  - Wants to search a transcript by topic, keyword, speaker, or theme
  - Has a Premiere Pro transcript and wants to do anything with it related to editing or selecting clips

  Always trigger this skill even if the user hasn't explicitly mentioned XML — the final export step
  is part of the workflow and users often don't know it's needed until you show them the selected clips.
---

# Soundbite Editor

1. **Transcript Ingestion** — accept the user's JSON transcript, confirm frame rate, and generate a sentence-level summary table
2. **Soundbite Selection** — understand what the user wants, match sentences, and iterate until they confirm a final list
3. **XML Generation** — collect file details, build the config, and export via `scripts/generate_xml.py`

Do not read or transcribe the JSON by hand. Do not generate XML by hand.

---

## Phase 1 — Transcript Ingestion

### Step 1: Accept the transcript and prompt

The user provides a **Premiere Pro JSON transcript** file (exported via Premiere's transcript panel). They may also include a natural-language prompt describing what kind of soundbites they want — if so, hold onto it for Step 4.

This step initiates the soundbite editor workflow. Proceed immediately to Step 2.

### Step 2: Ask the user for their timeline frame rate

Use the `ask_user_input_v0` tool to present a frame rate selector. All timecodes in the segment table and all subsequent XML output depend on this value, so it must be confirmed first.

```
ask_user_input_v0(questions=[{
    "question": "What is the frame rate of your timeline?",
    "type": "single_select",
    "options": ["23.976", "24", "25", "29.97", "30", "50", "59.94", "60", "Custom"]
}])
```

- If the user selects **Custom**, follow up asking them to type the exact value.
- If the user has already stated the fps earlier in the conversation, skip this step and use that value.
- Store the confirmed fps and use it for **all** timecode conversions from this point forward — both in the sentence summary table and in the XML config.

### Step 3: Run the summarize script and generate the sentence table

The script splits the transcript at sentence boundaries (using word-level `eos` flags) and outputs a pipe-delimited table. It also prints a summary line to stderr — e.g. `25 sentences | last ends 00:08:32:14 | 30734 frames @ 60fps`. Save the **frames** value from this line — it will be used as `source_frames` in Step 8.

**Do not display the table in chat.** Run these two commands — the first saves the table to disk, the second generates the HTML for the user:

```bash
python scripts/summarize_transcript.py "<path_to_transcript.json>" --fps <fps> > /home/claude/transcript_table.txt
```

```bash
python scripts/table_to_html.py /home/claude/transcript_table.txt > /home/claude/transcript_table.html
```

Then present the file to the user using `present_files` with path `/home/claude/transcript_table.html`.

## Phase 2 — Soundbite Selection

### Step 4: Understand the user's selection prompt

If the user has already given a prompt alongside the transcript, skip this step and proceed directly to step 5 using the provided prompt.

Otherwise, analyse the sentence table to identify 4 distinct themes or content types that are genuinely present in the transcript. When generating the 4 themes:
- Vary across different dimensions — topic, emotion, speaker, moment type — so they feel meaningfully distinct
- Write each as a short natural-language phrase a non-editor would understand — e.g. "Jensen's boldest predictions about AI" not "Segment topic: AI predictions"
- Never use generic fallbacks like "Inspiring moments" or "Technical explanations" unless the transcript genuinely warrants them

Use these 4 themes to populate the `ask_user_input_v0` options. The UI renders a free-text input field at the bottom automatically, so the user can either tap a preset or type anything custom:

```
ask_user_input_v0(questions=[{
    "question": "What are you looking for in this transcript?",
    "type": "single_select",
    "options": [
        "<theme 1>",
        "<theme 2>",
        "<theme 3>",
        "<theme 4>"
    ]
}])
```

Accept whatever the user selects or types — both are valid inputs for soundbite matching.

### Step 5: AI-powered soundbite matching

Read all sentences from the table and semantically match them against the user's prompt. Prioritise:
- **Semantic relevance** — does the content match the theme, not just keywords?
- **Completeness** — prefer sentences or groups of adjacent sentences that contain a complete thought or serve a point
- **Speaker clarity** — prefer sentences where speech is unambiguous
- **Duration** — avoid very short fragments (<2s) unless they're punchy and self-contained

You may propose **merging adjacent sentences** if they form a single coherent thought. Present these as a single soundbite using the first sentence's Start and the last sentence's End as the in/out time.

### Step 6: Present proposed soundbites for confirmation

Display a numbered list with enough context for the user to decide:

```
Proposed soundbites for: "moments about mindset and resilience"

 #1  00:01:23:10 → 00:01:31:05  (7s 20f)
     "You have to train your brain the same way you train your body — every single day."

 #2  00:04:11:00 → 00:04:19:14  (8s 14f)
     "When things get hard, that's exactly when champions lean in rather than back off."

 #3  00:07:55:20 → 00:08:04:08  (8s 13f)
     "I've never met a successful athlete who didn't have an obsessive relationship with discipline."

Accept all? Remove any? Add anything I missed? You can also adjust in/out times.
```

Iterate as needed: if the user removes soundbites, asks for replacements, adjusts in/out times, or requests a different search prompt, repeat from the relevant step (Step 5 for re-matching, Step 6 for adjustments). Only move to Step 7 once the user is satisfied with the final list.

**Do not proceed to XML generation until the user confirms the selection.**

Once confirmed, store the final soundbite list — each with its in/out timecodes.

## Phase 3 — XML Generation

### Step 7: Collect missing file details

First, ask for the folder path as a plain text message:

> *"What is the folder path where your video is saved? Just the folder — not the filename (e.g. `D:\Projects\Videos` or `/Users/john/Movies`)."*

Then present the filename and duration questions using `ask_user_input_v0`. Derive the filename stem from the JSON filename by stripping the `.json` extension. Truncate the middle of the stem to keep the buttons readable while showing enough context at both ends — aim for roughly 25 characters from the start and 20 from the end, joined with `...`:

```
ask_user_input_v0(questions=[
    {
        "question": "What is the video filename?",
        "type": "single_select",
        "options": [
            "<stem_start>...<stem_end>.mp4",
            "<stem_start>...<stem_end>.mov",
            "<stem_start>...<stem_end>.avi",
            "<stem_start>...<stem_end>.mxf",
            "<stem_start>...<stem_end>.mkv"
        ]
    },
    {
        "question": "Source duration calculated from transcript: <HH:MM:SS:FF> (<N> frames at <fps>fps). Is this correct?",
        "type": "single_select",
        "options": ["Yes, that's correct", "No, I'll type the correct frame count"]
    },
    {
        "question": "What is the video resolution?",
        "type": "single_select",
        "options": [
            "1920 \u00d7 1080 (16:9 HD)",
            "3840 \u00d7 2160 (16:9 4K)",
            "1280 \u00d7 720 (16:9 720p)",
            "1080 \u00d7 1920 (9:16 vertical)",
            "1080 \u00d7 1350 (4:5 portrait)",
            "1080 \u00d7 1080 (1:1 square)",
            "Custom"
        ]
    }
])
```

Rules:
- The full untruncated filename is used when assembling the final file path — truncation is display only
- If the user selects a button, extract the extension from the button label and combine with the full stem: `<full_stem>.<ext>`
- If the user types a custom filename in the text field, use that as-is
- If the user selects "No, I'll type the correct frame count", follow up with a plain text message: *"Please type the correct total frame count for your source video."*
- If the user selects a resolution button, parse the width and height from the numbers before and after `×`
- If the user selects **Custom**, follow up: *"Please type your resolution as `width x height` (e.g. `2560 x 1440`)."*
- Once folder path, filename, duration, and resolution are confirmed, assemble the full path as `<folder>\<filename>` and proceed to Step 8
- Frame rate is already confirmed in Step 2 — do not ask for it again here

**File path handling:** Pass the raw Windows path (e.g. `D:\My Project\Video (4K).mp4`) as the `path` field in the config JSON. The script handles all URL encoding internally — spaces become `%20`, drive colon becomes `%3a`, parentheses are left literal. Do not pre-encode the path.


### Step 8: Build config JSON and verify before export

Assemble the config JSON from all collected inputs:
- `fps` — from Step 2
- `source_frames` — from the Step 3 stderr summary line
- `soundbites` — the confirmed list from Step 6 (each with `in` and `out` as `HH:MM:SS:FF`)
- `filename`, `path` — from Step 7
- `width`, `height` — from Step 7 (default 1920×1080 if not provided)

Config format:
```json
{
    "filename":      "MyVideo (4K).mp4",
    "path":          "C:\\Users\\User\\Desktop\\MyVideo (4K).mp4",
    "fps":           25,
    "width":         3840,
    "height":        2160,
    "source_frames": 46293,
    "output":        "MyVideo (4K)_highlights.xml",
    "soundbites": [
        {"in": "00:03:08:05", "out": "00:03:18:21"}
    ]
}
```

**Required fields:** `filename`, `path`, `fps`, `source_frames`, `soundbites`

**Optional fields:** `width` (default 1920), `height` (default 1080), `output` (default: `<stem> Highlights.xml`, e.g. `MyVideo (4K) Highlights.xml`)

Then display a verification table so the user can confirm all values before export:

| # | In (TC) | Out (TC) | In (frames) | Out (frames) | Duration (frames) | Timeline start | Timeline end |
|---|---------|----------|-------------|--------------|-------------------|----------------|--------------|
| 1 | ... | ... | ... | ... | ... | 0 | ... |

Timecode conversion formulas:
- HH:MM:SS:FF → frames (NDF): `(HH×3600×fps) + (MM×60×fps) + (SS×fps) + FF`

The script handles pproTicks internally using: `frames × (254,016,000,000 ÷ fps)`. This is fps-dependent — do not hardcode a per-frame multiplier.

Show the assembled config JSON and the verification table together. Ask the user to confirm everything looks correct. If they request any amendments — correcting a timecode, changing the filename, adjusting source_frames, etc. — update the config and re-display the table until they approve. Only proceed to Step 9 once the user confirms.

### Step 9: Run the script and validate

Run the export:

```bash
python scripts/generate_xml.py --config config.json
```

The script writes the XML file automatically and prints a summary with soundbite count, sequence duration, and resolution.

The script runs its own internal validation. Additionally confirm:
- [ ] `<sequence duration>` = sum of all `(out_frame − in_frame)` values
- [ ] Each segment's `timeline_end` = next segment's `timeline_start`
- [ ] Total clipitems = N × 3 (video + 2 audio per segment) + 3 master clipitems

---

## Known Premiere Pro Behaviour

**Importing will always bring the source video in as a new project item**, even if the same file is already in the project. This is a limitation of XMEML — Premiere links by file path, not by matching existing project items. The duplicate clip points to the same file on disk so no extra storage is used. The user can safely delete the duplicate from the project panel after import and the sequence will keep working. Always mention this proactively so users are not surprised.


## Edge Cases

- **User gives seconds, not timecodes**: Convert with `round(seconds × framerate)`, format as `HH:MM:SS:FF` for the config
- **Adjacent sentences to merge**: Combine into one soundbite; use first sentence's Start and last sentence's End from the table as in/out
- **User selects by description**: Match semantically; confirm which segment numbers you matched before proceeding
- **Missing file path**: Never invent one — always ask
- **Missing total duration**: Never guess — always ask; it's needed for `<duration>` on the master clip

---

## Do Not

- Do not generate XML by hand — always use `scripts/generate_xml.py`
- Do not add transitions, effects, or colour grades unless asked
- Do not include every segment automatically — always wait for user selection
- Do not change default label colours (Iris/Forest/Mango) unless asked
- Do not pre-encode the file path — pass the raw Windows path; the script handles URL encoding
- Do not truncate the XML output
- Do not read or parse the raw JSON transcript — always use `scripts/summarize_transcript.py`