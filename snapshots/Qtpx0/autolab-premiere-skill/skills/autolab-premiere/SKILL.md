---
name: autolab-premiere
version: "1.8.3"
description: "Official bilingual (TH/EN) control skill for AutoLab CEP Extension (38 AutoLab UI, pipeline & production tools · 41 with aliases) and Adobe Premiere Pro MCP (434 native timeline/project tools · v1.24.1). Use whenever the user asks to inspect Premiere Pro bins/movies, run Auto Highlights, load clips into Auto Frame Queue, assign .mogrt Frames & Promo banners per bin, tune frame scale/position ('🎯 จัดกรอบ') with AI Vision PNG verification, run AI Auto-Name (Variety mode), run Name Refiner ('✂️ ย่อชื่อที่ยาว' + '✅ Apply All'), run the single-call high-speed af_pipeline, batch-export sequences to Adobe Media Encoder, manage Premiere Pro bins/items, or build a personalized production workflow skill."
---

# AutoLab & Adobe Premiere Pro Autonomous Control Skill (`autolab-premiere`)
# คู่มือมาตรฐานการควบคุม AutoLab (38 Tools · 41 Aliases) และ Adobe Premiere Pro (434 Tools) แบบไร้คนคุม 100%

> [!NOTE]
> **🔄 AUTOMATIC SKILL VERSION SYNC, DEV SHIELD & EXISTING USER MIGRATION PROTOCOL:**
> 1. **Skill Version:** `1.8.3` (จับคู่กับ AutoLab CEP Extension v1.8.2+)
> 2. **Dev Machine Shield (Zero Self-Overwrite):** หากตรวจพบว่ากำลังรันอยู่ในเครื่อง Dev / Maintainer (มีโฟลเดอร์ `G:\Dev\autolab-premiere-skill` อยู่บน Disk) ➔ **ห้ามรันคำสั่งดาวน์โหลดจาก GitHub มาทับเด็ดขาด** ให้ยึดไฟล์ซอร์สโค้ดที่กำลังพัฒนาในเครื่องเป็นความจริงสูงสุด 100%
> 3. **Production User Auto-Update & Non-Destructive Personal Skill Migration (สำหรับคนใช้ก่อนๆ):**
>    - เมื่อเรียก `autolab_get_status` และพบว่า `latestSkillVersion` สูงกว่าเลขเวอร์ชันในสกิลนี้ ให้ AI รันคำสั่ง `npx skills add https://github.com/Qtpx0/autolab-premiere-skill --skill autolab-premiere --force` ในพื้นหลังเพื่ออัปเดตสกิลกลางอัตโนมัติ
>    - **การอัปเกรดสกิลประจำตัวและ `GEMINI.md` ของคนใช้ก่อนๆ (Non-Destructive Surgical Patch):** หากผู้ใช้สร้างสกิลประจำเครื่องไว้ก่อนหน้านี้แล้ว (เช่น `my-premiere-production-workflow`) และยังไม่มีป้าย `ruleVersion: "1.8.3"` ให้ AI **ใช้ `edit_file` อัปเกรดเฉพาะหัวข้อกฎ Engine มาตรฐาน** (เช่น กฎเช็คสต็อก 1 คำสั่งจบ `< 1s` `lowStockThreshold: 25, scanPremiere: true`, ห้ามเรียก `pr_bin_tree`/Shell ตอนเช็คสต็อก, กฎตาราง `Standard Stock Dashboard Table`, กฎ `Central Raw Pool ➔ Work Bin` พร้อม 1-Call JSX Fuzzy Import จาก `rawDiskRoot`, ห้ามอ่านไฟล์ `.json` schema, และ `autoFit: true`) พร้อมอัปเดตไฟล์ `GEMINI.md` และ `mcp/autolab/instructions.md` ให้เป็นเวอร์ชันล่าสุดทันที **โดยห้ามลบหรือเขียนทับพาธโฟลเดอร์ส่วนตัวและตารางจับคู่ป้ายโปรโมทของผู้ใช้เด็ดขาด!** (ดูรายละเอียดใน [`references/06-personal-workflow-skill-builder-guide.md`](references/06-personal-workflow-skill-builder-guide.md))

สกิลนี้เป็นคู่มือปฏิบัติการหลักสำหรับเอเจนต์ AI ทุกค่าย (Claude, Cursor, Codex, Antigravity, Windsurf, DeepSeek Harness, OpenClaw) ในการควบคุม **AutoLab CEP Extension** ร่วมกับ **Adobe Premiere Pro** ผ่านสะพานเชื่อมคู่ขนานในเครื่อง (`AutoLab/js/core/mcp_bridge.js` ที่พอร์ต `17890` และ `%TEMP%\premiere-mcp-bridge`):

1. **`autolab` MCP (`38 Tools · 41 with aliases`)** — ควบคุมทุกหน้าจอ ทุกปุ่ม และทุกคิวงานของโปรแกรม AutoLab โดยตรงด้วยความเร็ว `1–7ms` (`Auto Highlights`, `Auto Frame Queue`, คำสั่งรวบยอดความเร็วสูง `af_pipeline`, `🎯 จัดกรอบ Live Frame Tuner`, `✨ AI Auto-Name`, `💬 Name Refiner ✂️ ย่อชื่อที่ยาว`, `START Batch`, ตรวจสอบ Bin & ตรวจจับเลขตอน `pr_inspect`, ส่องผัง Bin กะทัดรัด `pr_bin_tree`, สร้าง Bin แบบ `mkdir -p` `pr_create_bin`, ย้ายคลิปพร้อมสร้างโฟลเดอร์ปลายทาง `pr_move_item`, ลบ Bin & รูด Sequence ไฮไลท์ทิ้งยกชุด `pr_delete_bin`, เตรียมโฟลเดอร์ `pr_prepare_ep`, และส่งคิว `pr_export_ame`)
2. **`premiere-pro` MCP (`434 Tools · v1.24.1`)** — ควบคุม Adobe Premiere Pro เชิงลึก (สำรวจโปรเจกต์/Bin, จัดการ Sequence/Track, ตัดต่อคลิป, ปรับขนาด/ตำแหน่ง, ใส่เอฟเฟกต์/สี Lumetri, ปรับแต่งเสียง/คีย์เฟรม, มาร์กเกอร์/ซับไตเติล, แคปภาพหน้าจอ Program Monitor และส่งออกไฟล์ผ่าน Media Encoder)

