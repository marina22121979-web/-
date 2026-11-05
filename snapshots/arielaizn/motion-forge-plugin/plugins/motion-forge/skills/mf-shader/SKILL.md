---
name: mf-shader
description: עולמות שיידר ב-WebGL - synthwave עם גריד ושמש, כרום נוזלי, אורורה, פלזמה, metaballs, מנהרת כוכבים, שדות רעש, raymarching, רקעים גנרטיביים חיים, ומעליהם טקסט וגרפיקה בקנבס. הפעל כשמבקשים "שיידר", "רקע גנרטיבי", "synthwave", "רטרו אייטיז", "כרום נוזלי", "אורורה", "רקע מופשט חי", "shader", "WebGL", "liquid chrome", "abstract background", "visualizer". חלק מ-Motion Forge; קרא קודם את motion-forge.
---

# mf-shader · פיקסלים שמחושבים

סרט דוגמה: `../motion-forge/studio/gallery/07_synthwave.html`. כלים: `GL.shader`, `GL.frag`, `GL.chunks`, `GL.presets`.

## איך זה עובד
שיידר רץ על כל פיקסל, ומקבל `u_time`, `u_res` וכל יוניפורם שתגדיר. הסרט מצייר אותו לקנבס של WebGL ומעתיק לקנבס הראשי,
ומעליו טקסט וגרפיקה רגילים.

```js
let bg;
film({ /* ... */
  async setup() { bg = GL.presets.synthwave({ sun: '#ff7ad9', grid: '#35f2ff', sky: '#1a0b3d' }); },
  draw(c, t) { bg.render({ u_time: t }); c.drawImage(bg.canvas, 0, 0, W, H); /* טקסט מעל */ },
});
```
שיידר משלך: `GL.shader(GL.frag(body, ['noise', 'fbm', 'palette']))`, כש-`body` מגדיר `vec4 shade(vec2 uv)`
(פתח את `engine/API.md` לחתימה המדויקת).

## כללי ברזל
1. **הזמן בא מבחוץ.** רק `u_time` שהסרט מעביר. אין מצב, אין feedback buffers בלי checkpoints.
2. **ביצועים ב-headless.** ברינדור Chrome רץ לעיתים על SwiftShader (מעבד). פריים 1080p צריך להיות מתחת ל-250ms:
   `GL.shader(src, { scale: .5 })` מרנדר בחצי רזולוציה ומגדיל, עד 64 צעדי raymarch, עד 5 אוקטבות fbm.
3. **טון.** סיים ב-`aces` (tonemap) ו-grain קל, אחרת גרדיאנטים יוצאים עם banding.
4. **טקסט מעל שיידר** צריך ניגוד: פס כהה רך מאחוריו, או glow, או stroke.

## מתכונים
| מראה | מרכיבים |
|---|---|
| Synthwave | שמיים בגרדיאנט, שמש עם פסים, הרים בסילואט (fbm חד-ממדי), גריד פרספקטיבה שזז לכיוון המצלמה, כרום על הטקסט |
| כרום נוזלי | fbm מעוות פעמיים (domain warping) → נורמל מדומה → השתקפות של גרדיאנט סביבה |
| אורורה | וילונות של fbm אנכי, צבעים ירוק-טורקיז-סגול, כוכבים מנצנצים (hash על גריד) |
| Metaballs | שדה סכום של 1/d² מכמה נקודות שזזות, סף רך, צבע לפי עוצמה |
| מנהרה ו-warp | קואורדינטות קוטביות, `1/r` לעומק, פסים שזזים עם הזמן |
| ויזואלייזר | עוצמות מה-score (`tempo().pulse`) מועברות כיוניפורמים, הצורות פועמות על הביט |

## סאונד
Synthwave: `A.groove('synthwave', 0, dur, { bpm: 100, chords: 'Am F C G' })` עם `delay: .25`. מופשט: `ambient` או `trailer`.
