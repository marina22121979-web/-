---
name: davinci
description: DaVinci Resolve post-production assistant — read timelines, extract audio, transcribe, generate subtitles, color-mark clips by content keywords. Uses Python Scripting API with smart multi-track audio merging.
---

# DaVinci Resolve Skill

Automate documentary post-production workflows in DaVinci Resolve: timeline queries, audio extraction & transcription, subtitle generation, and transcript-driven clip color marking.

## Environment Setup

### Python Scripting API (Primary)

Environment variables (must be set before every script invocation):

```bash
export PYTHONPATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
```

**Prerequisites:**
- **DaVinci Resolve Studio** (paid version) — the free version does not support external scripting
- **macOS** — all paths and commands in this document are macOS-specific; Windows/Linux users need to adjust paths accordingly
- DaVinci Resolve must be running
- Preferences → System → General → External Scripting → set to **Local**
- **The target timeline must be open in DaVinci Resolve.** `GetCurrentTimeline()` only returns the currently active timeline. Always prompt the user: "Please open the timeline you want to process in DaVinci Resolve" before starting.

### PostgreSQL (Optional, Advanced)

Only needed for batch-querying project data without opening DaVinci Resolve. **For most workflows, the Python API is sufficient — no PostgreSQL setup required.**

```bash
# Connection template — fill in your credentials
PGPASSWORD="<your_password>" PGGSSENCMODE=disable \
  /Library/PostgreSQL/13/bin/psql -U postgres -h 127.0.0.1 -d <database_name>
```

- Default PostgreSQL version shipped with Resolve: **13**
- Each project library is a separate database

---

## Database Queries (Read-Only, Optional)

### List All Projects

```sql
SELECT "ProjectName", "LastModTimeInSecs"
FROM "SM_Project"
ORDER BY "LastModTimeInSecs" DESC LIMIT 20;
```

### List Timelines in a Project

```sql
SELECT t."Name", t."ModTimeInSecs"
FROM "Sm2Timeline" t
JOIN "SM_Project_Sm2Timeline" pt ON t."Sm2Timeline_id" = pt."DbAssociate"
WHERE pt."DbOwner" = '<project_uuid>'
ORDER BY t."ModTimeInSecs" DESC;
```

### List Clips in a Timeline (with File Paths)

```sql
SELECT i."Name", i."Start", i."Duration", i."In", i."MediaFilePath"
FROM "Sm2TiItem" i
JOIN "Sm2TiTrack" tr ON i."Sm2TiTrack_id" = tr."Sm2TiTrack_id"
JOIN "Sm2SequenceContainer" sc ON tr."Sm2SequenceContainer_id" = sc."Sm2SequenceContainer_id"
JOIN "Sm2Sequence" s ON sc."Sm2Sequence_id" = s."Sm2Sequence_id"
JOIN "Sm2Timeline" t ON s."Sm2Timeline_id" = t."Sm2Timeline_id"
WHERE t."Name" = '<timeline_name>'
ORDER BY i."Start";
```

### Query Track Structure

```sql
-- Sm2TiTrack.Type: 0 = video, 1 = audio
SELECT tr."Type", tr."Sm2TiTrack_id",
       (SELECT COUNT(*) FROM "Sm2TiItem" ii
        WHERE ii."Sm2TiTrack_id" = tr."Sm2TiTrack_id") as item_count,
       (SELECT ii."Name" FROM "Sm2TiItem" ii
        WHERE ii."Sm2TiTrack_id" = tr."Sm2TiTrack_id"
        AND ii."MediaFilePath" IS NOT NULL AND ii."MediaFilePath" <> ''
        LIMIT 1) as sample_name
FROM "Sm2TiTrack" tr
JOIN "Sm2SequenceContainer" sc ON tr."Sm2SequenceContainer_id" = sc."Sm2SequenceContainer_id"
JOIN "Sm2Sequence" s ON sc."Sm2Sequence_id" = s."Sm2Sequence_id"
JOIN "Sm2Timeline" t ON s."Sm2Timeline_id" = t."Sm2Timeline_id"
WHERE t."Name" = '<timeline_name>'
ORDER BY tr."Type", item_count DESC;
```

**Key notes:**
- Timeline name is in `Sm2Timeline."Name"` (not `TimelineName`)
- Join keys are `"DbAssociate"` / `"DbOwner"` (not UUID field names)
- `"Start"` field type is `character varying` — use `CAST(i."Start" AS bigint)` for comparisons
- `"In"` field corresponds to the Python API's `GetLeftOffset()` (source in-point, unit: frames)
- Results may have duplicates (one row per video track + audio track) — deduplicate as needed

---

## Python API Operations

### Connect to Resolve

```python
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()        # current project
# or
proj = pm.LoadProject('Project Name') # switch to a specific project
```

### Browse Media Pool Folders (Recursive)

```python
def find_folder(folder, name):
    if folder.GetName() == name:
        return folder
    for sf in folder.GetSubFolderList():
        result = find_folder(sf, name)
        if result:
            return result
    return None

mp = proj.GetMediaPool()
root = mp.GetRootFolder()
target = find_folder(root, 'Folder Name')
clips = target.GetClipList()
```

### Get Clip Properties

```python
clip.GetClipProperty('File Path')
clip.GetClipProperty('Duration')
clip.GetClipProperty('Type')
```

### Read Timeline Audio Track

```python
tl = proj.GetCurrentTimeline()
fps = float(tl.GetSetting('timelineFrameRate'))  # typically 23.976, 24, 29.97, etc.
items = tl.GetItemListInTrack('audio', 1)         # track index starts at 1
items_sorted = sorted(items, key=lambda x: x.GetStart())

for item in items_sorted:
    item.GetStart()          # absolute frame position on timeline
    item.GetDuration()       # clip duration (frames)
    item.GetLeftOffset()     # source in-point (frames)
    item.GetName()           # clip name
    item.GetMediaPoolItem().GetClipProperty('File Path')  # source file path
```

### Add Media Pool Clips to Timeline

```python
mp.SetCurrentFolder(target_folder)
mp.AppendToTimeline(clips)   # clips from GetClipList()
```

### Rename Tracks

```python
tl.SetTrackName('audio', 1, 'New Name')
tl.GetTrackName('audio', 1)
```

