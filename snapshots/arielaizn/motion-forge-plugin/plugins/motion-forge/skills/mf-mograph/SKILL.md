---
name: mf-mograph
description: מושן גרפיקס ברמת After Effects בקוד - shape layers, Trim Paths, repeaters, בלוקי צבע, overshoot, precomps, track mattes, bursts, צורות שמתחלפות על הביט. הפעל כשמבקשים "מושן גרפיקס", "סטייל אפטר", "motion graphics", "shape animation", "אנימציית צורות", "אינטרו גרפי", "באמפר", "רקע מושן לפרזנטציה", "סרטון גרפי לריל", או כשסרט מושן יצא שטוח ו"מצגתי". חלק מחבילת Motion Forge; קרא קודם את motion-forge.
---

# mf-mograph · מושן גרפיקס ברמת After Effects

סרט דוגמה: `../motion-forge/studio/gallery/01_mograph-shapes.html`. כלים: `P` (shapes.js), `FX`, `E`, `kf`, `spring`, `stagger`.

## מה עושה את זה "אפטר"
1. **Trim Paths בכל מקום.** קווים נכתבים (`P.trim(path, 0, p)`), טבעות נסגרות, קו מוביל את העין לנקודה הבאה.
   קו שנכתב ב-0.5 עד 0.8 שניות עם `E.inOutCubic`, והזנב שלו נמחק באיחור של 0.15 (`P.trim(path, p2, p1)`).
2. **צורות עם משקל.** כל צורה שנכנסת עוברת scale מ-0 עם overshoot (`E.overshoot` או `springAt(t, t0, 0, 1, 'pop')`),
   ובאותו זמן מסתובבת 15 עד 40 מעלות ומתיישבת.
3. **Repeaters ו-offsets.** עותקים עם הזזת זמן ביניהם (`stagger(i, n, .04, 'center')`) יוצרים גלים. 3 עד 12 עותקים, לא 50.
4. **בלוקי צבע כמעברים.** מלבן בצבע המותג מכסה את המסך ב-0.35 שניות (`E.whip`), והסצנה הבאה נחשפת מאחוריו.
   בשכבות: 2 או 3 בלוקים בצבעים שונים, 60ms ביניהם.
5. **Bursts ונקודות אימפקט.** כל נחיתה חשובה מקבלת `P.burst` (קווים רדיאליים) ו-`A.pop` או `A.hit`.
6. **Parenting.** קבוצה זזה יחד: `c.save(); c.translate(...); c.rotate(...);` ובתוכה כל ילד עם התזמון שלו.
7. **Track mattes.** טקסט או צורה נחשפים דרך צורה אחרת: `FX.matte(c, drawContent, drawMask)`.

## גרפי מהירות (העתק מהם)
| פעולה | easing | משך |
|---|---|---|
| כניסת צורה | `E.overshoot` או spring `pop` | 0.35 עד 0.5s |
| יציאה | `E.inCubic` / `E.inBack` | 0.2 עד 0.3s |
| תנועה בין מקומות | `E.snappy` (מהיר, התיישבות ארוכה) | 0.5 עד 0.8s |
| מעבר מסך מלא | `E.whip` | 0.3 עד 0.45s |
| Trim path | `E.inOutCubic` | 0.5 עד 0.9s |
| סיבוב קבוע ברקע | `E.linear` | כל הסרט |

## מבנה סצנה (precomp)
כל סצנה היא פונקציה `sceneX(c, lt, p)` שמקבלת זמן מקומי. `scenes()` מחליט מי פעילה. מעבר = שתי סצנות פעילות
יחד ב-0.3 השניות של החפיפה, עם בלוק צבע או מסכה ביניהן.

```js
const SC = scenes([['logoBuild', 0, 2.4], ['stats', 2.4, 5.6], ['outro', 5.6, 8]]);
function draw(c, t) {
  const s = SC.at(t);
  ({ logoBuild, stats, outro })[s.name](c, s.t, s.p);
  colorWipe(c, t, 2.25); colorWipe(c, t, 5.45);   // בלוקים מעל החיתוכים
}
```

## פלטות שעובדות
- כהה ניאון: `#0d0d14` רקע · `#ff3d6e` · `#ffd23f` · `#3ddcff` · לבן לטקסט.
- פלאט חם: `#fff4e6` · `#ff6b35` · `#004e89` · `#1a1a2e`.
- מותג אחד: גוון המותג + שני גוונים שלו (בהיר/כהה) + ניטרלי אחד. אל תוסיף צבע חמישי.

## סאונד
`A.groove('house' | 'uplift' | 'minimal', ...)`. כל כניסת צורה: `A.pop` או `A.blip` בגובה שעולה עם ה-stagger
(`A.blip(t, 72 + i*2)`); כל בלוק צבע: `A.whoosh(t - .2, .35)`; נחיתת לוגו: `A.impact` + `A.sparkle`.

## מה הורס את זה
- הכל נכנס יחד. תן לכל קבוצה 80 עד 150ms משלה.
- צורות סטטיות אחרי הכניסה. הוסף `wiggle` עדין (2 עד 6px) או סיבוב איטי.
- יותר מ-3 גופנים. בחר אחד לכותרות (Anton, Bebas Neue, Space Grotesk) ואחד לגוף (Inter, Heebo).
- מעבר לכל שנייה. מעבר-גיבור אחד ועוד חיתוכים פשוטים על הביט.