> [!CAUTION]
> **🛡️ IRONCLAD OPERATOR & AUTONOMOUS CHAINING PROTOCOL (ZERO CODE READING / ZERO HESITATION):**
> 1. **Operator Only:** When executing Premiere operations (Auto Frame, Highlights, Queues), the Agent is strictly an **OPERATOR**. It is STRICTLY FORBIDDEN to read `AutoLab/js/**` source files or inspect implementation code before/after calling tools. Never write manual regex or inspect internal AutoLab CEP extension files. However, using `autolab_call_jsx` for Premiere Pro project DOM mutations/state repair (such as moving clips with `clip.moveBin()`) is 100% encouraged when high-level tools do not cover the task.
> 2. **Multi-Bin Native Queueing & Category-Aware Speed Partitioning:** Both **Auto Highlights** (`autolab_ah_queue_add` with `binNames: [...]`) and **Auto Frame** (`autolab_af_pipeline` with `bins: [...]`), as well as `autolab_pr_inspect({ queries: [...] })`, `autolab_pr_prepare_ep({ items: [...] })`, and `autolab_pr_export_ame({ items: [...] })`, natively support processing **multiple shows/bins at once in a single call**. NEVER ask "จะเริ่มเรื่องไหนก่อน" or process shows one-by-one when the user asks to process multiple shows of the same category!
>    - **🚨 Category-Aware Batch Partitioning (Auto Highlights Speed Isolation):** เนื่องจากค่า Speed Assist ใน Auto Highlights เป็นค่า Engine รวมทั้งคิว (`ah_configure`) หากผู้ใช้สั่งตัดหลายเรื่องพร้อมกันที่มีทั้ง **งานหนัง/ซีรีส์ (เปิด Speed 1.15×)** และ **งานรายการทีวี (ปิด Speed)** ห้ามเทรวมคิว AH เดียวกันเด็ดขาด (เพราะจะทำให้สปีดเสียงตีกัน)! ให้ AI ทำการแบ่งกลุ่มรัน Auto Highlights แยกตามสูตรสปีดอัตโนมัติ (เช่น รันกลุ่มหนังที่เปิด Speed ให้เสร็จก่อน ➔ สลับ Preset ปิด Speed ➔ แล้วรันกลุ่มรายการต่อ) โดยทำต่อเนื่องรวดเดียวจนจบโดยไม่ต้องหยุดถาม!
> 3. **End-to-End Autonomous Execution:** When the user orders to cut/export (e.g. *"ถ้ามีก็ตัดให้เลย"*, *"ตัดเรื่อง...ให้ด้วย"*), execute the modular steps continuously from start to finish (`pr_inspect` ➔ `pr_prepare_ep` ➔ `ah_configure` + `ah_queue_add` + `ah_run` ➔ `af_pipeline` ➔ `pr_export_ame`) **without stopping to ask permission between steps**. If destination folder on Disk does not exist yet (new show / first cut), create it immediately or let `pr_export_ame` create it automatically — NEVER stop to ask permission to create a folder!

---

## 🔥 0. ท่าฉุกเฉินและงานยืดหยุ่น (ห้ามบอกว่าทำไม่ได้เด็ดขาด — State Repair via `autolab_call_jsx`)

ปุ่มสำเร็จรูป (`af_pipeline`, `pr_prepare_ep`) คือทางลัดของ Standard Flow เท่านั้น **ไม่ใช่ขอบเขตความสามารถของระบบ**

หากเจองานจัดการเฉพาะจุด (เช่น ย้ายคลิปกลับ, จัดการ Bin แปลกๆ, แก้ไข Sequence เฉพาะหน้า):

- ❌ **ห้ามอ้างว่า "ไม่มีปุ่ม / ไม่มี API / design gap"**
- ❌ **ห้ามข้ามไปใช้ `premiere-pro-mcp`** (ที่มีปัญหา Guard และขยะล้น)
- ✅ **ต้องใช้ `autolab_call_jsx` เขียน ExtendScript ตรงสั่ง Premiere Pro ทันที** — `clip.moveBin()`, `bin.children`, ฯลฯ Adobe ทำได้ทุกอย่าง

**ตัวอย่างท่าฉุกเฉินที่ใช้บ่อย:**

```javascript
// ย้ายคลิปกลับ Bin (ไม่ต้อง nodeId, ไม่ผ่าน Guard)
var root = app.project.rootItem;
function findBin(node, name) {
  for (var i = 0; i < node.children.numItems; i++) {
    var c = node.children[i];
    if (c.type === ProjectItemType.BIN && c.name === name) return c;
    var f = findBin(c, name); if (f) return f;
  }
  return null;
}
var roBin = findBin(root, "รอ");
// เดินหาคลิปแล้วสั่ง moveBin
// clip.moveBin(roBin);
```

**กฎกำกับ:**
1. `autolab_call_jsx` **ไม่นับเป็น**การ "อ่านโค้ด implementation" ตาม CAUTION ข้อ 1 — ใช้ซ่อมและจัดการ project state ได้เสมอ
2. ยิง JSX แล้ว error แปลก → **หยุดถามผู้ใช้ 1 บรรทัด** ห้ามเดาซ้ำ
3. งานที่แตะ project state (ย้าย/ลบ/เปลี่ยน Bin) ถ้าไม่มั่นใจ → **ถามก่อน 1 บรรทัด**

---

## 🚨 1. กฎเหล็กห้ามฝ่าฝืน (Non-Negotiable Operational Rules)

1. **ห้ามใช้เครื่องมือดิบของ Premiere Pro สร้างงานแทนคิว AutoLab (Never Reinvent AutoLab Queue with Raw Premiere Tools):**
   - เมื่อผู้ใช้สั่งตัดไฮไลท์หนัง, นำคลิปเข้าคิวใส่กรอบ `.mogrt`, จัดกรอบ, ตั้งชื่อคลิป หรือสร้างซีเควนซ์คลิปสั้น **ต้องใช้เครื่องมือตระกูล `autolab_*` เสมอ** ห้ามไปเรียก `create_sequence` หรือ `import_mogrt` ของ `premiere-pro` มาต่อเองทีละอันเด็ดขาด
2. **ห้ามเปิด `AutoCut` สำหรับงานตัดไฮไลท์หนัง/ละคร/ซีรีส์เด็ดขาด (`autoCutState: 0`):**
   - `AutoCut` ใช้สำหรับงานตัดข่าวพูดคนเดียวเท่านั้น สำหรับงานหนัง/ละคร/รายการวาไรตี้ ต้องตั้ง `autoCutState: 0` ใน `autolab_af_configure_topbar` เสมอ
