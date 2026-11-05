---
name: fcp-xml
description: Generate FCP 7 XML (xmeml v5) timelines from structured data using OpenTimelineIO (OTIO). Use when building a timeline to import into a professional editing app (Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro 7, etc.), iterating via round-trip (edit in chat → export XML → import to NLE → refine → export XML → parse back → iterate), or converting an edit decision list to FCP XML format. Covers OTIO usage plus post-processing fixes for format, video/audio linking, scale, speed, and transitions that OTIO's adapter doesn't handle. Round-trip workflow has only been tested with Adobe Premiere Pro.
allowed-tools: Bash Read Write Edit Glob
---

# fcp-xml

Generate and parse FCP 7 XML (xmeml v5) timelines for professional editing apps. Built on OpenTimelineIO (OTIO) as the in-memory model, with post-processing to work around OTIO's adapter quirks and FCP XML's requirements.

**Typical workflow**: agent drafts a timeline from structured data → writes FCP XML → user imports into their editor → refines visually → exports FCP XML back → agent parses with OTIO → iterate.

**Tested with Adobe Premiere Pro.** FCP 7 XML (xmeml v5) is also supported by DaVinci Resolve, Final Cut Pro 7, and others — the workflow should work with them but hasn't been verified. Specific quirks documented below ("Premiere imports clips at native resolution", etc.) are based on Premiere's behavior; other apps may differ.

## Before using this skill

- Source media **must have rotation baked in**. Most NLEs' FCP XML importers ignore Display Matrix rotation metadata (confirmed for Premiere). Use `/video-rotation-fix` first to normalize any rotated source files.
- Python 3.9-3.13 in a venv with `OpenTimelineIO-Plugins` installed.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install OpenTimelineIO OpenTimelineIO-Plugins
```

Verify the `fcp_xml` adapter is available:
```bash
.venv/bin/python3 -c "
import opentimelineio as otio
print('fcp_xml' in otio.adapters.available_adapter_names())
"
```

## Core OTIO API

Build a timeline in Python:

```python
import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

SEQUENCE_RATE = 30.0  # Must be SMPTE-compatible: 23.976, 24, 25, 29.97, 30, 50, 60
                      # Non-standard rates (e.g., 600/19 = 31.58) raise ValueError in fcp_xml

tl = otio.schema.Timeline(name="my_sequence")
v_track = otio.schema.Track(kind=otio.schema.TrackKind.Video, name="V1")
a_track = otio.schema.Track(kind=otio.schema.TrackKind.Audio, name="A1")
tl.tracks.append(v_track)
tl.tracks.append(a_track)

# One clip = video clipitem + audio clipitem (same media, same timing)
def add_clip(source_path, in_s, out_s, total_duration, label):
    rate = SEQUENCE_RATE
    media_ref = otio.schema.ExternalReference(
        target_url=f"file://{source_path}",
        available_range=TimeRange(
            RationalTime(0, rate),
            RationalTime(round(total_duration * rate), rate),
        ),
    )
    source_range = TimeRange(
        RationalTime(round(in_s * rate), rate),
        RationalTime(round((out_s - in_s) * rate), rate),
    )
    for track in (v_track, a_track):
        track.append(otio.schema.Clip(
            name=label,
            media_reference=media_ref,
            source_range=source_range,
        ))
```

Source paths must be absolute. Use `file://` URL scheme.

### Stills and silent timelines

`ffprobe` doesn't return a usable duration for images. For stills (PNG/JPG/HEIC), use PIL for dimensions and pass any large arbitrary value (e.g. 36000s) as `total_duration`. OTIO accepts any `source_range` within that fake range, so you can hold a still for any length:

```python
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.heic')

def probe(path):
    if path.lower().endswith(IMAGE_EXTS):
        from PIL import Image
        with Image.open(path) as img:
            w, h = img.size
        return w, h, 36000.0  # fake 10-hour duration — any large value works
    # video: ffprobe as usual
```

For silent timelines (gallery loops, ambient pieces), build only the video track — skip adding the audio track entirely. `fix_linking` then has nothing to match and no-ops silently, which avoids broken audio references for stills (which have no audio streams).

```python
v_track = otio.schema.Track(kind=otio.schema.TrackKind.Video, name="V1")
tl.tracks.append(v_track)
# no a_track at all
```

