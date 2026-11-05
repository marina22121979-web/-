---
name: mf-3d
description: תלת-ממד בקוד בלי ספריות - סצנות low-poly עם הצללה שטוחה או toon, מצלמה שמסתובבת ועושה dolly, עולמות איזומטריים, טקסט ולוגו מוחצנים, כרטיסים בחלל 2.5D עם עומק שדה, ו-raymarching דרך שיידרים. הפעל כשמבקשים "תלת ממד", "3D", "low poly", "איזומטרי", "טקסט תלת ממדי", "לוגו תלת ממדי", "מצלמה שמסתובבת", "isometric", "3D text", "orbit camera". חלק מ-Motion Forge; קרא קודם את motion-forge.
---

# mf-3d · עומק בלי מנוע

סרט דוגמה: `../motion-forge/studio/gallery/12_lowpoly.html`. כלים: `CAM.create`, `CAM.mesh.*`, `CAM.render`, `CAM.parallax`, `CAM.iso*`, `CAM.extrude`, `GL`.

## ארבע רמות, בחר את הזולה שעובדת
| רמה | מתי | כלי |
|---|---|---|
| **2.5D כרטיסים** | רוב המקרים: שכבות שטוחות בעומק שונה, מצלמה שזזה, DOF | `CAM.parallax` |
| **איזומטרי** | אקספליינרים, עולמות קטנים, בנייה | `CAM.iso`, `CAM.isoBox` |
| **Mesh מלוטש** | חפצים שמסתובבים: קופסה, כדור, טורוס, לוגו מוחצן | `CAM.mesh.*` + `CAM.render` |
| **Raymarching** | צורות רכות, מתכת, מיזוג צורות, תאורה אמיתית | שיידר (`mf-shader`) |

## Mesh
- `CAM.render(c, meshes, cam, { style: 'toon', light, ambient: .35, stroke: '#111', strokeWidth: 3 })`.
- סגנונות: `flat` (צבע לכל פאה לפי זווית לאור), `lowpoly` (flat + ריצוד צבע קטן לכל פאה), `toon` (2 עד 3 רמות תאורה + קו מתאר), `wire`.
- מצלמה: `CAM.orbit(t, { radius, speed, height })` לסיבוב סביב מרכז, או `kf` על `x, y, z, rx, ry` לתנועות מתוכננות.
  Dolly-in איטי (5 עד 10 אחוז לאורך שוט) נותן חיים.
- ספירת פאות: עד כמה אלפים ב-2D. icosphere עם `sub: 2` מספיק לכדור.

## טקסט ולוגו מוחצנים
`CAM.extrude(c, drawFn, { depth: 30, angle: .8, dark: '#3a1d6e' })` מערם עותקים כהים מתחת לשכבה העליונה, והעליונה מקבלת
גרדיאנט ו-`FX.lightSweep`. לסיבוב מדומה: scaleX = cos(זווית) יחד עם שינוי כיוון ההחצנה.

## תאורה וצבע
אור אחד מלמעלה-שמאל, ambient בין 0.3 ל-0.4, צבע רקע שמשלים את צבע החפץ. צל מגע: אליפסה כהה רכה על הרצפה שמתכווצת כשהחפץ עולה.

## סאונד
`A.groove('minimal' | 'synthwave' | 'cinematic')`, `A.whoosh` לתנועות מצלמה מהירות, `A.thud` לנחיתות, `A.shimmer` על highlights.
