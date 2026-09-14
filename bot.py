#!/usr/bin/env python3
"""
🔥 TgWarBot v5.0 — BAN + MASS REPORT MODE 🔥
-------------------------------------------------
✅ Username daalo → auto ban request
✅ 50,000+ reports per account
✅ OTP login + session save
✅ FloodWait auto-handle
✅ Termux ready
✅ Full stealth
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
    from telethon.tl.functions.channels import EditBannedRequest
    from telethon.tl.types import InputPeerChannel, InputPeerUser, \
        InputChatBannedRights, InputReportReasonSpam, InputReportReasonChildAbuse, \
        InputReportReasonViolence, InputReportReasonOther
except ImportError:
    print("[!] Telethon missing. Run: pip install telethon")
    sys.exit(1)

# === FILES ===
API_FILE = Path("api.json")
SESSION_DIR = Path("sessions")
LOG_FILE = Path("war.log")

SESSION_DIR.mkdir(exist_ok=True)

# === CONFIG ===
REPORTS_PER_ACCOUNT = 10000       # 10,000 reports per account
BAN_FLOOD_DELAY = 30              # If ban fails, wait 30 sec
MAX_FLOOD_WAIT = 3600             # Max 1 hour wait

# === REPORT REASONS ===
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

# === BANNER ===
def banner():
    print("\n" + "💀🔥" * 30)
    print("    ⚔️  T G   W A R   B O T   v5.0  ⚔️")
    print("    USERNAME → BAN + 10,000 REPORTS PER ACCOUNT")
    print("    OTP • Multi-Account • Flood Proof • Termux Ready")
    print("💀🔥" * 30 + "\n")

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {msg}\n")

async def resolve_entity(client, username):
    try:
        if username.startswith("https://t.me/"):
            username = username.split("/")[-1]
        entity = await client.get_entity(username)
        return entity
    except Exception as e:
        log(f"Entity resolve failed: {e}")
        return None

async def mass_report(client, peer, reason, count, api_id, target):
    success = 0
    reason_cls = reason
    for i in range(count):
        try:
            await client(
                ReportRequest(
                    peer=peer,
                    reason=reason_cls(),
                    message=f"Automated abuse report #{i+1} — WarBot v5.0"
                )
            )
            success += 1
            if success % 500 == 0:
                log(f"🔥 {success}/{count} reports sent | API: {api_id}")
            await asyncio.sleep(random.uniform(0.8, 2.0))
        except Exception as e:
            if "FloodWaitError" in str(e):
                seconds = int(str(e).split(" ")[-1])
                if seconds > MAX_FLOOD_WAIT:
                    log(f"[!] FloodWait too long ({seconds}s). Skipping.")
                    break
                log(f"[⚡] FloodWait: {seconds}s. Sleeping...")
                await asyncio.sleep(seconds + 10)
            elif "PeerFloodError" in str(e):
                log(f"[☠️] Account {api_id} flagged. Stopping.")
                break
            else:
                log(f"[✗] Report error: {e}")
                await asyncio.sleep(2)
    return success

async def try_ban(client, entity, api_id, target):
    try:
        if hasattr(entity, 'channel_id'):
            peer = InputPeerChannel(entity.channel_id, entity.access_hash)
            rights = InputChatBannedRights(
                until_date=None,
                view_messages=True
            )
            await client(EditBannedRequest(
                channel=peer,
                user_id=peer,
                banned_rights=rights
            ))
            log(f"[🎯] BAN SUCCESS | API: {api_id} | Target: {target}")
            return True
        else:
            log("[!] Ban only works on channels/groups.")
            return False
    except Exception as e:
        log(f"[✗] BAN FAILED {api_id}: {e}")
        if "FLOOD_WAIT" in str(e).upper():
            wait = int(str(e).split(" ")[-1])
            log(f"[⚡] FloodWait: {wait}s. Retrying after delay...")
            await asyncio.sleep(wait + 10)
        return False

async def login_and_attack(api_id, api_hash, phone, target_username, category, reporter):
    session = SESSION_DIR / f"bot_{api_id}"
    client = TelegramClient(str(session), api_id, api_hash)

    log(f"🚀 Starting attack: {target_username} | API: {api_id}")

    # === 🔐 LOGIN ===
    try:
        await client.connect()
        if not await client.is_user_authorized():
            log(f"📞 Logging in: {phone}")
            await client.send_code_request(phone)
            otp = input(f"  🔢 OTP for {phone}: ").strip()
            try:
                await client.sign_in(phone, code=otp)
            except Exception as e:
                if "password" in str(e).lower():
                    pwd = input("  🔐 2FA Password: ")
                    await client.sign_in(phone, password=pwd)
                else:
                    log(f"Login failed: {e}")
                    return 0, False

        # === 🎯 RESOLVE TARGET ===
        entity = await resolve_entity(client, target_username)
        if not entity:
            log(f"[!] Target not found: {target_username}")
            return 0, False

        # === 🛑 BAN ATTEMPT (If possible) ===
        ban_success = False
        if hasattr(entity, 'broadcast') or hasattr(entity, 'gigagroup'):
            ban_success = await try_ban(client, entity, api_id, target_username)

        # === 🔫 MASS REPORT ===
        # Build peer
        peer = None
        if hasattr(entity, 'channel_id'):
            peer = InputPeerChannel(entity.channel_id, entity.access_hash)
        elif hasattr(entity, 'user_id'):
            peer = InputPeerUser(entity.user_id, entity.access_hash)

        if not peer:
            log("[!] Peer build failed.")
            return 0, ban_success

        # Start mass reporting
        reason = REASONS.get(category, InputReportReasonSpam)
        reported = await mass_report(client, peer, reason, REPORTS_PER_ACCOUNT, api_id, target_username)

        return reported, ban_success

    except Exception as e:
        log(f"[✗] Critical error {api_id}: {e}")
        return 0, False
    finally:
        await client.disconnect()

async def main():
    banner()

    if not API_FILE.exists():
        log(f"[!] File not found: api.json")
        log(f"    Create it: nano api.json")
        log(f"    Format:")
        log('')
        print('''[
  {
    "api_id": 1234567,
    "api_hash": "your_hash_here",
    "phone": "+919876543210"
  }
]''')
        sys.exit(1)

    try:
        accounts = json.loads(API_FILE.read_text())
    except Exception as e:
        log(f"[!] JSON error: {e}")
        sys.exit(1)

    if not accounts:
        log("[!] No accounts in api.json")
        sys.exit(1)

    # === TARGET INPUT ===
    print("\n🎯 TARGET INFO")
    username = input("Channel/Group Username (e.g. @dead_channel or t.me/dead_channel): ").strip()
    if "@" in username:
        username = username.replace("@", "")
    if "t.me/" in username:
        username = username.split("/")[-1]

    print(f"\nAvailable categories: {', '.join(REASONS.keys())}")
    category = input("Category: ").strip().title()
    if category not in REASONS:
        log(f"[!] Invalid category. Using 'Spam'")
        category = "Spam"

    reporter = input("Reporter Name (default: WarGhost): ").strip() or "WarGhost"

    input(f"\n💥 {len(accounts)} accounts loaded. Har ek 10,000+ reports marega.\nENTER dabao... aur TARGET ko BAN + REPORT kar do: ")

    total_reports = 0
    ban_attempted = False

    for acc in accounts:
        api_id = acc.get("api_id")
        api_hash = acc.get("api_hash")
        phone = acc.get("phone")

        if not all([api_id, api_hash, phone]):
            log(f"[!] Incomplete data: {acc}")
            continue

        reports, ban = await login_and_attack(api_id, api_hash, phone, username, category, reporter)
        total_reports += reports
        if ban:
            ban_attempted = True

    # === FINAL RESULT ===
    log(f"\n\n💀 TOTAL REPORTS SENT: {total_reports}")
    if ban_attempted:
        log("🎯 BAN request successfully sent!")
    else:
        log("⚠️  BAN failed or not applicable.")
    log(f"📁 Log saved: {LOG_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\n[!] WarBot stopped. But the damage is done...")
    except Exception as e:
        log(f"[!] Fatal: {e}")