## Sequence format (essential — don't skip)

Without explicit format metadata, OTIO's adapter defaults to NTSC DV 720x480 with 10:11 pixel aspect ratio. Premiere then applies a weird 90.9% width scale to compensate. Always set the format explicitly via `timeline.metadata["fcp_xml"]`:

```python
SEQUENCE_WIDTH = 1080
SEQUENCE_HEIGHT = 1920  # 1080x1920 for 9:16 vertical, 1920x1080 for 16:9

tl.metadata["fcp_xml"] = {
    "media": {
        "video": {
            "format": {
                "samplecharacteristics": {
                    "width": str(SEQUENCE_WIDTH),
                    "height": str(SEQUENCE_HEIGHT),
                    "pixelaspectratio": "square",
                    "anamorphic": "FALSE",
                    "fielddominance": "none",
                    "rate": {"timebase": str(int(SEQUENCE_RATE)), "ntsc": "FALSE"},
                },
            },
        },
    },
}
```

The adapter reads this dict and injects matching XML elements under `<sequence>`.

## Write the XML

```python
otio.adapters.write_to_file(tl, "sequence.xml", adapter_name="fcp_xml")
```

This produces a valid xmeml v5 file, but with **four issues** that need post-processing fixes (see below).

## Post-processing fixes

After OTIO writes the XML, run the following fixes. See `scripts/build_xml.py` in this skill directory for the complete reference implementation. The fixes, in order:

### Fix 1: Reorder sequence children

When `timeline.metadata["fcp_xml"]` contains a `media` key, OTIO appends `<name>`, `<duration>`, `<rate>` *after* `<media>` instead of before. Reorder them:

```python
import xml.etree.ElementTree as ET
tree = ET.parse("sequence.xml")
root = tree.getroot()
for seq in root.iter("sequence"):
    children = list(seq)
    order = ["name", "duration", "rate", "in", "out", "timecode", "media"]
    children.sort(key=lambda e: order.index(e.tag) if e.tag in order else len(order))
    seq[:] = children
```

### Fix 2: Video/audio linking

OTIO writes audio clipitems as self-closing back-references sharing video IDs (`<clipitem id="clipitem-1"/>`). This does **not** create a link group in Premiere — clicking a video clip won't highlight its audio. Add explicit `<link>` elements to both.

For each video clipitem, match the audio clipitem by id, replace it with a full element that has a distinct id (e.g., `clipitem-1-a1`), then add two `<link>` elements to **both** video and audio clipitems — one pointing to the video, one to the audio, sharing a `groupindex`:

```python
import copy

for media in root.iter("media"):
    v_track_e = media.find("video/track")
    a_track_e = media.find("audio/track")
    video_clips = [c for c in v_track_e if c.tag == "clipitem"]
    audio_refs = [c for c in a_track_e if c.tag == "clipitem"]

    for idx, vclip in enumerate(video_clips):
        vid = vclip.get("id")
        aid = f"{vid}-a1"
        aref = next((c for c in audio_refs if c.get("id") == vid), None)
        if aref is None:
            continue

        # Build full audio clipitem by copying video clipitem
        aclip = copy.deepcopy(vclip)
        aclip.set("id", aid)
        aclip.attrib.pop("frameBlend", None)
        # File element becomes a reference only (no nested content)
        for fe in aclip.findall("file"):
            for child in list(fe):
                fe.remove(child)
        # Add sourcetrack marking this as audio channel 1
        st = ET.SubElement(aclip, "sourcetrack")
        ET.SubElement(st, "mediatype").text = "audio"
        ET.SubElement(st, "trackindex").text = "1"

        # Add link elements to both video and audio clipitems
        group = str(idx + 1)
        clip_idx = str(idx + 1)
        for target in (vclip, aclip):
            for old in target.findall("link"):
                target.remove(old)
            for link_id, mt in ((vid, "video"), (aid, "audio")):
                link = ET.SubElement(target, "link")
                ET.SubElement(link, "linkclipref").text = link_id
                ET.SubElement(link, "mediatype").text = mt
                ET.SubElement(link, "trackindex").text = "1"
                ET.SubElement(link, "clipindex").text = clip_idx
                ET.SubElement(link, "groupindex").text = group

        # Replace the self-closing ref with the full audio clipitem
        aref_idx = list(a_track_e).index(aref)
        a_track_e.remove(aref)
        a_track_e.insert(aref_idx, aclip)
```