3. **ค่าป้ายโปรโมทมาตรฐานของ AutoLab คือ `เริ่มวิที่ 5 - ลูป 0 (ลากจนจบคลิป)` (`promoStart: 5`, `promoInterval: 0`):**
   - ห้ามตั้ง `20 - 20` โดยพลการ หากผู้ใช้ไม่ได้ระบุค่าอื่น ให้ใช้ `promoStart: 5` และ `promoInterval: 0` เสมอ
4. **โหมดตั้งชื่อ AI ต้องเป็น `🎭 Variety` (`mode: "variety"`) เสมอสำหรับงานบันเทิง:**
   - ห้ามใช้โหมด `📰 News` (`"news"`) กับงานหนัง/ละคร/ซีรีส์เด็ดขาด
5. **หลังกด `✨ AI Auto-Name` ต้องตามด้วย `💬 Name Refiner` ➔ `✂️ ย่อชื่อที่ยาว` ➔ `✅ Apply All` เสมอ:**
   - เรียก `autolab_af_run_name_refiner` (หรือเปิด `autoRefine: true` / ใช้ `autolab_af_pipeline`) เพื่อคัดกรองชื่อพาดหัวที่ยาวเกิน **17 ตัวอักษรไทย (`FILTER_CAP = 17`)** มาสั่งย่อให้กระชับไม่ล้นกรอบ `.mogrt`
6. **ใช้คำสั่งรวบยอด `autolab_af_pipeline` ได้ทั้งกรณีมี `Master Profile` และไม่มี `Master Profile` (มีระบบ Auto-Fit วัดกรอบ+ตัดขอบดำในตัว):**
   - แทนที่จะแยกเรียกทีละคำสั่งให้เสียเวลารอ LLM 6–7 รอบ ให้ใช้ `autolab_af_pipeline` คำสั่งเดียว ซึ่งจะดึงคลิปเข้าคิว (พร้อมบล็อก Sub-bin `ไฟล์ต้นฉบับ`), ผูกพรีเซ็ต/กรอบ, **วัดช่องใส `.mogrt` + สแกนขอบดำวิดีโอ 3 ช่วงเวลา (`cropdetect`) คำนวณ `scale / posX / posY` ระดับพิกเซลให้อัตโนมัติ (เมื่อระบุ `frame` โดยไม่มี `profileName`/`scale` หรือตั้ง `autoFit: true`)**, ตั้งค่า Topbar `5 - 0`, รัน `✨ AI Auto-Name`, รัน `💬 Name Refiner` ย่อชื่อ และกด `START` ต่อเนื่องทันทีแบบ `0ms` Latency!
7. **การวัดและจัดกรอบอัตโนมัติ (`autolab_af_tuner_auto_fit`) สำหรับเรื่องที่ไม่มีพรีเซ็ต — ห้ามเดาค่าสเกลเอง และไม่ต้อง Hardcode ค่าใดๆ:**
   - คลิปแต่ละเรื่องมีขนาดไฟล์และขอบดำบน/ล่างที่ฝังอยู่ในเนื้อวิดีโอ (Hardcoded Letterbox) ไม่เท่ากัน ต่อให้เป็น `1920x1080` เหมือนกันก็อาจมีขอบดำข้างในไม่เท่ากัน และกรอบ `.mogrt` แต่ละแบบมีช่องใสไม่เท่ากัน
   - ห้ามเดาตัวเลข `scale` / `posY` หรือใส่ `targetWindowWidth` ตายตัวเด็ดขาด ให้เรียก `autolab_af_tuner_auto_fit({ "binKey": "*" })` ระบบจะแกะ `thumb.png` ใน `.mogrt` วัดช่องใสจริง + สแกนพิกเซลวิดีโอ 3 ช่วงเวลา (`120s`, `360s`, `720s`) เพื่อเช็คว่ามีขอบดำหรือไม่ (`hasBlackBars: true/false`) แล้วคำนวณและบันทึก `scale`, `posX`, `posY` ลงคิวทันทีใน `~0.2–0.4 วินาที` (หากต้องการเรนเดอร์ภาพ `.png` ออกมาตรวจด้วยตา AI Vision ให้ส่ง `"preview": true`)
8. **ห้ามส่งชื่อป้ายโปรโมทแบบย่อหรือกำกวมเข้า MCP เด็ดขาด (Exact Template Name & Shared-Machine Multi-Promo Routing):**
   - เครื่องของผู้ใช้/พนักงานมักมีป้ายโปรโมทหลายตัวในแบรนด์เดียวกัน (เช่น แยกตามหมวดงาน `Show_Promo_A`, `Movie_Promo_A` หรือแยกตามพนักงานหลายคนที่ใช้คอมเครื่องเดียวกัน เช่น `_Team1`, `_Team2`)
   - ระบบกลาง MCP จะ **ปฏิเสธคำค้นที่กำกวมทันที (`Ambiguous promo template`)** เพื่อป้องกันการใส่ป้ายโปรโมทผิดเพจ/ผิดคน
   - ดังนั้นเมื่อผู้ใช้พูดชื่อแบรนด์สั้นๆ **AI ต้องตรวจสอบตารางจับคู่โปรโมในสกิลประจำเครื่องของผู้ใช้ (หรือดูจาก `autolab_list_templates` + หมวดหมู่ Bin/โฟลเดอร์)** แล้วแปลงเป็น **ชื่อไฟล์เต็มเป๊ะ (เช่น `"Movie_Promo_Team1"` หรือ `"Movie_Promo_Team2"`)** ก่อนส่งเข้า `autolab_af_set_bin_template` หรือ `autolab_af_pipeline` เสมอ!
9. **กฎเหล็กเอเจนต์ทำงานความเร็วสูงควบคู่การตรวจสอบคุณภาพ (High-Speed & Intelligent Quality Audit Protocol):**
   - **เอเจนต์ไม่ใช่สคริปต์ตาบอด:** ห้ามยิงคำสั่งทิ้งขว้างโดยไม่ตรวจสอบผลลัพธ์ และห้ามมัวแต่นั่งงมอ่านโค้ดทีละบรรทัดจนช้าเป็นนาที
   - **การทำงานต้องแบ่งเป็น 2 เฟส จบใน 1–2 วินาที:**
     - **Phase 1: Ultra-Fast Execution (< 500ms):** สั่งงานผ่าน `autolab_af_pipeline` (หรือ Native Tools) แบบ One-shot คำสั่งเดียวจบ
     - **Phase 2: Intelligent Quality Audit (~100ms):** ตรวจสอบ 4 Checkpoints คุณภาพทันที:
       1. `allBinsHaveTemplates === true` (เทมเพลตและโปรโมเข้าครบทุกคลิป 100%)
       2. `scale` อยู่ในเกณฑ์มาตรฐาน (`150%–180%`) และสแกนตัดขอบดำสำเร็จ (`cropAnalysis.hasBlackBars`)
       3. `longClipsOver17Chars === 0` (ชื่อคลิปไม่ยาวเกิน 17 ตัวอักษร ไม่ล้นกรอบโปรโม)
       4. `duration > 0s` (ฟุตเทจสมบูรณ์ ไม่มีคลิปเสีย)
     - **รายงานผล:** สรุป Compact Audit Card 3 บรรทัดพร้อมตัวเลขจริงให้ผู้ใช้เห็นทันที!
