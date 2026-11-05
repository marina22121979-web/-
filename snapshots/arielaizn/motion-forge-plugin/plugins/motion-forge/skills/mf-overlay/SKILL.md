---
name: mf-overlay
description: אנימציה מעל תמונה או וידאו אמיתיים - דודלים, חצים, מסגרות, הדגשות, מדבקות, טקסט מונפש, כוכבים וניצוצות מעל צילום; רינדור שקוף (ProRes 4444) וקומפוזיט עם ffmpeg כולל הנמכת הפסקול מתחת לדיבור. הפעל כשמבקשים "לצייר על הסרטון", "דודלים על התמונה", "אנימציה מעל וידאו", "אוברליי", "חצים והדגשות על סרטון", "draw on my video", "doodle over photo", "animated overlay", "annotate footage". חלק מ-Motion Forge; קרא קודם את motion-forge.
---

# mf-overlay · קוד מעל המציאות

## שני מסלולים
**תמונה:** התמונה נכנסת לסרט כ-data URL, והסרט מצייר מעליה.
```bash
python3 - <<'EOF'
import base64, sys
from PIL import Image; import io
im = Image.open('photo.jpg'); im.thumbnail((1920, 1920))
b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=90)
open('films/photo-data.js', 'w').write("const PHOTO_SRC = 'data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode() + "';")
EOF
```
בסרט: `<script src="photo-data.js"></script>`, וב-`setup()` טוענים `new Image()` מ-`PHOTO_SRC` ומחכים ל-`decode()`.
תמונה מ-`file://` רגיל "מלכלכת" את הקנבס, ואז הרינדור נכשל ב-`toDataURL`. לכן data URL.

**וידאו:** הסרט מרונדר עם רקע שקוף ומולבש על הקליפ ב-ffmpeg.
1. בסרט: `bg: null`, ואותו `size` ו-`fps` כמו הקליפ (או 1080x1920 ב-30fps וחיתוך הקליפ).
2. `node render.mjs films/overlay.html --alpha` → `out/overlay.mov` (ProRes 4444 עם אלפא) + `out/overlay.wav`.
3. קומפוזיט, כשהפסקול של הסרט יורד מתחת לדיבור של הקליפ (sidechain):
```bash
ffmpeg -i clip.mp4 -i out/overlay.mov -i out/overlay.wav -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[bg];\
[bg][1:v]overlay=0:0:format=auto[v];\
[0:a]asplit=2[sp][key];[2:a]volume=0.8[fx];[fx][key]sidechaincompress=threshold=0.04:ratio=5:attack=8:release=250[fxd];\
[sp][fxd]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93[a]" \
-map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart final.mp4
```
אם לקליפ אין אודיו: `-map 2:a` במקום השרשרת.

## לסנכרן לתוכן הקליפ
אין מעקב אוטומטי. חלץ פריימים (`ffmpeg -ss T -i clip.mp4 -frames:v 1 f.png`) בזמנים שבהם צריך הדגשה, פתח אותם, קבע קואורדינטות
ידנית לכל נקודת מפתח, וכתוב אותן כ-`kf`. לאובייקט שזז: 3 עד 6 מפתחות לשנייה ו-`E.linear` ביניהם.

## השפה של אוברליי טוב
- קו כתב יד: `P.catmull` על נקודות עם `wiggle` קבוע, `P.trim` שנכתב ב-0.3 עד 0.5 שניות, עובי 6 עד 10px, צבע אחד בולט.
- חץ שמצביע, עיגול סביב מילה, קו תחתון, כוכבים ונצנוצים (`P.star` + `A.sparkle`), מדבקת טקסט עם צל קשיח.
- פחות זה יותר: דודל אחד לכל רעיון, ונעלם לפני הבא.
- פנים של אנשים נשארות גלויות תמיד.

## סאונד
`A.pop` להופעת דודל, `A.slide` לחץ, `A.sparkle` לנצנוצים. בלי גרוב אם יש דיבור בקליפ, או גרוב שקט (`ambient`) שה-sidechain מנמיך.