### Fix 3: Basic Motion scale (scale-to-fit)

Premiere imports clips at native resolution, which means a 478x850 source appears as a tiny rectangle in a 1080x1920 sequence. Inject a Basic Motion filter with a computed scale value so clips fill the frame on import.

```python
def add_scale_filter(vclip, src_width, src_height, seq_width, seq_height):
    scale_pct = min(seq_width / src_width, seq_height / src_height) * 100.0  # scale-to-fit
    # Use max() instead of min() for scale-to-fill (crops edges)

    filter_e = ET.Element("filter")
    effect = ET.SubElement(filter_e, "effect")
    ET.SubElement(effect, "name").text = "Basic Motion"
    ET.SubElement(effect, "effectid").text = "basic"
    ET.SubElement(effect, "effectcategory").text = "motion"
    ET.SubElement(effect, "effecttype").text = "motion"
    ET.SubElement(effect, "mediatype").text = "video"
    ET.SubElement(effect, "pproBypass").text = "false"
    param = ET.SubElement(effect, "parameter", authoringApp="PremierePro")
    ET.SubElement(param, "parameterid").text = "scale"
    ET.SubElement(param, "name").text = "Scale"
    ET.SubElement(param, "valuemin").text = "0"
    ET.SubElement(param, "valuemax").text = "1000"
    ET.SubElement(param, "value").text = f"{scale_pct:.4f}"

    # Insert before any <link> elements (conventional ordering)
    insert_at = next((i for i, c in enumerate(vclip) if c.tag == "link"), len(list(vclip)))
    vclip.insert(insert_at, filter_e)
```

Get `src_width`/`src_height` via `ffprobe` on the source file at build time.

**Scale is preserved in round-trips** — if you write it in the XML, Premiere keeps it on export. But scale values Premiere adds *after* import (e.g., user drags the scale slider on a clip that had no scale filter) do **not** reliably survive export.

### Fix 4: Time Remap (speed)

Speed is NOT supported by OTIO — `LinearTimeWarp` effects are silently dropped by the fcp_xml adapter. Inject manually with a Time Remap filter. Apply to **both** video and audio clipitems (the speed value must match).

Speed value is a percentage: `200` = 2x playback (clip plays in half the timeline time), `50` = half speed (slow-mo, clip takes 2x timeline time).

```python
def add_speed_filter(clipitem, speed_pct, media_kind):
    filter_e = ET.Element("filter")
    effect = ET.SubElement(filter_e, "effect")
    ET.SubElement(effect, "name").text = "Time Remap"
    ET.SubElement(effect, "effectid").text = "timeremap"
    ET.SubElement(effect, "effectcategory").text = "motion"
    ET.SubElement(effect, "effecttype").text = "motion"
    ET.SubElement(effect, "mediatype").text = media_kind  # "video" or "audio"
    for pid, val, vmin, vmax in [
        ("variablespeed", "0", "0", "1"),
        ("speed", str(speed_pct), "-100000", "100000"),
    ]:
        p = ET.SubElement(effect, "parameter", authoringApp="PremierePro")
        ET.SubElement(p, "parameterid").text = pid
        ET.SubElement(p, "name").text = pid
        ET.SubElement(p, "valuemin").text = vmin
        ET.SubElement(p, "valuemax").text = vmax
        ET.SubElement(p, "value").text = val
    for pid in ("reverse", "frameblending"):
        p = ET.SubElement(effect, "parameter", authoringApp="PremierePro")
        ET.SubElement(p, "parameterid").text = pid
        ET.SubElement(p, "name").text = pid
        ET.SubElement(p, "value").text = "FALSE"

    insert_at = next((i for i, c in enumerate(clipitem) if c.tag == "link"), len(list(clipitem)))
    clipitem.insert(insert_at, filter_e)
```

**Important**: when you apply a speed effect, also shrink the clip's timeline position (`<start>`/`<end>`) to `source_duration / (speed/100)`. The source in/out stays the same; only the timeline duration changes.