10. **ระบบล้างรหัสฉากอัตโนมัติ (Zero Leaked S-Prefixes):**
   - **รหัสฉากต้องไม่หลุดไปหน้าจอ:** ชื่อดิบจาก Auto Highlights มี `S01_`, `S04_` ติดมาเสมอ ระบบ Core Engine จะทำการดักตัดคำนำหน้า `S01..S99` ทิ้งอัตโนมัติทันทีที่เข้าคิว
   - **ห้ามข้าม Auto-Name:** ในคำสั่ง `autolab_af_pipeline` จะล็อคให้รัน `✨ AI Auto-Name` พ่วง `✂️ Name Refiner` อยู่ในวงจรเสมอ เพื่อเปลี่ยนชื่อดิบให้กลายเป็นพาดหัวภาษาไทยที่น่าสนใจและยาวไม่เกิน 17 ตัวอักษรเสมอ 100%
11. **Central Raw Pool ➔ Work Bin Routing (คลังฟุตดิบรวม ➔ Bin ทำงานแยกเพจ/ตอน):**
   - **คลังฟุตดิบกลาง (`Raw Pool`):** ฟุตดิบของเรื่องจะพักรวมไว้ที่ `<ชื่อเรื่อง>/รอ` เสมอ (เช่น `<ชื่อเรื่อง>/รอ`, `<หมวด>/<ชื่อเรื่อง>/รอ`)
   - **Work Bin ประจำเพจ/ตอน:** เมื่อตัดเพจย่อย (เช่น `<ชื่อเรื่อง> - <ชื่อเพจ/คนตัด>`) หรือตอนย่อย (`ep<N>`) ให้ตรวจสอบใน Work Bin ก่อน หากว่าง ให้ใช้ `pr_move_item` ดึง 1 ตอนจากคลังกลาง `<ชื่อเรื่อง>/รอ` มาใส่ Work Bin
   - **Strict Isolation:** ล้าง `HIGHLIGHTS_` เก่าเฉพาะใต้ Work Bin ของตัวเองเท่านั้น ห้ามแตะต้องหรือลบ `HIGHLIGHTS_` ของเพจหลักหรือคลังกลางเด็ดขาด และหากในคลังกลางหมด ให้หยุดรายงานทันที ห้ามเดาหรือสลับไปดึง Bin อื่น!
12. **Standard Stock Dashboard Table Protocol (มาตรฐานตารางสรุปผลสต็อก — ห้ามใช้ Bullet List ย่อหน้าซ้อนกัน):**
   - เมื่อผู้ใช้สั่งเช็คสต็อกหรือตรวจความพร้อมตัดต่อ **ห้ามรายงานเป็น Bulleted List หรือข้อความย่อหน้าซ้อนกันเด็ดขาด**
   - **ต้องแสดงผลเป็นตาราง Markdown Table สรุปแบบ Dashboard เสมอ** แบ่งคอลัมน์มาตรฐาน:
     `| ลำดับ | เรื่อง | สต็อกบน Disk | ตอนที่เหลือบน Disk | สถานะใน Premiere Pro | Action ที่ต้องทำ |`
   - **จัดเรียงตามความเร่งด่วน:** เรียงจากเรื่องที่สต็อกเหลือน้อยสุด/หมดขึ้นก่อน (🔴 สต็อกวิกฤต 0–2 คลิป ➔ 🟡 สต็อกปานกลาง ➔ 🟢 มีฟุตเทจดิบพร้อมตัดทันที ➔ ⚪ สต็อกปลอดภัย)
   - **สรุป Action สั้นๆ ใต้ตาราง 2 บรรทัด:** แยกชัดเจนว่าเรื่องไหนมีฟุตเทจพร้อมตัดได้ทันที และเรื่องไหนต้องโหลดฟุตเทจใหม่เข้ามาเติม
   - **Clean Thai Output 100%:** ห้ามมีข้อความคิดในใจหรือประโยคภาษาอังกฤษหลุดปนออกมาเด็ดขาด

---

## 🗂️ 2. สารบัญเครื่องมือ AutoLab MCP ทั้ง 38 คำสั่ง (Complete 38-Tool Quick Map · 41 with aliases)

> 📖 ดูตารางพารามิเตอร์ทุกฟิลด์และตัวอย่าง JSON ครบทั้ง 38 คำสั่งได้ที่: [`references/02-autolab-30-tools-reference.md`](references/02-autolab-30-tools-reference.md)

