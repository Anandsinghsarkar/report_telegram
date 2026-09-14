# 🔥 TgAbuseReporter v3.0 — Khatarnak Telegram Reporter

> "Jo report karega, wahi ban jayega hunter."  

A full stealth, multi-account abuse reporter for Telegram.  
Bina kisi email ke, seedhe **Telegram ke official API** se illegal content ki report maar do.

Works on **Termux (Android)** and Linux.

---

### 📦 Features
- ✅ Unlimited API ID + HASH support
- ✅ Rotates between accounts (anti-ban)
- ✅ No email required — direct Telegram API
- ✅ Works in Termux (Android)
- ✅ Logs everything
- ✅ Easy setup
- ✅ Khatarnak Mode ON 😈

---

### 🚀 Install & Run (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/Anandsinghsarkar/report_telegram.git
cd report_telegram
python -m pip install -r requirements.txt
python bot.py