**Limitations**: "Maintain audio pitch" is not in FCP XML format. Pitch tracks speed by default — if the user wants pitch preservation, they apply it manually in Premiere after import.

### Fix 5: Transitions (fade-to-black, cross dissolve)

Transitions are `<transitionitem>` elements placed on the track, *between* clipitems. They "steal" frames from adjacent clips (causing `start=-1` or `end=-1` on those clips).

```python
def build_transition(start_frame, end_frame, alignment, rate=30):
    """
    alignment: 'end-black' (fade out at end of preceding clip)
               'start-black' (fade in at start of following clip)
               'center' (cross dissolve between two clips)
    """
    t = ET.Element("transitionitem")
    ET.SubElement(t, "start").text = str(start_frame)
    ET.SubElement(t, "end").text = str(end_frame)
    ET.SubElement(t, "alignment").text = alignment
    r = ET.SubElement(t, "rate")
    ET.SubElement(r, "timebase").text = str(rate)
    ET.SubElement(r, "ntsc").text = "FALSE"
    effect = ET.SubElement(t, "effect")
    ET.SubElement(effect, "name").text = "Cross Dissolve"
    ET.SubElement(effect, "effectid").text = "Cross Dissolve"
    ET.SubElement(effect, "effectcategory").text = "Dissolve"
    ET.SubElement(effect, "effecttype").text = "transition"
    ET.SubElement(effect, "mediatype").text = "video"
    ET.SubElement(effect, "wipecode").text = "0"
    ET.SubElement(effect, "wipeaccuracy").text = "100"
    ET.SubElement(effect, "startratio").text = "0"
    ET.SubElement(effect, "endratio").text = "0"
    ET.SubElement(effect, "reverse").text = "FALSE"
    return t
```

**Note**: "fade in" / "fade out" in Premiere UI are not distinct effects from Cross Dissolve — they are Cross Dissolves with `alignment=start-black` / `end-black`. Premiere's translation report may say "Transition Cross Dissolve not translated, Cross Dissolve used instead" — this is a cosmetic warning, not a problem.

## Read FCP XML back (round-trip from the editor)

When the user exports FCP XML from their NLE (in Premiere: `File > Export > Final Cut Pro XML`), parse it with OTIO:

```python
tl = otio.adapters.read_from_file("exported.xml", adapter_name="fcp_xml")
for track in tl.tracks:
    for clip in track:
        if isinstance(clip, otio.schema.Clip):
            sr = clip.source_range
            tl_range = track.range_of_child(clip)
            # clip.name, sr.start_time.to_seconds(), sr.duration.to_seconds(), etc.
```

## Round-trip limitations

(Verified with Adobe Premiere Pro. Other NLEs may behave differently.)

**What survives a round-trip** (XML we generate → NLE → XML export):
- Clip identity (source file, in/out points)
- Clip order and timeline positions
- Video/audio linking
- Scale filter values we explicitly set
- Speed values we explicitly set
- Transitions we explicitly set

**What does NOT survive**:
- Default/native values the NLE adds after import (e.g., scale of a clip we didn't specify)
- "Maintain audio pitch" setting (not in FCP XML format)
- Color grading (Lumetri in Premiere, color page in Resolve, LUTs)
- Most effects beyond Basic Motion and Time Remap (unless explicit in original XML)
- Free-form labels/comments we put in OTIO metadata

**Design implication**: Use this skill for structure (which clips, which order, timing, speed, fades). Leave refinement (color, fine motion, advanced effects) to be applied inside the NLE. When you iterate the structure from chat, import the new XML into a new sequence; NLE-side refinements stay intact in the old sequence.

## Reference implementation

See `scripts/build_xml.py` for a complete working example that demonstrates all the fixes on a small sample timeline. Agents can copy and adapt this for their own clip lists and sequence parameters.

## Integration with other skills

- **Before using this skill**: run `/video-rotation-fix` on source media with rotation metadata (NLE FCP XML import ignores Display Matrix; rotated files will appear sideways)
- **For ffmpeg previews** of an OTIO timeline (quick chat-based iteration without opening the NLE): see `/ffmpeg-editing` — can render from the same clip list
- **High-level workflow**: see `/video-editing` for when to use this skill vs. ffmpeg-only rendering