### Check Clip Enabled State

```python
items = tl.GetItemListInTrack('audio', track_num)
for item in items:
    if not item.GetClipEnabled():
        pass  # this clip is disabled, skip it
```

> **Important:** The database `Sm2TiItem."Flags"` field is NOT a disabled flag. Flags 0 and 2 indicate track linking state. Use the Python API's `GetClipEnabled()` instead.

### Batch Delete Clips (Ripple Delete)

> **Use with caution.** Boundary clips (partial overlap) may not be handled correctly. Always test on a duplicate timeline first. Get explicit confirmation from the user before executing.

```python
# IMPORTANT: re-read the timeline before each operation,
# because ripple delete shifts all subsequent clips' Start positions
items = tl.GetItemListInTrack('audio', 1)
items_sorted = sorted(items, key=lambda x: x.GetStart())

# Build cumulative time mapping
cumulative = 0.0
clip_map = []
for item in items_sorted:
    dur_sec = item.GetDuration() / fps
    clip_map.append({'item': item, 'start': cumulative, 'end': cumulative + dur_sec})
    cumulative += dur_sec

# Find clips fully within target range
to_delete = [c['item'] for c in clip_map
             if c['start'] >= t_start and c['end'] <= t_end]

# Batch delete in one call (avoids cascading timecode shifts)
tl.DeleteClips(to_delete, True)  # True = ripple delete
```

---

## Audio Extraction from Timeline

Extract audio clips from a timeline into a single WAV file, preserving the edit order.

> **⚠️ Multi-Track Handling (MUST READ)**
>
> Timelines typically have multiple audio tracks (e.g., A/B camera, dialogue/SFX). **Do NOT concatenate clips from all tracks sequentially** — parallel tracks play simultaneously on the timeline. Concatenating them would:
> 1. Duplicate the same dialogue (same words appear twice)
> 2. Break all timestamp mappings
> 3. Produce audio much longer than the actual timeline duration
>
> **Correct approach: merge by timeline position, not by track.**

### Step 1: Collect Enabled Clips from All Tracks

```python
import subprocess, os, tempfile

fps = float(tl.GetSetting('timelineFrameRate'))
track_count = tl.GetTrackCount('audio')

all_items = []
target_tracks = [1, 2]  # adjust based on actual needs

for track_num in target_tracks:
    items = tl.GetItemListInTrack('audio', track_num)
    for item in items:
        if item.GetClipEnabled():
            all_items.append({
                'item': item,
                'track': track_num,
                'start': item.GetStart(),
                'duration': item.GetDuration(),
                'left_offset': item.GetLeftOffset(),
                'file_path': item.GetMediaPoolItem().GetClipProperty('File Path'),
                'name': item.GetName()
            })
```

### Step 2: Deduplicate by Timeline Position

```python
all_items.sort(key=lambda x: x['start'])

merged_items = []
for item in all_items:
    start_sec = item['start'] / fps
    end_sec = start_sec + item['duration'] / fps
    
    overlaps = False
    for existing in merged_items:
        ex_start = existing['start'] / fps
        ex_end = ex_start + existing['duration'] / fps
        overlap_start = max(start_sec, ex_start)
        overlap_end = min(end_sec, ex_end)
        if overlap_end > overlap_start:
            overlap_ratio = (overlap_end - overlap_start) / min(
                end_sec - start_sec, ex_end - ex_start)
            if overlap_ratio > 0.5:
                overlaps = True
                break
    
    if not overlaps:
        merged_items.append(item)

merged_items.sort(key=lambda x: x['start'])
```

### Step 3: Extract and Concatenate

```python
tmp_dir = tempfile.mkdtemp()
concat_list = os.path.join(tmp_dir, 'concat.txt')
output_wav = '/tmp/merged.wav'

clip_mapping = []
merged_cumulative = 0.0

with open(concat_list, 'w') as f:
    for idx, item in enumerate(merged_items):
        src_file = item['file_path']
        start_sec = item['left_offset'] / fps
        dur_sec = item['duration'] / fps
        tl_start_sec = item['start'] / fps
        seg_path = os.path.join(tmp_dir, f'seg_{idx:03d}.wav')
        
        subprocess.run(['ffmpeg', '-y', '-i', src_file,
            '-ss', str(start_sec), '-t', str(dur_sec),
            '-ar', '16000', '-ac', '1', seg_path], capture_output=True)
        f.write(f"file '{seg_path}'\n")
        
        clip_mapping.append({
            'merged_start': merged_cumulative,
            'merged_end': merged_cumulative + dur_sec,
            'tl_start': tl_start_sec,
            'duration': dur_sec,
            'track': item['track'],
            'name': item['name']
        })
        merged_cumulative += dur_sec

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_list, output_wav], capture_output=True)

print(f"Extracted {len(merged_items)} clips, total {merged_cumulative:.1f}s")
```

### Verify Extraction Results

After extraction, check:
1. **Total duration should be close to timeline range** (e.g., 10 min target → result should be 500-600s; the gap is silence between clips)
2. **Clip count should be less than sum of all tracks** (dedup removed overlapping clips)
3. **clip_mapping tl_start should be monotonically increasing**

### Single-Track Simplified Version

If only one track is needed:

```python
items_sorted = sorted(tl.GetItemListInTrack('audio', 1), key=lambda x: x.GetStart())
items_enabled = [item for item in items_sorted if item.GetClipEnabled()]
# proceed with extraction, skip dedup step
```

---

## Transcription

> **Before each transcription, ask the user: "Fast processing or accurate transcription?"**
> - **Accurate transcription** → Volcano Engine Doubao Seed-ASR 2.0 (high accuracy, punctuation, good homophone disambiguation)
> - **Fast processing** → Local whisper-large-v3-turbo (fast, offline, but more typos)

**Transcription output storage:**
- Save transcripts to a project-specific directory: `/path/to/project/transcripts/<timeline_name>.md`
- Add frontmatter: `tags: [transcript]`
- Format: paragraph-style, merge consecutive utterances from the same speaker into one paragraph, separate speaker switches with blank lines (see A5/A6 below)