| หมวดหมู่ (Category) | ชื่อเครื่องมือ (Exact Tool Names) | หน้าที่หลัก (Primary Responsibility) |
| :--- | :--- | :--- |
| **A. System & Templates (6)** | `autolab_get_status`<br>`autolab_navigate`<br>`autolab_list_templates`<br>`autolab_sync_company_pack`<br>`autolab_manage_profiles`<br>`autolab_manage_transforms` | เช็คสถานะพาเนล, สลับหน้าจอ (`home`/`auto_frame`/`auto_highlights`), ดูรายชื่อกรอบ `.mogrt` & ป้ายโปรโมททั้งหมดในเครื่อง, ซิงค์ Company Pack จาก Cloud, และจัดการ Master Profile / Transform Preset |
| **B. Auto Highlights (6)** | `autolab_ah_queue_add`<br>`autolab_ah_queue_manage`<br>`autolab_ah_configure`<br>`autolab_ah_run`<br>`autolab_ah_status`<br>`autolab_ah_cancel` | ดึงไฟล์หนังจาก Bin เข้าคิวไฮไลท์, ตั้งค่าโหมด `gemini_audio`, `100 Shots`, `60-90s`, ตั้งค่า `Speed Assist` (`preset: "movie"` หรือ `"show"`), และสั่งสแกนตัดสร้าง Sub-Sequences อัตโนมัติ |
| **C. Auto Frame Queue (4)** | `autolab_af_queue_add`<br>`autolab_af_queue_inspect`<br>`autolab_af_set_bin_template`<br>`autolab_af_queue_manage` | ดึงคลิป/Sequence จาก Bin เข้าคิวแยกกลุ่มตาม Bin (บล็อก Sub-bin `ไฟล์ต้นฉบับ` อัตโนมัติ), ตรวจสอบคิวและความยาวชื่อไทย (> 17 ตัวอักษร), ผูก Master Profile / กรอบ `.mogrt` (`frame`) และป้ายโปรโมท (`promo`) |
| **D. Live Frame Tuner `🎯 จัดกรอบ` (4)** | `autolab_af_tuner_start`<br>`autolab_af_tuner_auto_fit`<br>`autolab_af_tuner_adjust`<br>`autolab_af_tuner_apply` | สร้างซีเควนซ์ `_AutoLab_Preview_` ใน Premiere Pro, วัดขอบดำด้วย FFmpeg `cropdetect`, ปรับจูน `scale`/`posX`/`posY`, ส่งออกภาพ `.png` ให้ AI Vision ตรวจดู และบันทึกค่าเข้า Bin |
| **E. AI Naming & Refiner `✂️ ย่อชื่อ` (4)** | `autolab_af_configure_naming`<br>`autolab_af_run_autoname`<br>`autolab_af_run_name_refiner`<br>`autolab_af_set_clip_title` | ตั้งโหมด `variety`, กด `✨ AI Auto-Name` ถอดเสียง+คิดชื่อคลิปไวรัล (รองรับ `autoRefine: true`), กด `💬 Name Refiner` ➔ `✂️ ย่อชื่อที่ยาว` (> 17 ตัวอักษร) ➔ `✅ Apply All`, และแก้ไขข้อความพาดหัว 1-2 บรรทัด / ใส่ชื่อหนังบรรทัด 2 + ปรับขนาดฟอนต์บรรทัด 2 ยก Bin (`binKey`, `line2`, `fontSizeL2`) |
| **F. Topbar, Fast Pipeline & `START` (5)** | `autolab_af_configure_topbar`<br>`autolab_af_pipeline`<br>`autolab_af_start_queue`<br>`autolab_af_batch_status`<br>`autolab_af_cancel_queue` | ตั้งค่าความละเอียด `1080x1920`, เวลาป้ายโปรโมทมาตรฐาน (`promoStart: 5`, `promoInterval: 0`), คำสั่งรวบยอดความเร็วสูง `autolab_af_pipeline` (ครบจบใน 1 คำสั่ง), และกดปุ่ม `START` สร้างซีเควนซ์ |
| **G. Production Helpers, Bin Management & Escape Hatches (9 + 3 aliases)** | `autolab_pr_inspect`<br>`autolab_pr_prepare_ep`<br>`autolab_pr_create_bin`<br>`autolab_pr_delete_bin`<br>`autolab_pr_move_item`<br>`autolab_pr_bin_tree`<br>`autolab_pr_export_ame`<br>`autolab_call_js`<br>`autolab_call_jsx`<br>*(Aliases: `autolab_pr_bin_move`, `autolab_pr_bin_clean`, `autolab_pr_find_bin`)* | ส่องดูโครงสร้าง Bin & ดึงชื่อไฟล์ใน `รอ` พร้อมตรวจจับเลขตอนอัตโนมัติ (`pr_inspect`), ส่องผัง Bin & คลิปแบบ Bounded ไม่ล้น Context (`pr_bin_tree`), สร้าง Bin Recursive `mkdir -p` (`pr_create_bin`), ย้ายคลิป/Sequence พร้อมสร้าง Bin ปลายทางอัตโนมัติ (`pr_move_item`), ลบ Bin / กวาดรูด Sequence ไฮไลท์ทิ้งยกชุดด้วย Batch Sweep <150ms (`pr_delete_bin`), เตรียมโฟลเดอร์ Disk + สร้าง Bin `epX` + ย้ายฟุตเทจ (`pr_prepare_ep`), ส่งออกทุก Sequence เข้าคิว Adobe Media Encoder (`pr_export_ame`), และรัน JS / ExtendScript โดยตรง |

---

## 🔄 3. ลำดับขั้นตอนมาตรฐานครบวงจร (End-to-End Autonomous SOP)

### Step 1: สำรวจโปรเจกต์ & เช็คสต็อก 1 คำสั่งจบ (`autolab_pr_inspect`) และเตรียมโฟลเดอร์/Bin (`autolab_pr_prepare_ep`)
1. **เช็คสต็อกบน Disk และสำรวจ Bin ใน Premiere Pro ในคำสั่งเดียว (`autolab_pr_inspect` — One-Call Stock Check `< 0.1s`):**
   ```json
   // Tool: autolab_pr_inspect
   {
     "diskRoot": "<พาธโฟลเดอร์บน Disk>",
     "categoryBin": "<ชื่อ Root Bin หมวดงานใน Premiere Pro>",
     "excludeDirs": "<โฟลเดอร์ที่ต้องการข้าม เช่น ลงแล้ว,จบแล้ว>",
     "lowStockThreshold": 25,
     "scanPremiere": true
   }
   ```
   *(💡 **v1.8.3 One-Call Smart Auto-Scoping:** เมื่อส่ง `diskRoot` ควบคู่ `categoryBin` + `lowStockThreshold: 25` + `scanPremiere: true` โดยไม่ใส่ `queries` ระบบจะคืน `diskFolders` ครบทุกเรื่องบน Disk พร้อมยอดซับโฟลเดอร์ (`[epX:count]` / `[คิว:X,คอม:Y]`) และคัดกรองเฉพาะเรื่องที่สต็อกใกล้หมด (`<= 25` คลิป) ไปตรวจสถานะ Premiere Pro ใน `queryAudit` + `readyToCut` อัตโนมัติใน `< 0.1s` ขนาด Output กะทัดรัด ~1.8 KB ไม่ล้นลง `output.txt` แน่นอน 100%! **⛔ ห้ามเรียก `pr_bin_tree` กวาดทั้งหมวดงาน และห้ามรันคำสั่ง Shell นับไฟล์บน Disk ซ้ำซ้อนเด็ดขาด!** หากต้องการส่องไฟล์เจาะจงรายเรื่อง ค่อยใส่ `query: "<ชื่อเรื่อง>"` หรือ `queries: [...]`)*
