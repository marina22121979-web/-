---
name: mf-sound
description: פסקול מסונתז בקוד לסרטי Motion Forge - 11 גרוביי ז'אנר (uplift, lofi, synthwave, trailer, chiptune, minimal, house, playful, ambient, cinematic, hiphop), אקורדים וסולמות, 32 אפקטים (whoosh, riser, impact, braam, glitch, UI, מכונת כתיבה), סנכרון התמונה לביט, sidechain, מיקס ו-LUFS. הפעל כשצריך לכתוב או לתקן score(A), "תוסיף מוזיקה", "סאונד דיזיין", "אפקטים קוליים", "שהאנימציה תהיה על הביט", "הסאונד חלש/חזק", "sound design", "sync to beat". חלק מ-Motion Forge; קרא קודם את motion-forge.
---

# mf-sound · לשמוע את מה שרואים

המנוע: `../motion-forge/studio/engine/audio.js`. אין סמפלים. כל צליל נבנה מאוסצילטורים, רעש ופילטרים, ואותו קוד רץ
בנגן החי וברינדור. הרינדור מנרמל ל-‎-14 LUFS ו-‎-1 dBTP, אז המטרה היא איזון בין החלקים ולא עוצמה.

## גריד אחד לתמונה ולסאונד
```js
const B = tempo(112);                       // מ-motion.js
// בתמונה: const pop = springAt(t, B.beat(8), 0, 1, 'pop');  B.pulse(t) לפעימות
score(A) {
  A.groove('uplift', 0, B.bar(4), { bpm: 112, chords: 'C G Am F' });
  A.whoosh(B.beat(8) - .25, .35);  A.impact(B.beat(8));
}
```
כל חשיפה חשובה נוחתת על `B.beat(n)`. whoosh מתחיל 0.15 עד 0.3 שניות לפני. riser באורך 1 עד 2 ביטים לפני drop.

## גרוביים
| סגנון | BPM | מתאים ל |
|---|---|---|
| `uplift` | 110-124 | מוצר, הסבר, תאגידי חיובי |
| `minimal` | 90-110 | Apple-style, טכנולוגיה נקייה |
| `house` | 120-126 | אנרגיה, אופנה, ריל מהיר |
| `synthwave` | 90-110 | רטרו, ניאון, שיידרים |
| `lofi` / `hiphop` | 75-95 | שיחה, ציטוט, סטודנטים, יומיומי |
| `trailer` | 90-120 | דרמה, השקה גדולה (עם `energy` עולה) |
| `cinematic` | 70-90 | רגש, סיפור |
| `playful` | 100-120 | דמויות, ילדים, פאן |
| `chiptune` | 120-150 | פיקסל, גיימינג |
| `ambient` | 60-80 | שקט, יוקרה, גנרטיבי |

אפשרויות: `{ bpm, chords: 'Am F C G', barsPerChord: 1, energy: 0..1 }`. אפשר כמה קטעי groove ברצף (בנייה: `energy` .4 ואז 1),
ושקט דרמטי עם `A.silence(ta, tb)` לפני פאנץ'. `A.pump(.45)` לפני הגרוב נותן EDM pumping.

## אקורדים ומנגינה
`chord('Am7', 4)` → תווים. `scale('A', 'minor', 4)`. מוטיב של 3 עד 5 תווים ב-`A.bell` / `A.pluck` / `A.lead` שחוזר בפתיחה ובסיום
נותן לסרט זהות. `A.arp(ta, tb, chord('Am', 4), B.spb / 2)`.

## אפקטים לפי אירוע
| אירוע | צליל |
|---|---|
| כניסת צורה או אייקון | `A.pop`, `A.blip(t, note)` בגובה שעולה עם ה-stagger |
| מעבר | `A.whoosh` / `A.swish`, בלוק צבע: `A.whoosh(dir: 'down')` |
| חשיפה גדולה | `A.riser` לפני + `A.impact` או `A.braam` + `A.duck` |
| טקסט | `A.tick` למילה, `A.typewriter`, `A.glitch` לסקרמבל |
| מונה | `A.count(t0, t1)` + `A.chime` בסוף |
| UI | `A.click`, `A.ui('confirm' | 'notify' | 'like' | 'send' | 'error')`, `A.keyboard` |
| דמות | `A.boing`, `A.splat`, `A.thud`, `A.slide`, `A.heartbeat` |
| קסם, הצלחה | `A.sparkle`, `A.shimmer`, `A.chime` |
| רקע | `A.vinyl`, `A.room`, `A.wind`, `A.drone` |

## מיקס
- `audio: { music: .6, sfx: .85, reverb: .22, delay: 0 }` בקונפיג הסרט. אפקט שנבלע: הגדל את ה-`v` שלו, או `A.duck` על המוזיקה.
- אי אפשר לשמוע את התוצאה. `--qa` מדווח LUFS גולמי, שיא ושקטים ארוכים; שקט של יותר משנייה וחצי באמצע הוא כמעט תמיד באג.
- קריינות: אין TTS מובנה. אם יש קובץ קול, רנדר את הסרט ומזג עם ffmpeg (שרשרת sidechain ב-`mf-overlay`).
