#!/usr/bin/env python3
"""
Telegram Abuse Reporter
-----------------------
Ek simple tool jo illegal Telegram content ki official report
abuse@telegram.org par email ke through bhejta hai.

Author: <your-name>
License: MIT
"""

import os
import sys
import ssl
import json
import smtplib
import datetime
from pathlib import Path
from email.message import EmailMessage
from email.utils import formataddr

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

REPORT_LOG = Path("reports_log.jsonl")
ABUSE_EMAIL = "abuse@telegram.org"

CATEGORIES = [
    "Child Sexual Abuse Material (CSAM)",
    "Terrorism / Violent Extremism",
    "Drugs / Illegal Goods",
    "Financial Scam / Fraud",
    "Piracy / Copyright",
    "Harassment / Threats",
    "Doxxing / Privacy Violation",
    "Impersonation",
    "Other",
]

TYPES = ["Channel", "Group", "User", "Message"]


def banner():
    print("=" * 60)
    print("  Telegram Abuse Reporter  (official email mode)")
    print("  Reports are sent ONE AT A TIME to abuse@telegram.org")
    print("=" * 60)


def ask(prompt, required=True, default=None):
    while True:
        val = input(prompt).strip()
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("  ! Ye field zaroori hai.")


def choose(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            idx = int(input("Number chuno: ").strip())
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass
        print("  ! Sahi number daalo.")


def collect_report():
    print("\n--- Naya Report ---")
    link = ask("Telegram link (https://t.me/...): ")
    if not link.startswith("http"):
        link = "https://" + link.lstrip("/")

    rtype = choose("Type kya hai?", TYPES)
    category = choose("Category chuno:", CATEGORIES)
    description = ask("Description (kya illegal hai, kab dekha): ")

    print("\nScreenshots ka poora path do (comma se alag karo, Enter = skip)")
    print("Example: /sdcard/Pictures/ss1.png,/sdcard/Pictures/ss2.png")
    files_raw = input("Files: ").strip()
    files = [Path(f.strip()) for f in files_raw.split(",") if f.strip()] if files_raw else []

    valid_files = []
    for f in files:
        if f.exists():
            valid_files.append(f)
        else:
            print(f"  ! File nahi mili: {f}")

    reporter = ask("Tumhara naam/handle (Reporter): ", default="Anonymous")

    return {
        "link": link,
        "type": rtype,
        "category": category,
        "description": description,
        "files": valid_files,
        "reporter": reporter,
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


def build_email(rep, sender_email):
    subject = f"Report of illegal content on Telegram - {rep['category']}"
    body = f"""To: {ABUSE_EMAIL}
Subject: {subject}

Telegram link: {rep['link']}
Type: {rep['type']}
Category: {rep['category']}
Description:
{rep['description']}

Evidence: attached screenshots ({len(rep['files'])} file(s))
Date/time (reporter local): {rep['datetime']}
Reporter: {rep['reporter']}

--
This report was sent manually via Telegram Abuse Reporter tool.
I confirm the content described above appears to violate Telegram's
Terms of Service / applicable law. Evidence is attached for review.
"""

    msg = EmailMessage()
    msg["From"] = formataddr((rep["reporter"], sender_email))
    msg["To"] = ABUSE_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    for f in rep["files"]:
        mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
        if f.suffix.lower() in (".mp4", ".mov"):
            mime = "video/mp4"
        with open(f, "rb") as fh:
            msg.add_attachment(
                fh.read(),
                maintype=mime.split("/")[0],
                subtype=mime.split("/")[1],
                filename=f.name,
            )
    return msg


def send_email(msg, smtp_host, smtp_port, user, password):
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as s:
        s.login(user, password)
        s.send_message(msg)


def log_report(rep, status):
    entry = {
        "time": datetime.datetime.now().isoformat(),
        "link": rep["link"],
        "type": rep["type"],
        "category": rep["category"],
        "reporter": rep["reporter"],
        "attachments": [str(f) for f in rep["files"]],
        "status": status,
    }
    with open(REPORT_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    banner()

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    sender = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    if not sender or not password:
        print("\n[!] SMTP credentials nahi mile.")
        print("    .env file banao (dekho .env.example) ya export karo:")
        print("      export SMTP_USER='you@gmail.com'")
        print("      export SMTP_PASS='app-password'")
        sys.exit(1)

    rep = collect_report()

    print("\n--- Preview ---")
    print(f"To       : {ABUSE_EMAIL}")
    print(f"Link     : {rep['link']}")
    print(f"Type     : {rep['type']}")
    print(f"Category : {rep['category']}")
    print(f"Files    : {[f.name for f in rep['files']]}")
    print(f"Reporter : {rep['reporter']}")

    confirm = input("\nBhej du? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancel kar diya.")
        return

    try:
        msg = build_email(rep, sender)
        send_email(msg, smtp_host, smtp_port, sender, password)
        log_report(rep, "sent")
        print("\n[✓] Report bhej di gayi abuse@telegram.org ko.")
        print("    Log:", REPORT_LOG.resolve())
    except Exception as e:
        log_report(rep, f"failed: {e}")
        print(f"\n[✗] Bhejne me error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRok diya.")