**Audio file archiving:**
- Archive exported audio files (wav, mp3) to the project folder: `/path/to/project/exports/transcription-audio/`
- Use the timeline name for filenames: `<timeline_name>_merged.wav`, `<timeline_name>_merged.mp3`
- **Before each transcription, check if the archive directory already has the corresponding audio file** — reuse it to avoid duplicate exports
- `/tmp/` is for temporary processing only; copy results to the archive directory when done

### Method A: Volcano Engine Doubao Seed-ASR 2.0 (Accurate Transcription)

> **⚠️ API Key Required:** Before starting cloud transcription, confirm the user has a Volcano Engine API Key configured. If not, prompt them before proceeding — do not wait until the submission fails.

**Credentials (new format, Seed-ASR 2.0):**
- API Key: `<your_api_key>`
- Resource ID: `volc.seedasr.auc`
- Auth: single `x-api-key` header (replaces the legacy `X-Api-App-Key` + `X-Api-Access-Key` method)

**Legacy credentials (deprecated, free quota exhausted):**
- ~~App Key: `<your_app_key>`~~
- ~~Access Key: `<your_access_key>`~~
- ~~Resource ID: `volc.bigasr.auc`~~

**Full Steps:**

#### A1. Convert to MP3 (reduce upload size)

```bash
ffmpeg -y -i /tmp/merged.wav -ac 1 -ar 16000 -b:a 64k /tmp/merged.mp3
```

#### A2. Upload to a Public URL

The Volcano Engine API requires an audio URL (no direct upload).

```bash
# uguu.se: free, supports up to 100MB, files retained for 48 hours
curl -s -F "files[]=@/tmp/merged.mp3" https://uguu.se/upload
# Returns JSON — use files[0].url
```

**Alternatives (if uguu is unavailable):**
1. Local HTTP server + cloudflared tunnel (`brew install cloudflared`)
   ```bash
   python3 -m http.server 18080 --directory /tmp &
   cloudflared tunnel --url http://localhost:18080
   # Use the returned trycloudflare.com URL
   ```
   Note: trycloudflare.com may be blocked in some regions — test first
2. Any object storage service (Aliyun OSS, Volcano TOS, AWS S3) — most reliable option

**File hosting gotchas (from real testing):**
- transfer.sh: inaccessible from China
- catbox.moe: upload timed out
- cloudflare tunnel (trycloudflare.com): upload succeeded but Volcano Engine server failed to download (`audio download failed`) — inaccessible from China-based servers
- uguu.se: upload succeeded, Volcano Engine downloaded successfully

#### A3. Submit Transcription Job

```bash
AUDIO_URL="<url_from_step_2>"
REQ_ID=$(uuidgen)

curl -s -X POST "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <your_api_key>" \
  -H "X-Api-Resource-Id: volc.seedasr.auc" \
  -H "X-Api-Request-Id: $REQ_ID" \
  -H "X-Api-Sequence: -1" \
  -d "{
    \"user\": {\"uid\": \"my-studio\"},
    \"audio\": {
      \"url\": \"$AUDIO_URL\",
      \"format\": \"mp3\"
    },
    \"request\": {
      \"model_name\": \"bigmodel\",
      \"enable_itn\": true,
      \"enable_punc\": true,
      \"enable_ddc\": true,
      \"show_utterances\": true,
      \"enable_speaker_info\": true
    }
  }"
```

- Success: header `x-api-status-code: 20000000`, body `{}`
- Save `$REQ_ID` for polling

#### A4. Poll for Results

```bash
# Single query (write headers to file, body to result file)
curl -s -D /tmp/vc_headers.txt -o /tmp/vc_body.json -X POST \
  "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <your_api_key>" \
  -H "X-Api-Resource-Id: volc.seedasr.auc" \
  -H "X-Api-Request-Id: $REQ_ID" \
  -d "{}"

# Extract status code (MUST match line start to avoid false match
# from access-control-expose-headers line)
STATUS=$(grep -i "^x-api-status-code:" /tmp/vc_headers.txt | awk '{print $2}' | tr -d '\r')
```

**Auto-polling script template:**

```bash
REQ_ID=$(cat /tmp/volcengine_reqid.txt)
for i in $(seq 1 20); do
  sleep 30
  curl -s -D /tmp/vc_headers.txt -o /tmp/vc_body.json -X POST \
    "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query" \
    -H "Content-Type: application/json" \
    -H "x-api-key: <your_api_key>" \
    -H "X-Api-Resource-Id: volc.seedasr.auc" \
    -H "X-Api-Request-Id: $REQ_ID" \
    -d "{}"
  STATUS=$(grep -i "^x-api-status-code:" /tmp/vc_headers.txt | awk '{print $2}' | tr -d '\r')
  echo "Poll $i: status=$STATUS"
  if [ "$STATUS" = "20000000" ]; then
    cp /tmp/vc_body.json /tmp/volcengine_result.json
    echo "DONE"
    break
  fi
done
```

- `20000001` = processing, keep polling (every 60 seconds)
- `20000000` = done, result in `/tmp/volcengine_result.json`
- Benchmark: 153 min audio ≈ **12 min** processing

#### A5. Result Format

```json
{
  "audio_info": {"duration": 9177840},
  "result": {
    "text": "Full transcript...",
    "utterances": [
      {
        "text": "Sentence text",
        "start_time": 95056,
        "end_time": 95126,
        "additions": {"speaker": "1"},
        "words": [{"text": "word", "start_time": 95056, "end_time": 95080}]
      }
    ]
  }
}
```

- Timestamps in **milliseconds**
- Includes punctuation
- Segmented into natural, complete sentences (not fragmented)
- Speaker info in `additions.speaker` (NOT `speaker_id` — that field always returns -1, useless)
- `additions.speaker` values are strings like `"1"`, `"2"`, consistent across the full audio
- Map speaker IDs to real names based on content of the first few sentences

#### A6. Output Format: Paragraph-Style Transcript

**Core rules:**
1. Merge consecutive utterances from the same speaker into a single paragraph; only insert line breaks (with blank line separation) when the speaker changes
2. **Pure filler word filtering**: the other party's brief responses like "uh-huh", "yeah", "right" should not trigger a speaker switch — skip them to avoid paragraph fragmentation
3. Mark the timestamp and speaker name at the beginning of each paragraph
4. Multiple speaker IDs may correspond to the same person (e.g., Speaker 2 and 3 are both the interviewer) — merge based on content analysis

