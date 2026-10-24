# STATE.md — جای checkpoint سرور (آخرین به‌روزرسانی: اکانت A4)

## خلاصه
پارت ۱ (A2)، پارت ۲ (A4) و پارت ۳ (A4) تمام و تست شده‌اند. آخرین خروجی بازی: `game/aria_v32_p3.html`. گام بعدی: **پارت ۴ — Prism Warden (t7)**: ورودی `game/aria_v32_p3.html` → خروجی `game/aria_v32_p4.html`.

## فایل‌ها (اندازه · sha ۸ نویسه)
- `game/aria_v32_p3.html` · 876625B · sha f675636d
- `game/aria_v32_p2.html` · 861669B · sha cf03c57b
- `game/aria_v32_p1.html` · 842144B · sha bd1a65e4
- `game/aria_v31.html` · 835566B · sha f0c902bd
- `tools/patch_v32_p3.py` · 15747B · sha df21cf25
- `tools/he_p3_test.py` · 37513B · sha ec7ffa4d
- `tools/he_p2_test.py` · 34838B · sha bc1d2631
- `tools/patch_v32_p2.py` · 21505B · sha 079b241b

## تست‌ها (آخرین اجرا، همه سبز)
- `he_p1_test.py`: ۱۰۶ چک روی p1 (روی p2/p3 فقط چک «HEX خالی» عمداً قرمز است)
- `he_p2_test.py <p1> <p2|p3>`: ۱۳۳/۱۳۳ روی هر دو
- `he_p3_test.py <p2> <p3>`: ۱۳۴/۱۳۴ (parity p2↔p3، رجیستری، patrol/hunt، crouch ۲۸f، قفل هدف، پرش بالستیک، گودال/خار/گدازه/سکوی متحرک، feint، موج‌ها، stomp/daze/damage، ۷ مسیر heFail، نقاشی/determinism، fuzz روی ۵ مرحله)

## تصمیم‌های کلیدی (دلیل‌ها در HANDOFF.md → Part 2/3)
- `lowSpd 4` برای Widow punish؛ `startV 10 < maxV 11` + feint فقط وقتی هنوز قابل‌حل است (`fgFeintOK`)؛ پرش فقط روی سکوی ایستا؛ زمان‌های HE با `wdT`.

## گام‌های بعدی (ترتیب)
1. زیپ را باز کنید، `sha256sum -c MANIFEST.sha256` (باید همه OK باشد).
2. PART 4 (Prism Warden): `prompts/PART4_prism_warden.md` یا `paste/PASTE_PART4_prism_warden.md`؛ شیت `reference_images/he4_prism_warden.png`.
3. بعد P5 Void Lantern، P6 Starmaw، P7 یکپارچه‌سازی (`aria_v32.html`)، سپس مسیر B (P8–P13 → `aria_v33.html`).

## سرور
MCP (`resume_project`, `save_checkpoint`) کار می‌کند ولی ابزار اجرای کد دامنه‌ی `sharedmemory.serveousercontent.com` را resolve نمی‌کند → آپلود فایل ممکن نیست؛ انتقال فقط دستی (همین زیپ). اگر کاربر دامنه را allowlist کرد: `cfile put` مطابق دستورالعمل اکانت و ثبت sha در checkpoint.