2. **ห้ามเรียก `autolab_list_templates({})` หรือเปิดอ่านไฟล์ Schema `.json` ตอนสั่งตัดเด็ดขาด:** หากผู้ใช้มีสกิลประจำเครื่อง (หรือระบุชื่อกรอบและป้ายโปรโมทไว้แล้ว) ให้ใช้ชื่อจากตารางสกิลประจำเครื่องส่งเข้า `autolab_af_pipeline` ทันที (เรียก `autolab_list_templates` เฉพาะตอนสร้างสกิลประจำตัวครั้งแรก หรือเมื่อผู้ใช้ถามหารายชื่อเทมเพลตเท่านั้น!)
3. **เตรียมโฟลเดอร์บน Disk คู่กับสร้าง Sub-bin ตอนใหม่ (`ep1`, `ep2`...) และย้ายไฟล์จาก Sub-bin พักไฟล์ในคำสั่งเดียว (รองรับส่ง `items: [...]` หลายเรื่องพร้อมกัน):**
   ```json
   // Tool: autolab_pr_prepare_ep
   {
     "items": [
       {
         "binName": "Series_A",
         "epName": "ep1",
         "createDiskDir": "D:\\OutputClips\\Series_A\\ep1",
         "removeOldHighlights": true
       }
     ]
   }
   ```

### Step 1.5: บริหารจัดการและจัดระเบียบ Bin ใน Premiere Pro (Production Bin Management)

ชุดคำสั่งสำหรับสร้าง, ย้าย, ลบ, และส่องดูผัง Bin & คลิปใน Premiere Pro โดยตรง (ไม่ต้องพึ่ง terminal script และไม่ต้องวนลูป):

#### 1. ส่องดูผัง Bin & คลิปแบบ Bounded (`autolab_pr_bin_tree`):
- **Native MCP:**
  ```json
  // Tool: autolab_pr_bin_tree
  { "binPath": "<หมวดหมู่>/<ชื่อเรื่อง>", "includeClips": true, "maxDepth": 3 }
  ```
- **Universal CLI:**
  ```powershell
  node "C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\AutoLab\mcp\autolab-mcp.js" --call pr_bin_tree --arg binPath="<หมวดหมู่>/<ชื่อเรื่อง>"
  ```

#### 2. สร้าง Bin ใหม่แบบ Recursive `mkdir -p` (`autolab_pr_create_bin`):
- **Native MCP:**
  ```json
  // Tool: autolab_pr_create_bin
  { "binPath": "<หมวดหมู่>/<ชื่อเรื่อง>/ep1" }
  ```
- **Universal CLI:**
  ```powershell
  node "C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\AutoLab\mcp\autolab-mcp.js" --call pr_create_bin --arg binPath="<หมวดหมู่>/<ชื่อเรื่อง>/ep1"
  ```

#### 3. ย้ายคลิป/Sequence พร้อมสร้าง Bin ปลายทางอัตโนมัติ (`autolab_pr_move_item`):
- **Native MCP:**
  ```json
  // Tool: autolab_pr_move_item
  {
    "from": "<ชื่อไฟล์คลิป>.mp4",
    "to": "<หมวดหมู่>/<ชื่อเรื่อง>/ep1",
    "autoCreateTarget": true
  }
  ```
- **Universal CLI:**
  ```powershell
  node "C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\AutoLab\mcp\autolab-mcp.js" --call pr_move_item --arg from="<ชื่อไฟล์คลิป>.mp4" --arg to="<หมวดหมู่>/<ชื่อเรื่อง>/ep1"
  ```

#### 4. ลบ Bin หรือกวาด Sequence ไฮไลท์ทิ้งยกชุดด้วย High-Speed Batch Sweep (`autolab_pr_delete_bin`):
- รูดลงถังขยะใบเดียว ลบเสร็จใน `<150ms` (รองรับ wildcard `pattern: "S*"` และ `cleanSequences: true`):
- **Native MCP:**
  ```json
  // Tool: autolab_pr_delete_bin
  // ท่ากวาด Sequence S* ทั้งหมดใน Bin ทิ้งในคำสั่งเดียว:
  { "binPath": "<หมวดหมู่>/<ชื่อเรื่อง>", "pattern": "S*" }

  // ท่าลบ Bin ทั้งโฟลเดอร์:
  { "binPath": "<หมวดหมู่>/<ชื่อเรื่อง>/HIGHLIGHTS_<ชื่อเรื่อง>", "force": true }
  ```
- **Universal CLI:**
  ```powershell
  node "C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\AutoLab\mcp\autolab-mcp.js" --call pr_delete_bin --arg binPath="<หมวดหมู่>/<ชื่อเรื่อง>" --arg pattern="S*"
  node "C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\AutoLab\mcp\autolab-mcp.js" --call pr_delete_bin --arg binPath="<หมวดหมู่>/<ชื่อเรื่อง>/HIGHLIGHTS_<ชื่อเรื่อง>" --arg force=true
  ```

### Step 2: ตัดไฮไลท์อัตโนมัติ (Auto Highlights) *(ข้ามไป Step 3 ได้หากมีคลิป/Sequence ใน Bin พร้อมแล้ว)*
```json
// 1. ตั้งค่า Auto Highlights ตามประเภทงาน (Tool: autolab_ah_configure)
// งานหนัง/ซีรีส์: { "preset": "movie" } | งานรายการทีวี: { "preset": "show" }
{
  "preset": "movie"
}

// 2. เพิ่มฟุตเทจจาก Bin เข้าคิว (Tool: autolab_ah_queue_add)
{ "binPath": "หมวดหมู่/ชื่อเรื่อง/ep1", "clearFirst": true }

// 3. สั่งรันจนเสร็จ (Tool: autolab_ah_run)
{ "wait": true }
```

### Step 3: โหมดความเร็วสูงสุดคำสั่งเดียว (`autolab_af_pipeline`) vs โหมดจัดกรอบใหม่ (`🎯 จัดกรอบ`)

#### ⚡ กรณีที่ A: เรื่องนั้นมี `Master Profile` (หรือมีพรีเซ็ตที่เซ็ตไว้) — **ส่ง `profileName` คู่กับ `autoFit: true` ใน `autolab_af_pipeline` คำสั่งเดียวจบ!**
- ระบบจะผูกคู่ Frame + Promo จาก Master Profile ที่สร้างไว้ให้ทันที
- และรัน **Auto Scale (`autoFit: true`) เป็นค่ามาตรฐานเริ่มต้นเสมอ** เพื่อวัดช่องใสของกรอบและสแกนขอบดำวิดีโอหน้างานจริง ป้องกันไม่ให้ภาพล้นหรือติดขอบดำ
- *(ข้อยกเว้น: หากต้องการล็อกขนาดตาม Master Profile ตายตัวโดยไม่ให้ระบบคำนวณใหม่ ให้ระบุ `"autoFit": false`)*
```json
// Tool: autolab_af_pipeline
// ดึงเฉพาะ Sequences + ผูกพรีเซ็ต (Frame + Promo) + คำนวณ Auto Scale มิลลิเมตรกันขอบดำ + ตั้ง Topbar (5-0) + รัน AI Auto-Name (Variety) + ย่อชื่อเกิน 17 ตัวอักษร + กด START ในคำสั่งเดียว
{
  "binPath": "หมวดหมู่/ชื่อเรื่อง/ep1/HIGHLIGHTS_ep1",
  "profileName": "ชื่อชุดพรีเซ็ตหลัก",
  "autoFit": true,
  "promoStart": 5,
  "promoInterval": 0,
  "startQueue": true
}
```