**Format example:**
```
[00:07.89] [Interviewee] I grew up in a small town. My dad was from the countryside, my mom was from the city. Later I moved to the district for school. My grandfather was a farmer, my grandmother was a farmer. My dad was also from a farming background, I grew up in the countryside. But my mom was a city person. My maternal grandmother was an elementary school teacher.

[00:36.75] [Interviewer] I see. So what was your daily life like back then? What kind of environment did you grow up in?
```

**Processing logic:**

```python
import json, re

with open('/tmp/volcengine_result.json') as f:
    data = json.load(f)

utterances = data['result']['utterances']

# Map speaker IDs to names based on content analysis
# Note: Volcano Engine may split one person into multiple speaker IDs — merge as needed
# speaker_map = {"1": "Interviewee", "2": "Interviewer", "3": "Interviewer"}  # example

# Filler word regex: short interjections that shouldn't trigger speaker switches
FILLERS = re.compile(r'^[嗯啊哦呃对是好哈嘿噢欸呀吧嘛呢么]+[。，、！？,.!?]?$')

def is_filler(text):
    return bool(FILLERS.match(text.strip()))

paragraphs = []
current_speaker = None
current_texts = []
current_ts = None

for u in utterances:
    spk = speaker_map.get(u.get('additions', {}).get('speaker', '?'), 'Unknown')
    text = u['text']

    if current_speaker is None:
        current_speaker = spk
        current_texts = [text]
        current_ts = u['start_time']
        continue

    if spk == current_speaker:
        current_texts.append(text)
    else:
        if is_filler(text):
            continue  # pure filler — don't switch speaker
        else:
            if current_texts:
                ms = current_ts
                m, s = int(ms // 60000), (ms % 60000) / 1000
                combined = "".join(current_texts)
                if not is_filler(combined):
                    paragraphs.append(f'[{m:02d}:{s:05.2f}] [{current_speaker}] {combined}')
            current_speaker = spk
            current_texts = [text]
            current_ts = u['start_time']

# Handle last paragraph
if current_texts:
    ms = current_ts
    m, s = int(ms // 60000), (ms % 60000) / 1000
    combined = "".join(current_texts)
    if not is_filler(combined):
        paragraphs.append(f'[{m:02d}:{s:05.2f}] [{current_speaker}] {combined}')

transcript = '\n\n'.join(paragraphs)
```

#### A7. Speaker Label Verification (Human-Assisted Correction)

Volcano Engine's speaker diarization (ssd_version 200) has roughly 90% accuracy — key segments may be mislabeled. **A manual verification pass is required after generating the transcript:**

