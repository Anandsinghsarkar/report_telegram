#!/usr/bin/env python3
"""
🔥 TgAbuseReporter v4.0 — BOTNET MODE 🔥
-------------------------------------------------
✅ 5000 REPORTS PER ACCOUNT
✅ AUTO OTP LOGIN
✅ MULTI-ACCOUNT ROTATION
✅ FULL TERMUX SUPPORT
✅ STEALTH + PERSISTENT

> "Jab tak report na ruke, tab tak bot na soye."
"""

import os
import sys
import json
import time
import random
import asyncio
from datetime import datetime
from pathlib import Path

try:
    from telethon import TelegramClient, events
    from telethon.tl.types import InputPeerChannel, InputPeerUser, \
        InputReportReasonChildAbuse, InputReportReasonViolence, \
        InputReportReasonSpam, InputReportReasonOther
except ImportError:
    print("[!] Telethon missing. Run: pip install -r requirements.txt")
    sys.exit(1)

# === PATHS ===
ROOT = Path(__file__).parent.resolve()
SESSION_DIR = ROOT / "sessions"
DATA_DIR = ROOT / "data"
API_FILE = DATA_DIR / "api_accounts.json"
LOG_FILE = DATA_DIR / "reports_log.jsonl"

for d in [SESSION_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

# === REPORT LIMIT ===
REPORTS_PER_ACCOUNT = 5000  # 🔥 5000 per account

# === REPORT REASONS ===
REASONS = {
    "Child Sexual Abuse Material (CSAM)": InputReportReasonChildAbuse,
    "Terrorism / Violent Extremism": InputReportReasonViolence,
    "Drugs / Illegal Goods": InputReportReasonSpam,
    "Financial Scam / Fraud": InputReportReasonSpam,
    "Piracy / Copyright": InputReportReasonOther,
    "Harassment / Threats": InputReportReasonSpam,
    "Doxxing / Privacy Violation": InputReportReasonOther,
    "Impersonation": InputReportReasonOther,
    "Other": InputReportReasonOther,
}

TYPES = ["Channel", "Group", "User"]

# === BANNER ===
def banner():
    print("\n" + "🔥" * 40)
    print("    K H A T A R N A K   A B U S E   B O T N E T   v4.0")
    print("    5000 REPORTS × UNLIMITED ACCOUNTS = TOTAL CHAOS")
    print("    OTP LOGIN • AUTO SESSION • FULL TERMUX SUPPORT")
    print("🔥" * 40 + "\n")

def log_report(link, category, api_id, status):
    entry = {
        "time": datetime.now().isoformat(),
        "link": link,
        "category": category,
        "via_api_id": api_id,
        "status": status,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

async def login_and_report(api_id, api_hash, phone, target, category, reporter_name):
    session_path = SESSION_DIR / f"bot_{api_id}"
    client = TelegramClient(str(session_path), api_id, api_hash)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[→] Logging in: {phone}")
            await client.send_code_request(phone)
            otp = input(f"  ✉️  OTP for {phone}: ").strip()
            try:
                await client.sign_in(phone, code=otp)
            except Exception as e:
                if "password" in str(e).lower():
                    pwd = input("  🔐 2FA Password: ")
                    await client.sign_in(password=pwd)
                else:
                    raise e
            print(f"[✓] Logged in: {phone}")

        # Now start reporting
        reason_class = REASONS[category]
        entity = await client.get_entity(target)
        if hasattr(entity, 'channel_id'):
            peer = InputPeerChannel(entity.channel_id, entity.access_hash)
        elif hasattr(entity, 'user_id'):
            peer = InputPeerUser(entity.user_id, entity.access_hash)
        else:
            print("[!] Unsupported target")
            return 0

        success_count = 0
        for i in range(REPORTS_PER_ACCOUNT):
            try:
                await client(ReportRequest(
                    peer=peer,
                    reason=reason_class(),
                    message=f"Abuse report #{i+1} by {reporter_name}"
                ))
                success_count += 1
                log_report(target, category, api_id, "success")
                print(f"[🔥] REPORT {success_count}/5000 | API: {api_id} | Target: {target}")
                
                # Random delay to avoid flood
                await asyncio.sleep(random.uniform(1.5, 4.0))
            except errors.FloodWaitError as e:
                print(f"[⚡] FloodWait: {e.seconds} seconds. Sleeping...")
                await asyncio.sleep(e.seconds + 10)
            except errors.PeerFloodError:
                print(f"[☠️] Account {api_id} permanently flagged. Stopping.")
                break
            except Exception as e:
                log_report(target, category, api_id, f"fail: {e}")
                print(f"[✗] Error: {e}")
                await asyncio.sleep(2)

        return success_count

    except Exception as e:
        print(f"[✗] Login failed {api_id}: {e}")
        log_report(target, category, api_id, f"login_fail: {e}")
        return 0
    finally:
        await client.disconnect()

async def main():
    banner()

    if not API_FILE.exists():
        print(f"[!] {API_FILE} nahi mili.")
        print("    Template de rakha hai — apne API ID, HASH, phone daalo.")
        sys.exit(1)

    try:
        accounts = json.loads(API_FILE.read_text())
    except Exception as e:
        print(f"[!] JSON parse error: {e}")
        sys.exit(1)

    if not accounts:
        print("[!] Koi account nahi mila.")
        sys.exit(1)

    # Get target
    print("\n🎯 TARGET INFO")
    target = input("Telegram link (https://t.me/...): ").strip()
    if not target.startswith("http"):
        target = "https://t.me/" + target.lstrip("/").split("/")[0]

    category = input(f"Category {list(REASONS.keys())}:\n> ").strip()
    if category not in REASONS:
        print("[!] Invalid category. Using 'Other'.")
        category = "Other"

    reporter_name = input("Reporter Name (default: Ghost): ").strip() or "Ghost"

    print(f"\n[✓] Target set: {target}")
    print(f"    Category: {category}")
    print(f"    Reports per account: {REPORTS_PER_ACCOUNT}")
    print(f"    Total accounts: {len(accounts)}")
    input("\nENTER dabao jab taiyar ho sabko jalane ke liye...")

    total_reports = 0
    for acc in accounts:
        api_id = acc["api_id"]
        api_hash = acc["api_hash"]
        phone = acc["phone"]

        print(f"\n🚀 STARTING ACCOUNT: {phone} | API ID: {api_id}")
        count = await login_and_report(api_id, api_hash, phone, target, category, reporter_name)
        total_reports += count

        print(f"[📊] Account {api_id} finished: {count} reports")

    print(f"\n\n💀 TOTAL REPORTS SENT: {total_reports}")
    print(f"    Log: {LOG_FILE.name}")
    print("    Ab Telegram tumhare paon me hai.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Botnet rok diya. Lekin kuch reports toh pahuch chuke honge... 😈")
    except Exception as e:
        print(f"[!] Fatal: {e}")