#### 🚀 กรณีที่ C: รันหลายเรื่อง/หลาย Bin พร้อมกัน (Multi-Bin Batch Pipeline สำหรับงานระดับสิบถึงร้อย Bin)
คำสั่งเดียวจบสำหรับคิวยักษ์ที่ต้องทำพร้อมกันหลายเรื่อง แต่ละเรื่องมีกรอบและโปรโมต่างกัน:
```json
// Tool: autolab_af_pipeline
{
  "bins": [
    { "binPath": "Movies/Series_A/ep1/HIGHLIGHTS_ep1", "frame": "Frame_02.mogrt", "promo": "Promo_BrandA.mogrt" },
    { "binPath": "Movies/Series_B/ep2/HIGHLIGHTS_ep2", "frame": "Frame_01.mogrt", "promo": "Promo_BrandA.mogrt" }
  ],
  "autoFit": true,
  "startNow": true
}
```
*(ระบบจะดึงทุก Bin เข้าคิว ➔ ผูกกรอบ/โปรโมแยกตาม Bin ➔ สแกนวัดขนาดและขอบดำทุก Bin อัตโนมัติ ➔ รัน AI Auto-Name ตัด S ออก ➔ ย่อชื่อผ่าน Name Refiner ➔ กดปุ่ม START ในคำสั่งเดียวจบ)*

#### 🎯 กรณีที่ B: เรื่องใหม่ที่ยังไม่มีพรีเซ็ตสเกล (ไม่มี `Master Profile`) — **วัดช่องใส `.mogrt` + สแกนขอบดำวิดีโออัตโนมัติระดับพิกเซล (`~0.2–0.4s`)**
- **วิธีที่ 1: รันรวดเดียวใน `autolab_af_pipeline` (ส่งแค่ `frame` กับ `promo` โดยไม่ต้องส่ง `profileName` และไม่ต้องเดา `scale`)**
  ระบบจะแกะช่องใสจริงของ `.mogrt` + สแกนหาขอบดำในวิดีโอ 3 ช่วงเวลา (`120s/360s/720s`) + คำนวณและเซ็ต `scale / posX / posY` ลงคิวให้อัตโนมัติทันที:
  ```json
  // Tool: autolab_af_pipeline
  {
    "binPath": "หมวดหมู่/ชื่อเรื่อง/ep1/HIGHLIGHTS_ep1",
    "frame": "ชื่อกรอบ.mogrt",
    "promo": "ชื่อป้ายโปรโมท.mogrt",
    "autoFit": true,
    "promoStart": 5,
    "promoInterval": 0,
    "startQueue": true
  }
  ```
- **วิธีที่ 2: สั่งวัดขนาดและเช็คขอบดำแยกขั้นตอน (`autolab_af_tuner_auto_fit`)**
  1. ดึงเฉพาะ Sequences เข้า Auto Frame Queue และผูกกรอบ `.mogrt` + ป้ายโปรโมท:
     ```json
     // Tool: autolab_af_queue_add
     { "binPath": "หมวดหมู่/ชื่อเรื่อง/ep1/HIGHLIGHTS_ep1", "onlySequences": true, "clearFirst": true }

     // Tool: autolab_af_set_bin_template
     { "binKey": "*", "frame": "ชื่อกรอบ.mogrt", "promo": "ชื่อป้ายโปรโมท.mogrt" }
     ```
  2. สั่งวัดขนาดช่องใส `.mogrt` คู่กับสแกนขอบดำวิดีโอและเซ็ตค่าลง Bin ทันที (`~0.2–0.4 วินาที` โดยไม่ต้องใส่ตัวเลข Hardcode ใดๆ):
     ```json
     // Tool: autolab_af_tuner_auto_fit
     { "binKey": "*" }
     ```
     *(ระบบจะคืนค่า `mogrtAperture` บอกพิกัดช่องใสของกรอบ, `cropAnalysis` บอก `srcW/srcH`, `cropW/cropH`, `hasBlackBars: true/false`, และ `updatedTransform` บอก `scale, posX, posY` ที่คำนวณและบันทึกเข้า Bin เรียบร้อยแล้ว — หากต้องการเรนเดอร์ภาพ PNG จาก Premiere Pro มาตรวจด้วยตา AI Vision เพิ่มเติม ให้ส่ง `"preview": true`)*
  3. ตั้งค่า Topbar (`5 - 0`), รัน `✨ AI Auto-Name` พ่วง `💬 Name Refiner` (`autoRefine: true`), และกดปุ่ม `START`:
   ```json
   // 1. ตั้งค่า Topbar (Tool: autolab_af_configure_topbar)
   {
     "resMode": "custom",
     "width": 1080,
     "height": 1920,
     "promoStart": 5,
     "promoInterval": 0,
     "injectHeadline": true,
     "autoCutState": 0
   }

   // 2. ตั้งชื่อ AI + ย่อชื่อเกิน 17 ตัวอักษรอัตโนมัติ (Tool: autolab_af_run_autoname)
   { "mode": "variety", "autoApply": true, "autoRefine": true }

   // 3. กดปุ่ม START รันคิวจนเสร็จ (Tool: autolab_af_start_queue)
   { "wait": true, "autoDismissModal": true }
   ```

### Step 4: ส่งออกทุก Sequence เข้าคิว Adobe Media Encoder (`autolab_pr_export_ame`)
```json
// Tool: autolab_pr_export_ame
{
  "highlightsBinPath": "หมวดหมู่/ชื่อเรื่อง/ep1/HIGHLIGHTS_ep1",
  "outputDir": "D:\\OutputClips\\ชื่อเรื่อง\\ep1"
}
```
*(💡 **v1.8.3 Zero-Delay Auto-Render:** คำสั่ง `pr_export_ame` ตั้งค่า `startQueue: true` เป็นดีฟอลต์ จะส่งทุก Sequence เข้าคิว AME พร้อมสั่งให้ Media Encoder เริ่มเรนเดอร์ทันทีใน `0ms` ผ่าน `app.encoder.startBatch()` โดยไม่ต้องคลิกปุ่ม Start Queue เอง หรือรอตัวนับถอยหลัง Idle Countdown 2 นาที)*