**Workflow:**
1. Read through the entire transcript, cross-referencing project background materials (research notes, pre-production docs)
2. Identify clearly mislabeled sentences in **narratively critical segments** (e.g., an interviewee's first-person story tagged as the interviewer)
3. List all suspected mislabeled paragraphs with reasoning, submit to the user for confirmation
4. Batch-correct after confirmation

**Common mislabeling patterns:**
- Interviewee's first-person narrative ("when I was young", "my dad", "my mom") tagged as the interviewer
- Interviewee reciting/explaining their own work tagged as the interviewer
- Interviewer's follow-up questions merged into the same paragraph as the interviewee's answer (needs splitting)
- Mislabeled casual chat or transition sentences can be ignored — prioritize the narrative backbone

**Output format (for user confirmation):**
```
Segments to confirm:

1. [timestamp] [original label] — "content excerpt..."
   → Should be [correct speaker] (reasoning)
```

---

### Method B: Local mlx-whisper (Fast Processing)

**Hardware requirements:**
- **Apple Silicon (M1 or later)**: mlx-whisper is optimized for Apple Neural Engine — recommended
- **NVIDIA GPU**: use the standard `openai-whisper` package with CUDA instead of mlx-whisper
- **CPU only**: works but extremely slow for long audio — consider cloud ASR instead

#### Install

```bash
pip3 install mlx-whisper --break-system-packages
```

#### Transcribe

```python
import mlx_whisper, re

result = mlx_whisper.transcribe('/tmp/merged.wav',
    path_or_hf_repo='mlx-community/whisper-large-v3-turbo',
    language='zh')  # change language as needed

# Output with timestamps, filtering known hallucinations
skip_exact = {'谢谢观看', '请不吝点赞订阅转发打赏支持明镜与点点'}  # add your own
for seg in result['segments']:
    text = seg['text'].strip()
    if not text or text in skip_exact:
        continue
    if re.search(r'[vé]{2,}', text, re.IGNORECASE):
        continue
    m, s = int(seg['start'] // 60), seg['start'] % 60
    print(f'[{m:02d}:{s:05.2f}] {text}')
```

First-time model download (China users may need a mirror):
```bash
HF_ENDPOINT=https://hf-mirror.com python3 your_script.py
# Model cached at ~/.cache/huggingface/hub/ after first download
```

---

### Method C: Aliyun Bailian FunASR (Accurate Transcription Alternative)

**Credentials:**
- API Key: environment variable `DASHSCOPE_API_KEY`
- Model: `fun-asr`

**Full Steps:**

#### C1. Upload Audio to a Public URL

Same as Method A steps A1-A2 (convert to MP3 + uguu.se upload).

#### C2. Submit Transcription Job

```bash
curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "fun-asr",
    "input": {
      "file_urls": ["'"$AUDIO_URL"'"]
    },
    "parameters": {
      "diarization_enabled": true,
      "speaker_count": 2,
      "language_hints": ["zh"]
    }
  }'
```

- Returns `output.task_id` for polling

#### C3. Poll for Results

```bash
TASK_ID="<task_id>"
curl -s -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY"
```

- `task_status: SUCCEEDED` means done
- Result URL is in `output.results[0].transcription_url` — download that URL to get the actual JSON

#### C4. Result Format

```json
{
  "file_url": "...",
  "properties": {"original_duration_in_milliseconds": 514510},
  "transcripts": [{
    "channel_id": 0,
    "text": "Full transcript...",
    "sentences": [{
      "begin_time": 120,
      "end_time": 7320,
      "text": "Sentence text with punctuation.",
      "speaker_id": 0,
      "words": [
        {"begin_time": 120, "end_time": 200, "text": "word", "punctuation": ","}
      ]
    }]
  }]
}
```

**Field mapping vs Volcano Engine:**

| Volcano Engine | Aliyun FunASR |
|---------|--------|
| `result.utterances` | `transcripts[0].sentences` |
| `utterance.start_time` | `sentence.begin_time` |
| `utterance.end_time` | `sentence.end_time` |
| `utterance.text` | `sentence.text` |
| `additions.speaker` | `sentence.speaker_id` |
| Punctuation embedded in text | Punctuation in separate `word.punctuation` field |
| English preserves capitalization | English all lowercase — needs post-processing |

---

### Method D: Tencent Cloud ASR (Accurate Transcription Alternative)

**Credentials:**
- SecretId + SecretKey (Tencent Cloud API keys, from [console](https://console.cloud.tencent.com/cam/capi))
- Auth method: TC3-HMAC-SHA256 signature (more complex than Volcano/Aliyun — recommend using the official SDK)

**Full Steps:**

#### D1. Submit Transcription Job

```bash
# Recommend using Python SDK (pip install tencentcloud-sdk-python) to simplify auth
# REST API example:
curl -X POST https://asr.tencentcloudapi.com \
  -H "Content-Type: application/json" \
  -H "X-TC-Action: CreateRecTask" \
  -H "X-TC-Version: 2019-06-14" \
  -H "X-TC-Region: ap-shanghai" \
  -H "Authorization: TC3-HMAC-SHA256 Credential=..." \
  -d '{
    "Url": "'"$AUDIO_URL"'",
    "EngineModelType": "16k_zh",
    "ChannelNum": 1,
    "ResTextFormat": 2,
    "SourceType": 0,
    "SpeakerDiarization": 1,
    "SpeakerNumber": 2
  }'
```

- `ResTextFormat`: 0 = plain text, 2 = word-level timestamps + punctuation, 3 = sentence-level segments (subtitle mode)
- Returns `Response.Data.TaskId`

#### D2. Poll for Results

```bash
curl -X POST https://asr.tencentcloudapi.com \
  -H "X-TC-Action: DescribeTaskStatus" \
  -H "X-TC-Version: 2019-06-14" \
  -H "Authorization: TC3-HMAC-SHA256 Credential=..." \
  -d '{"TaskId": 1393265}'
```

- `Status: 2` = done
- Result in `ResultDetail` array

#### D3. Result Format

```json
{
  "ResultDetail": [{
    "FinalSentence": "Sentence text",
    "StartMs": 120,
    "EndMs": 7320,
    "SpeakerId": 0,
    "Words": [
      {"Word": "word", "OffsetStartMs": 120, "OffsetEndMs": 200}
    ]
  }]
}
```

**Field mapping vs Volcano Engine:**

| Volcano Engine | Tencent Cloud |
|---------|--------|
| `result.utterances` | `ResultDetail` |
| `utterance.start_time` | `StartMs` |
| `utterance.end_time` | `EndMs` |
| `utterance.text` | `FinalSentence` |
| `additions.speaker` | `SpeakerId` |

**Note:** Tencent Cloud uses TC3 signature for auth, which is cumbersome to write manually with curl. Recommend using `pip install tencentcloud-sdk-python` via the SDK.

---

### Transcription Method Comparison

| | Volcano Engine Seed-ASR 2.0 | Aliyun Bailian FunASR | Tencent Cloud ASR | Local Whisper |
|---|---|---|---|---|
| **Speed** | 153 min → 12 min | 8.6 min → <15 s | Fast | 153 min → ~10 min |
| **Accuracy** | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★ |
| **Punctuation** | Yes (in text) | Yes (separate field) | Yes (ResTextFormat >= 2) | No |
| **Segmentation** | Natural complete sentences | Longer, more natural | Natural sentences | Fragmented |
| **English capitalization** | Preserves case | All lowercase | TBD | Partially preserves |
| **Timestamps** | Sentence-level (ms) | Sentence + word-level (ms) | Sentence + word-level (ms) | Segment-level (s) |
| **Speaker diarization** | Yes | Yes (enable in params) | Yes (enable in params) | No |
| **Auth complexity** | Low (single API Key) | Low (single API Key) | High (TC3 signature) | None |
| **Dependencies** | Network + public URL | Network + public URL | Network + public URL | Fully local |

**Volcano vs Aliyun accuracy comparison (real test, 8.6 min narration test):**
- Both get proper nouns wrong (brand names, people's names)
- Aliyun: better on some homophone distinctions, but English is all lowercase
- Volcano: worse on some homophones, but preserves English capitalization
- Conclusion: core transcription quality is comparable; both need reference material for proofreading

**Volcano vs Whisper typical error comparison (colloquial speech):**
- Volcano handles colloquial Chinese better overall — fewer homophone errors on informal speech, slang, and financial/business terminology
- Whisper makes more homophone substitution errors in context-dependent words
- Both benefit significantly from post-processing with reference materials

**Choosing a transcription method — ask the user first:**
1. What hardware do you have? (Apple Silicon, NVIDIA GPU, CPU only)
2. Do you need speaker diarization?
3. Is accuracy or speed the priority?
4. Do you have reliable internet access?

Based on answers: Apple Silicon + offline + speed → local Whisper; accuracy + diarization → Volcano/Aliyun/Tencent Cloud.

**Reference materials for best accuracy:**
- Load ALL available reference materials (scripts, project briefs, character research, chat logs) into context before proofreading
- Do not summarize or extract keywords — full context yields the best corrections
- The more background information available, the better the proofreading quality

---

## SRT Subtitle Generation

> **Not a default step after transcription.** Only generate SRT when the user explicitly requests subtitles.

Generate SRT subtitles directly from transcription results and import into DaVinci Resolve — no need for third-party subtitle editors.

### Subtitle Text Conventions

1. **No spaces between letters/numbers and Chinese characters**: `AI员工` (correct) not `AI 员工` (wrong); `5分钟` (correct) not `5 分钟` (wrong)
2. **Pronouns he/she/it must be contextually accurate**: Volcano Engine transcription outputs a generic pronoun — when generating subtitles, correct based on the referent (he/she for people, it for AI/software/devices). This is a high-frequency error; check every subtitle line
3. **Remove all punctuation**: subtitle text should not contain commas, periods, or other punctuation marks
4. **Do not split English words across lines**: when breaking lines, never split `YouTube` into `YouTu` / `be`

### 10-Step SRT Workflow

1. **Confirm target audio track and time range**
2. **Confirm line-break preferences**: ask the user for maximum characters per subtitle line (default: 18 Chinese character widths), and any other line-breaking requirements (e.g., prefer short lines, minimize breaks in long sentences)
3. **Estimate time and confirm**: based on audio duration, estimate total time needed (audio extraction + transcription wait + proofreading + generation), inform the user, and get confirmation before starting
4. **Filter disabled clips**: use Python API's `GetClipEnabled()` to skip disabled clips
5. **Extract enabled clip audio → Transcribe → Timestamp mapping → Generate SRT draft**
6. **Load ALL reference materials**: before proofreading, load the user's reference materials (narration scripts, project briefs, character research, chat logs, etc.) in full — do not summarize or extract keywords. The more complete the background, the more accurate the proofreading
7. **Auto-proofread**: with full reference material context, review each transcription line. Fix typos, homophones, pronouns (he/she/it), remove spaces between letters/numbers and Chinese, align proper nouns to script. Fix what you are sure about; leave uncertain items for the next step
8. **List uncertain items**: after proofreading, list ALL items you are not confident about for user confirmation, including but not limited to:
   - Uncertain pronouns (he/she/it)
   - Uncertain homophones or typos
   - Uncertain proper noun spellings
   - Potentially unnatural line breaks
   - Anything else you are not sure about
   Format: list each item with timestamp and context, wait for confirmation before producing the final version
9. **Align first subtitle to frame 0**: set the first subtitle's start time to `00:00:00,000` — only change the first entry, leave everything else as-is. Inform the user of the alignment and the original offset
10. **Deliver with instructions**: output the final SRT and remind the user: "After dragging into DaVinci Resolve, place the subtitle at the first frame of the timeline, then only adjust the first subtitle's in-point to align with the actual speech start — subsequent subtitles don't need adjustment"

### Timestamp Mapping (Merged Audio → Timeline)

```python
def merged_to_timeline(ms, clip_mapping):
    """Convert merged audio timestamp to timeline position."""
    t = ms / 1000.0
    for cm in clip_mapping:
        if cm['merged_start'] <= t < cm['merged_end']:
            offset = t - cm['merged_start']
            return (cm['tl_start'] + offset) * 1000
    last = clip_mapping[-1]
    return (last['tl_start'] + last['duration']) * 1000

def ms_to_srt_time(ms):
    h = int(ms // 3600000)
    m = int((ms % 3600000) // 60000)
    s = int((ms % 60000) // 1000)
    ms_r = int(ms % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms_r:03d}"
```

### SRT Generation with Smart Line Breaking

```python
import re

punct_re = re.compile(r'[，。！？、；：""''「」【】（）《》…—·,.?!;:]')
filler_re = re.compile(r'^[嗯啊哦呃对是好哈嘿噢欸呀吧嘛呢么]+$')
SOFT_MAX = 16   # prefer breaking within this limit
HARD_MAX = 18   # absolute max (adjust to your subtitle font size)

srt_entries = []
for u in utterances:
    text = u['text'].strip()
    clean = punct_re.sub('', text)
    if not clean or filler_re.match(clean):
        continue

    tl_start = merged_to_timeline(u['start_time'], clip_mapping)
    tl_end = merged_to_timeline(u['end_time'], clip_mapping)
    total_dur = tl_end - tl_start

    if len(clean) <= HARD_MAX:
        srt_entries.append({'text': clean, 'start': tl_start, 'end': tl_end})
        continue

    # Split by punctuation, then merge short clauses
    clauses_raw = re.split(r'[，。！？、；：…]+', text)
    clauses = [punct_re.sub('', c).strip() for c in clauses_raw]
    clauses = [c for c in clauses if c and not filler_re.match(c)]

    merged = []
    for c in clauses:
        if merged and len(merged[-1]) + len(c) <= HARD_MAX:
            merged[-1] += c
        else:
            merged.append(c)

    # Distribute time proportionally by character count
    total_chars = sum(len(c) for c in merged)
    if total_chars == 0:
        continue
    char_rate = total_dur / total_chars
    cum = 0
    for clause in merged:
        c_start = tl_start + cum * char_rate
        cum += len(clause)
        c_end = tl_start + cum * char_rate
        srt_entries.append({'text': clause, 'start': c_start, 'end': c_end})
```

**Line-breaking best practices (from real production use):**
- Use `display_width` for line width calculation: Chinese character = 1, English letter/digit = 0.5, max_width = 18 as the upper limit
- When merging short clauses, check total `display_width` not just character count
- **After removing punctuation, also remove spaces between letters/numbers and Chinese** — Volcano Engine transcription inserts spaces automatically
- English words must not be split: when force-splitting, split by tokens (full English words / single Chinese characters), not by character position
- Orphan line merging: lines with display_width <= 3 should be merged into the previous line

### Import SRT into DaVinci Resolve

1. Drag the `.srt` file into the DaVinci Media Pool
2. Drag from Media Pool onto a subtitle track in the timeline
3. Double-click subtitle entries on the timeline to edit text
4. After updating the SRT file externally, re-import with a new filename (e.g., `_v2.srt`) — Resolve doesn't watch for external file changes

> **Note:** `mp.ImportMedia(['/path/to.srt'])` works for importing into the media pool, but `AppendToTimeline` does not position subtitles by timecode correctly. Manual drag-and-drop is required.

### Key Lessons

**Checking if clips are disabled:**
- Database `Sm2TiItem."Flags"` is NOT a disabled flag. Flags 0 and 2 are track linking states — unrelated to disabled status
- **Must use Python API**: `item.GetClipEnabled()` (returns True/False)
- If the current timeline is the target timeline, reading is safe (won't switch anything)

```python
# Get disabled clips (Resolve must be on the target timeline)
items = tl.GetItemListInTrack('audio', track_num)
for item in items:
    if not item.GetClipEnabled():
        # this clip is disabled, skip it
        pass
```

**Multi-track structure in rough-cut timelines:**
- Typically two audio tracks for dual-camera interviews (A/B audio), switching between them
- The user will specify which track to use
- At the same position, one track may be enabled and the other disabled — this is normal A/B switching
- Music tracks, SFX tracks, etc. also exist — subtitles only need the dialogue track

**Volcano Engine vs subtitle editor quality comparison (real test on classical/literary content):**
- Volcano Engine significantly outperforms third-party subtitle editors on classical Chinese content, literary references, and historical terms
- Person name consistency is better with Volcano Engine (same name used throughout)
- Volcano Engine has full punctuation
- Third-party editors occasionally win on short colloquial phrases

---

## Color Marking Workflow

### Color Semantics (Define Per Project)

Example color scheme for a documentary project:

| Color | DaVinci Name | Meaning |
|-------|-------------|---------|
| Violet | `Violet` | Key narrative moment — cannot be compressed |
| Blue | `Blue` | Normal keep |
| Orange | `Orange` | Good quality, pending decision |
| Pink | `Pink` | Must pull back (recall from other timelines) |
| Chocolate | `Chocolate` | Suggest removal (resume-style narration, pure filler) |

### Set / Get Clip Colors

```python
item.SetClipColor('Violet')    # set color
item.GetClipColor()            # get current color (returns string)
```

Available colors: `Orange`, `Apricot`, `Yellow`, `Lime`, `Olive`, `Green`, `Teal`, `Navy`, `Blue`, `Purple`, `Violet`, `Pink`, `Tan`, `Beige`, `Brown`, `Chocolate`

### Keyword-Based Color Marking

Mark clips based on transcript content. Core pattern: reset all to a base color, then apply rules by priority.

```python
# 1. Build clip → transcript text mapping
cumulative = 0.0
clip_map = []
for item in items:
    dur_sec = item.GetDuration() / fps
    texts = [txt for t, txt in segments if cumulative <= t < cumulative + dur_sec]
    clip_map.append({
        'item': item, 'start': cumulative, 'end': cumulative + dur_sec,
        'dur': dur_sec, 'text': ' '.join(texts)
    })
    cumulative += dur_sec

# 2. Define keyword lists per color (customize for your project)
violet_kw = ['keyword1', 'keyword2']     # key narrative moments — must keep
chocolate_kw = ['keyword3', 'keyword4']  # filler content — suggest removal
keep_kw = ['exception1']                 # override: always keep as Blue

# 3. Apply colors by priority (highest first)
for c in clip_map:
    text, item = c['text'], c['item']

    if any(kw in text for kw in keep_kw):
        item.SetClipColor('Blue'); continue

    if any(kw in text for kw in violet_kw):
        item.SetClipColor('Violet'); continue

    if any(kw in text for kw in chocolate_kw):
        item.SetClipColor('Chocolate'); continue

    item.SetClipColor('Blue')
```

**Supplementary rules (example):**
- Clips after a certain timestamp (e.g., `c['start'] > 900`) that are long (`c['dur'] > 3`) and not marked Violet can be auto-marked Chocolate (late-stage resume-style narration)

### Range-Based Color Marking (Pullback)

Mark clips within specific time ranges — useful for flagging segments to pull from other timelines.

```python
pullback_zones = [
    ('Scene A', 8*60+35,  8*60+55),   # (label, start_sec, end_sec)
    ('Scene B', 5*60+0,   6*60+20),
    ('Scene C', 124*60+50, 125*60+25),
    ('Scene D', 113*60+55, 114*60+35),
]

# Build cumulative time mapping
cumulative = 0.0
clip_map = []
for item in items:
    dur = item.GetDuration() / fps
    clip_map.append({'item': item, 'start': cumulative, 'end': cumulative + dur})
    cumulative += dur

# Mark clips overlapping any target zone
for c in clip_map:
    for label, t_start, t_end in pullback_zones:
        if c['start'] < t_end and c['end'] > t_start:
            c['item'].SetClipColor('Pink')
```

### Safe Color Correction Pattern

When re-marking colors, existing same-colored clips may be unintentionally affected. Always reset first, then re-apply:

```python
# Step 1: Reset all Pink back to the base color (e.g., Orange)
for item in items:
    if item.GetClipColor() == 'Pink':
        item.SetClipColor('Orange')

# Step 2: Re-apply Pink only to target zones
for c in clip_map:
    for label, t_start, t_end in pullback_zones:
        if c['start'] < t_end and c['end'] > t_start:
            c['item'].SetClipColor('Pink')
```

**Lesson:** Before any batch color change, check whether the timeline already has clips of the target color to avoid unintended modifications.

---

## Known Limitations

| Operation | Status | Notes |
|-----------|--------|-------|
| Query project / timeline / clip info | ✅ | Database or API |
| Rename project / timeline | ✅ | API or database |
| Rename tracks | ✅ | `tl.SetTrackName('audio', 1, 'New Name')` / `tl.GetTrackName('audio', 1)` |
| Import SRT to media pool | ✅ | `mp.ImportMedia(['/path/to.srt'])` |
| Place SRT on subtitle track | ⚠️ | `AppendToTimeline` runs but ignores timecodes — must drag manually |
| Set subtitle formatting (font/size/color) | ❌ | `timelineSubtitleFont*` settings exist but are read-only; `SetSetting` / `SetProperty` return False (even after switching timelines) — only changeable in the GUI Inspector |
| Ripple delete clips | ⚠️ | Works but boundary handling is imperfect — test first, get user confirmation |
| Batch add clips to timeline | ✅ | `mp.AppendToTimeline(clips)` |
| Trim / modify in/out points | ❌ | Not exposed in API; database modification is risky |
| Split clips | ❌ | Not exposed in API |
| Read frame content | ❌ | Would need a separate frame export pipeline |
| Read/write color grading data | ❌ | Stored as bytea blobs in unknown format |

**Critical rules:**
- **Read from database, write through API** — queries (project info, timeline structure, clip paths) always use PostgreSQL (fast, no side effects); mutations (color marking, deleting clips, adding media) always use Python API
- **Never switch projects/timelines while Resolve is in active use** — `LoadProject()` and `SetCurrentTimeline()` change the GUI. Only use when the user explicitly permits it
- Ripple delete shifts all subsequent clips' `Start` positions — always re-read the timeline before the next operation
- Batch multiple deletes into a single `DeleteClips()` call
- Modifying the database while Resolve is running risks data being overwritten by Resolve's in-memory state
- Merged audio timestamps and timeline absolute timecodes require `LeftOffset` mapping — expect a few frames of error

---

## Gotchas (Lessons from Production Use)

### Finding Timeline Assets

**Scenario:** The user mentions asset names like "03 Hangzhou" or "version management" — these are **media pool folder names** or **timeline names** inside DaVinci Resolve, not filesystem directories.

**Lesson:** When a user mentions asset names in a project context, check the DaVinci project library first (database queries), not the filesystem.

### Process Name

```bash
# Wrong — no results
pgrep -x "DaVinci Resolve"

# Correct — process name is "Resolve"
pgrep -fl "Resolve"
# Path: /Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/MacOS/Resolve
```

### Schema Assumptions

Never assume database field names. When unsure, check the schema first:
```sql
\d "Sm2TiTrack"
```
For example, `"TrackIndex"` does not exist in `Sm2TiTrack` — attempting to query it will fail.

### Python API Switches the Active Timeline

**Scenario:** The user is editing timeline V1. You need to transcribe audio from timeline V0.

**Problem:** `pm.LoadProject('...')` + `proj.SetCurrentTimeline(target_tl)` **changes what's visible in the DaVinci Resolve GUI** — the user gets forcibly switched from V1 to V0, interrupting their work.

**Correct approach:** For read-only operations, use database queries exclusively:
```sql
-- 1. Find the project UUID
SELECT "SM_Project_id", "ProjectName" FROM "SM_Project" WHERE "ProjectName" = 'Project Name';

-- 2. Find timelines
SELECT t."Sm2Timeline_id", t."Name"
FROM "Sm2Timeline" t
JOIN "SM_Project_Sm2Timeline" pt ON t."Sm2Timeline_id" = pt."DbAssociate"
WHERE pt."DbOwner" = '<project_uuid>';

-- 3. Get clips with file paths
SELECT i."Name", i."Start", i."Duration", i."In", i."MediaFilePath"
FROM "Sm2TiItem" i
JOIN "Sm2TiTrack" tr ON i."Sm2TiTrack_id" = tr."Sm2TiTrack_id"
JOIN "Sm2SequenceContainer" sc ON tr."Sm2SequenceContainer_id" = sc."Sm2SequenceContainer_id"
JOIN "Sm2Sequence" s ON sc."Sm2Sequence_id" = s."Sm2Sequence_id"
JOIN "Sm2Timeline" t ON s."Sm2Timeline_id" = t."Sm2Timeline_id"
WHERE t."Name" = '<timeline_name>'
AND i."MediaFilePath" IS NOT NULL
AND i."MediaFilePath" <> ''
ORDER BY i."Start";
```

- Results will have duplicate rows (video track + audio track) — deduplicate as needed
- `"In"` field = Python API's `GetLeftOffset()` (source in-point, frames)
- For ffmpeg extraction: `-ss <In/fps>` `-t <Duration/fps>`
- **Note:** `"Start"` field type is `character varying` — use `CAST(i."Start" AS bigint)` for comparisons

**Rule:** When Resolve is running (process detected), do NOT use `LoadProject` or `SetCurrentTimeline`. Only use these when the user explicitly says "you can switch" or "I'm not using Resolve right now."

### SRT Subtitle Generation Gotchas

**Gotcha 1: Database Flags ≠ Disabled**
- `Sm2TiItem."Flags"` values (0, 2) indicate track linking/complementary state between A/B camera tracks — NOT clip enabled/disabled state
- **Correct approach:** Use Python API's `item.GetClipEnabled()`
- When the target timeline is the currently open timeline, API calls are safe (no project/timeline switching involved)

**Gotcha 2: Volcano Engine `words` Are Per-Character**
- The `words` array splits each Chinese character into a separate entry — it is NOT word-level segmentation
- Using word boundaries for line breaking is equivalent to breaking by character count — it will split words like "moreover" or "article" in the middle
- **Correct approach:** Use punctuation positions in the original text as break points, strip punctuation in output

**Gotcha 3: MAX_CHARS Too Small**
- Initial setting of 18 characters caused excessive forced word splitting
- Chinese subtitles: 22 characters is a reasonable upper limit (third-party subtitle editors default to ~20-24)
- Use `display_width` (Chinese = 1, English/digit = 0.5) for more accurate line width calculation

**Lesson: Confirm which audio track to use**
- Rough-cut timelines typically have multiple audio tracks with different content (dialogue vs music vs SFX)
- Always ask the user which track to use before extracting

### Timestamp Precision

Merged audio → timeline timestamp mapping has a few frames of error (~1-2 frames ≈ 33-66ms at 29.97fps). Acceptable for subtitles; may matter for frame-accurate operations.

### Timeline Start Timecode (Important — commonly confuses AI agents)

DaVinci Resolve timelines default to starting at `01:00:00:00`, NOT `00:00:00:00`. This means:

- `item.GetStart()` returns frame numbers that **include this offset**. A clip at the very beginning of the timeline returns `fps × 3600` (~86400 frames @24fps), not 0
- When a user says "first 10 minutes", they mean the first 10 minutes of **content**, not frames 0 to N

**Correct approach:**
```python
# Find the first clip's start position as the content origin
all_clips = []
for t in range(1, tl.GetTrackCount('audio') + 1):
    all_clips.extend(tl.GetItemListInTrack('audio', t))
content_start_frame = min(c.GetStart() for c in all_clips if c.GetClipEnabled())

# "First 10 minutes" = content_start_frame to content_start_frame + 10*60*fps
cutoff_frame = content_start_frame + int(10 * 60 * fps)
```

**Wrong approach:**
```python
# ❌ Starting from frame 0 — will find no content
cutoff_frame = int(10 * 60 * fps)  # = 14400 @24fps, but content starts at 86400
```
