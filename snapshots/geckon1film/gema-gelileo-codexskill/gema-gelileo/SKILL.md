---
name: gema-gelileo
description: Analyze Final Cut Pro 7 / DaVinci Resolve XMEML editing timelines and music metadata to produce GEMA-ready music usage records. Use when Codex needs to extract music clips from XML, calculate actual on-air duration without double-counting overlapping instances of the same audio file, preserve simultaneous usage of different tracks, match cue metadata, flag missing metadata, or prepare TITEL / INTERPRET / KOMPONIST / LABEL / VERW. DAUER tables.
---

# GEMA Gelileo

Create auditable music cue-sheet data from an XMEML timeline and an optional Markdown metadata list.

## Workflow

1. Run the bundled analyzer:

   ```bash
   python3 scripts/analyze_gema.py \
     --xml "/path/to/timeline.xml" \
     --metadata "/path/to/Music.md" \
     --output-dir "/path/to/output"
   ```

2. Read `analysis.json` as the source of truth.
3. Inspect `track_summary.csv` for per-file interval unions and removed overlaps.
4. Inspect `gema_cards.csv` or `report.md` for the card-ready result.
5. If an `.xlsx` workbook is requested, use the spreadsheets skill to create it from the CSV files. Include:
   - a fragment-level sheet;
   - a per-file summary sheet;
   - a GEMA card sheet containing every analyzed track.
6. Verify totals, missing metadata, and formatting before delivery.

## Duration Rules

- Treat timeline frames as half-open intervals: `[start, end)`.
- Use timeline `start` and `end` when both are non-negative.
- Resolve `-1` boundaries from the adjacent transition cut point.
  - `center`: midpoint of transition start/end;
  - `start`: transition start;
  - `end`: transition end.
- If one boundary is still unknown, derive it from `source out - source in`.
- Group intervals by exact media filename.
- Sort and union intervals for each filename.
- Merge when `next.start <= current.end`.
- Count overlapping or adjacent instances of the same filename only once.
- Keep different filenames independent even when they play simultaneously.
- Sum the lengths of the merged intervals to obtain actual usage duration.
- Round `VERW. DAUER (MM:SS)` only after the frame union, to the nearest second.
- Preserve an exact `MM:SS:FF` value for auditing.

Example at 25 fps:

```text
same.wav: [00:00:00:00, 00:00:03:00)
same.wav: [00:00:01:02, 00:00:22:03)
union:    [00:00:00:00, 00:00:22:03)
```

Do not add the overlap from `00:00:01:02` through `00:00:03:00` twice.

## Metadata Rules

- Match `Title`/`Titel` records to filenames case-insensitively.
- Accept German and English field labels supported by the script.
- Include every timeline track in the final GEMA table.
- When metadata is absent, keep the inferred title and filename, set `METADATA STATUS` to `INSUFFICIENT DATA`, and use `INSUFFICIENT DATA` for unavailable card fields.
- Never omit an unmatched track.
- Do not invent an artist, composer, label, publisher, ISRC, or catalog identifier.

## Quality Checks

- Confirm that `raw_frames - union_frames = overlap_removed_frames`.
- Confirm that each merged interval is disjoint from the next.
- Confirm that simultaneous different files retain their full individual durations.
- Confirm that the GEMA card row count equals the per-file summary row count.
- Call out all `INSUFFICIENT DATA` rows in the final response.

## Bundled Script

Use `scripts/analyze_gema.py`. It requires Python 3 and only the standard library.
