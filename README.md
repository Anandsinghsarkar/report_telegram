# report_telegram
# Telegram Abuse Reporter

Ek simple CLI tool jo illegal Telegram content ki report
**abuse@telegram.org** par email ke through bhejta hai.

> Ye tool official abuse email channel use karta hai.
> Ye ek time par ek report bhejta hai — mass/automated reporting nahi karta.

## Features
- Interactive prompt: link, type, category, description
- Screenshot/video attachment support
- Local log (`reports_log.jsonl`)
- SMTP config `.env` se (Gmail App Password support)

## Install (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/<your-username>/telegram-abuse-reporter.git
cd telegram-abuse-reporter
pip install -r requirements.txt
cp .env.example .env
nano .env   # apna email + app password daalo
```

## Run

```bash
python report_telegram.py
```

## Gmail App Password kaise banaye
1. Google Account → Security → 2-Step Verification ON karo
2. Security → App passwords → "Mail" + "Other (Termux)" chuno
3. 16-character password milega — wahi `SMTP_PASS` me daalo

## File path Termux me
Android storage access ke liye:
```bash
termux-setup-storage
ls ~/storage/shared/Pictures
```

## Usage flow
1. Telegram link daalo (`https://t.me/...`)
2. Type chuno (Channel / Group / User / Message)
3. Category chuno
4. Description likho (kya illegal hai, kab dekha)
5. Screenshot paths do (optional)
6. Reporter naam do
7. Preview dekh ke `yes` type karo — mail chali jaayegi

## Safety / Rules
- Sirf genuine illegal content report karo
- CSAM ho to download/share **mat** karo — direct police + NCMEC
- False reporting illegal ho sakti hai
- India me: `cybercrime.gov.in` par bhi complaint karo
- Financial fraud: **1930**

## License
MIT