---

## 🧭 4. คู่มือให้ AI พาผู้ใช้สร้าง "สกิลเวิร์กโฟลว์ประจำตัว" & วางระบบคอมใช้ร่วมกันหลายคน / หลายโปรโม (Interactive Personal & Shared-PC Workflow Skill Builder)

**ผู้ใช้ทั่วไปและพนักงานตัดต่อไม่ใช่โปรแกรมเมอร์ (User is NOT a Dev) — ห้ามให้ผู้ใช้คิดระบบหรือเขียนไฟล์สกิลเองเด็ดขาด!**
เมื่อผู้ใช้แต่ละคน (หรือพนักงานหลายคนที่แชร์คอมเครื่องเดียวกัน / ตัดลงหลายเพจ / มีหลายป้ายโปรโมท) สั่งว่า *"ช่วยสร้างสกิลประจำตัว"*, *"ตั้งค่าเวิร์กโฟลว์ของฉัน"*, หรือเมื่อ AI ตรวจพบว่ายังไม่มีสกิลประจำเครื่อง:

1. **ให้ AI เปิดอ่านคู่มือ [`references/06-personal-workflow-skill-builder-guide.md`](references/06-personal-workflow-skill-builder-guide.md) ทันที**
2. **AI สำรวจและจัดกลุ่มไฟล์ในเครื่องให้ผู้ใช้ดูก่อนถาม (Phase 1 Auto-Discovery & Smart Clustering):**
   - เรียก `autolab_list_templates` และ `autolab_get_status`
   - หากตรวจพบป้ายโปรโมทหลายตัว (เช่น แยกตามหมวดหมู่เนื้อหา หรือมีรหัสต่อท้ายคนตัด/เพจ เช่น `_Team1`, `_Team2`, `_A`, `_B`), **AI ต้องจัดกลุ่มขึ้นมาแสดงให้ผู้ใช้เห็นทันที**
3. **AI เสนอระบบแยกโปรโม/แยกคนตัดสำเร็จรูปให้ผู้ใช้แค่เลือกตอบง่ายๆ (Phase 2 Guided Multi-User & Multi-Promo Architecture):**
   - แนะนำวิธีแยกด้วย **คำต่อท้ายชื่อโฟลเดอร์/Bin (Folder Suffix Tag)** เช่น โฟลเดอร์ปกติ = คนที่ 1 (เช่น `_Team1`), โฟลเดอร์ที่มีคำต่อท้ายระบุคนที่ 2 = คนที่ 2 (เช่น `_Team2`)
   - แนะนำระบบ **Central Raw Pool ➔ Work Bin Routing:** พักฟุตดิบรวมไว้ที่ `<ชื่อเรื่อง>/รอ` แล้วให้ AI ดึงทีละ 1 ตอนไปใส่ Work Bin แยกของแต่ละเพจ/คนตัด (`<ชื่อเรื่อง> - <รหัสเพจ>`) และลบ `HIGHLIGHTS_` เฉพาะใน Work Bin ตัวเอง
   - แนะนำวิธีแยกตาม **หมวดหมู่โฟลเดอร์หลัก** เช่น หมวดหนัง/ซีรีส์ = ใช้โปรโมหมวดหนัง + เปิด Speed Assist หนัง + วัดกรอบอัตโนมัติ (`af_tuner_auto_fit`), หมวดรายการทีวี = ใช้โปรโมหมวดรายการ + ปิด Speed Assist
4. **AI สร้างไฟล์สกิลประจำเครื่องพร้อมตารางจับคู่ 2 มิติ (2D Routing Matrix) แยกต่างหาก (Phase 3–4 Generate Separate Skill):**
   - สร้างไฟล์ `.agents/skills/<my-workflow>/SKILL.md` ให้ผู้ใช้โดยอัตโนมัติ (ห้ามเขียนข้อมูลส่วนตัวของผู้ใช้ทับลงในสกิลกลาง `autolab-premiere` เด็ดขาด เพื่อความปลอดภัยและเพื่อให้ดึงอัปเดตสกิลกลางได้ตลอดเวลา)

---

## 📚 5. คู่มืออ้างอิงเชิงลึกแยกตามโมดูล (Modular Reference Guides)

เมื่อต้องการดูรายละเอียดพารามิเตอร์ของเครื่องมือเฉพาะส่วน ให้เปิดอ่านไฟล์ในโฟลเดอร์ `references/` ตามรายการนี้:

1. **[`references/01-connection-and-bridge.md`](references/01-connection-and-bridge.md)** — สถาปัตยกรรม Dual Bridge (`http://127.0.0.1:17890` & `%TEMP%\premiere-mcp-bridge`), การรันผ่าน CLI โดยตรง (`--status`, `--list-tools`, `--call`), และตารางแก้ปัญหา
2. **[`references/02-autolab-30-tools-reference.md`](references/02-autolab-30-tools-reference.md)** — **คู่มืออ้างอิงครบทั้ง 38 Tools (41 รวม Aliases) ของ `autolab` MCP** (รวม `autolab_af_pipeline`, `autolab_pr_prepare_ep`, `autolab_pr_export_ame`, และ 7 Native Bin Tools) พร้อมตารางพารามิเตอร์ทุกฟิลด์และตัวอย่าง JSON
3. **[`references/03-auto-frame-and-vision-sop.md`](references/03-auto-frame-and-vision-sop.md)** — คู่มือปฏิบัติการเชิงลึกของ Auto Frame Queue, การจัดกรอบด้วย AI Vision (`🎯 จัดกรอบ`), และการตั้ง/ย่อชื่อคลิปไวรัล
4. **[`references/04-auto-highlights-and-jumpcut-sop.md`](references/04-auto-highlights-and-jumpcut-sop.md)** — คู่มือปฏิบัติการเชิงลึกของ Auto Highlights และ Auto Jump Cut
5. **[`references/05-premiere-pro-432-tools-catalog.md`](references/05-premiere-pro-432-tools-catalog.md)** — **สารบัญและแคตตาล็อกครบทั้ง 434 Tools ของ `premiere-pro` MCP (`v1.24.1`)** แยกตาม 8 หมวดหมู่พร้อมพารามิเตอร์ทุกตัว
6. **[`references/06-personal-workflow-skill-builder-guide.md`](references/06-personal-workflow-skill-builder-guide.md)** — **คู่มือจับมือทำสำหรับให้ AI สัมภาษณ์ผู้ใช้ สำรวจพรีเซ็ตในเครื่อง และสร้างสกิลเวิร์กโฟลว์ประจำตัว (`SKILL.md`) ให้อัตโนมัติ**

