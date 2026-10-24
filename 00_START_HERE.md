# 00_START_HERE — Aria Graveyard Pack (v2_1) · وضعیت: پارت ۱، ۲ و ۳ تمام

این زیپ **تنها منبع حقیقت** است و هیچ چیزی از سرور لازم ندارد. اگر سرور مشترک (claudeWeb) هم بالا بود، فقط برای checkpoint متنی استفاده شود؛ فایل‌ها از ابزار اجرای کد به سرور نمی‌رسند مگر دامنه‌ی `sharedmemory.serveousercontent.com` در تنظیمات شبکه‌ی ابزار allowlist شود.

## ترتیب خواندن
1. این فایل → `STATE.md` (جای checkpoint) → `HANDOFF.md` (جدول وضعیت + بخش `## Part N` هر پارت + مرجع HEX API).
2. اسکیل‌ها: `/mnt/skills/plugins/aria-game-maintainer/SKILL.md` (اگر نبود: `skills_copy/aria-game-maintainer/SKILL.md`). برای تست/بالانس: `skills_copy/aria-game-regression-qa`, `aria-gameplay-balance`.
3. پرامپت پارت بعدی: `prompts/PART4_prism_warden.md` — یا نسخه‌ی آماده‌ی چسباندن با زمینه‌ی بدون‌سرور: `paste/PASTE_PART4_prism_warden.md`.
4. شیت مفهومی: `reference_images/he4_*.png` (قبل از نوشتن نقاشی باید دیده شود).

## چیدمان
`game/` بازی‌ها (v31 پایه، `aria_v32_p1..p3.html`) · `tools/` پچ‌ها (`patch_v32_pN.py`)، تست‌ها (`he_pN_test.py` + لاگ)، ابزار زیپ (`make_pack.sh`, `make_paste.py`) · `prompts/` · `paste/` · `reference_images/` · `qa_shots_p2|p3/` · `skills_copy/` · `MANIFEST.sha256` (sha همه‌ی فایل‌ها: `sha256sum -c MANIFEST.sha256`).

## کار روزمره (هر پارت)
```
mkdir -p /home/claude/pack && cd /home/claude/pack && unzip -q -o /mnt/user-data/uploads/<zip>   # پوشه‌ی داخل زیپ را وارد شوید
python3 tools/patch_v32_pN.py game/aria_v32_p(N-1).html game/aria_v32_pN.html     # پچ جدید می‌نویسید (anchorهای assert‌دار)
python3 tools/he_pN_test.py game/aria_v32_p(N-1).html game/aria_v32_pN.html /home/claude/shotsN   # تست؛ ~۴۰ ثانیه
python3 tools/he_p(N-1)_test.py <p(N-2)> <pN>   # رگرسیون پارت قبلی روی خروجی جدید (باید سبز بماند)
bash tools/make_pack.sh P<N>done                 # MANIFEST + زیپ در /mnt/user-data/outputs، سپس present_files
```
پیش‌نیاز: python3 + playwright/chromium (در سندباکس هست) و node (برای `node --check` اسکریپت‌های داخل html).

## قوانین ثابت (نقض = باگ)
- Easy/Normal باید دقیقاً مثل v31 رفتار کنند، از جمله ترتیب/تعداد `Math.random`؛ همه‌چیز پشت `HE_ON && dif==2`. (تست parity هر پارت: Easy/Normal همه‌ی مراحل + Hard مراحل قبل از unlock.)
- در کد نقاشی `Math.random` ممنوع (فقط `tick` و `e.id`)؛ هر هوک رسم داخل save/restore و try/catch؛ هر خطا → `heFail` و بازی مثل v31 ادامه دارد.
- مارکرها: `/* ===== HE part N: ... ===== */` و `/*HE<N>*/` برای پچ‌های یک‌خطی داخل توابع موجود. ساعت HE برای سن/زمان‌بندی: `wdT` (نه `tick`).
- هرگز دو افکت کنترلی روی هم نیاورید؛ برای ریشه فقط `heRoot(n)`.
- پاسخ نهایی به کاربر فارسی؛ فقط تستی را «انجام‌شده» بگویید که واقعاً اجرا شده؛ خروجی = فایل html/zip در `/mnt/user-data/outputs` + `present_files` (کد خام در چت نه).
- اگر بودجه تمام می‌شود: وضعیت قابل‌لود + `game/aria_v32_pN_WIP.html` + چک‌لیست باقی‌مانده در HANDOFF.md + `bash tools/make_pack.sh P<N>WIP`.

## وضعیت (کوتاه)
Track A: P1 زیرساخت ✔ · P2 Root + Silk Widow ✔ · P3 Night-Fang ✔ · P4 Prism Warden · P5 Void Lantern · P6 Starmaw · P7 یکپارچه‌سازی/QA → `aria_v32.html`. Track B: P8–P13 → `aria_v33.html`. جزئیات و API: HANDOFF.md.
