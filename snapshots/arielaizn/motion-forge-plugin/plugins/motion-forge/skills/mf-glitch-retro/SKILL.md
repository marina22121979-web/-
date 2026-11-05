---
name: mf-glitch-retro
description: גליץ', VHS, CRT, דאטהמוש, פיקסל ארט 8-ביט, מסך טרמינל ורטרו-טק בקוד - RGB split, פלחים מוזזים, scanlines, רעש קלטת, tracking, פיקסלים על גריד נמוך, צ'יפטיון. הפעל כשמבקשים "גליץ'", "VHS", "וינטג' וידאו", "רטרו", "פיקסל ארט", "8 ביט", "מסך ישן", "האקר", "glitch", "retro", "CRT", "pixel art", "8-bit", "cyberpunk". חלק מ-Motion Forge; קרא קודם את motion-forge.
---

# mf-glitch-retro · מכונה שמתקלקלת יפה

סרט דוגמה: `../motion-forge/studio/gallery/08_glitch.html`. כלים: `FX.glitch`, `FX.chroma`, `FX.scanlines`, `FX.pixelate`, `FX.grain`, `T.fx.scramble`.

## גליץ' שעובד
- **גליץ' הוא אירוע.** רוב הזמן התמונה נקייה, ופרצי גליץ' של 0.1 עד 0.4 שניות נוחתים על ביטים וחיתוכים.
  גליץ' רציף מעייף אחרי שנייה.
- פרץ = `FX.glitch(c, drawScene, t, { amount, slices: 10-18, rgb: 6-14, fps: 12 })` כש-`amount` עולה ויורד ב-`kf`.
- בין הפרצים נשאר סימן קטן: chroma של 1 עד 2 פיקסלים, grain, scanlines ב-8 אחוז.
- טקסט: `T.fx.scramble` נכנס, ובאמצע ההחזקה עוד פרץ scramble קצר של 3 אותיות.

## VHS ו-CRT
- VHS: רוויה נמוכה, bleed אופקי (טשטוש אופקי קל של הצבע), פס tracking שעולה לאט (`FX.glitch` עם slices רחבים באזור אחד),
  רעש בקצה התחתון, חותמת זמן בפינה (`JetBrains Mono`, "PLAY ▶", "SP 00:00:12").
- CRT: עיוות חבית קל (שיידר, `mf-shader`) או scanlines + vignette חזק + glow על כל דבר בהיר.

## פיקסל ארט
- צייר לקנבס קטן (למשל 270x480 ל-9:16), ואז `c.imageSmoothingEnabled = false; c.drawImage(small, 0, 0, W, H)`.
- פלטה של 8 עד 16 צבעים. מיקומים מיושרים לגריד (`Math.round`). תנועה ב-12fps (`step(t, 12)`), ספרייטים לפי שלב.
- גופן: `Press Start 2P` בגדלים שהם כפולות של 8.

## סאונד
גליץ': `A.glitch(t, dur)` על כל פרץ, `A.tapeStop` לפני חיתוך, `A.groove('hiphop' | 'synthwave')`.
פיקסל: `A.groove('chiptune')`, `A.pulse` לקפיצות ולמטבעות, `A.blip` לתפריטים.

## בטיחות
הבזקים: עד 3 בשנייה, ובלי הבזק אדום-לבן מלא. דוח ה-QA מסמן "FLASH RISK" מעל הסף.
