#!/usr/bin/env python3
"""
🔥 TgAbuseReporter — Khatarnak Mode Activated
-------------------------------------------------
Direct Telegram API abuse reporting.
Supports multiple API accounts. Made for Termux.
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
    from telethon import TelegramClient, errors
    from telethon.tl.types import InputPeerChannel, InputPeerUser, \
        InputReportReasonChildAbuse, InputReportReasonViolence, \
        InputReportReasonSpam, InputReportReasonOther
except ImportError:
    print("[!] Telethon nahi mila. Chalao: python -m pip install -r requirements.txt")
    sys.exit(1)

# === PATHS ===
ROOT = Path(__file__).parent.resolve()
SESSION_DIR = ROOT / "sessions"
DATA_DIR = ROOT / "data"
API_FILE = DATA_DIR / "api_accounts.json"
LOG_FILE = DATA_DIR / "reports_log.jsonl"

# Create dirs
for d in [SESSION_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

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
    print("\n" + "=" * 65)
    print("  🔥🔥🔥  K H A T A R N A K   T E L E G R A M   R E P O R T E R  🔥🔥🔥")
    print("  💀 DIRECT API ABUSE REPORT — NO EMAIL, NO TRACE 💀")
    print("  Made for Termux | Stealth Mode: ON | Rotation: ENABLED")
    print("=" * 65 + "\n")

def log_event(link, category, reporter, api_id, status):
    entry = {
        "time": datetime.now().isoformat(),
        "link": link,
        "category": category,
        "reporter": reporter,
        "via_api_id": api_id,
        "status": status,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def save_api(api_id: int, api_hash: str):
    data = json.loads(API_FILE.read_text()) if API_FILE.exists() else []
    data.append({
        "api_id": api_id,
        "api_hash": api_hash,
        "added": datetime.now().isoformat()
    })
    API_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[✓] API ID {api_id} saved.\n")

async def resolve_entity(client, link):
    try:
        entity = await client.get_entity(link)
        return entity
    except Exception as e:
        print(f"[!] Entity load failed: {e}")
        return None

def choose(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            idx = int(input("Number chuno: ").strip())
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except:
            pass
        print("  ! Sahi number daalo.")

def ask(prompt, default=None):
    val = input(prompt).strip()
    return val if val else default

async def start_clients(clients):
    active = []
    for client in clients:
        try:
            await client.connect()
            if await client.is_user_authorized():
                active.append(client)
            else:
                print(f"[-] Client not logged in: {client.session.filename}")
        except Exception as e:
            print(f"[✗] Connection fail: {e}")
    return active

async def report_target(client, peer, reason_cls, desc=""):
    try:
        await client(ReportRequest(
            peer=peer,
            reason=reason_cls(),
            message=desc[:1024]
        ))
        return True
    except errors.PeerFloodError:
        print("[-] Flood detected — account flagged. Skip.")
        return False
    except errors.UserBannedInChannelError:
        print("[-] User banned. Skip.")
        return False
    except Exception as e:
        print(f"[✗] Report error: {e}")
        return False

async def main():
    banner()

    # First run: Add API
    if "--add" in sys.argv or not API_FILE.exists() or os.stat(API_FILE).st_size == 0:
        print("--- 🛠️  NEW API ACCOUNT SETUP ---")
        try:
            api_id = int(ask("Enter API ID: "))
            api_hash = ask("Enter API HASH: ")
            if api_id and api_hash:
                save_api(api_id, api_hash)
                print("[✓] Ab tumhari takat shuru ho rahi hai...\n")
            else:
                print("[!] API ID aur HASH dono chahiye.")
        except ValueError:
            print("[!] Number galat hai.")
        return

    # Load APIs
    try:
        apis = json.loads(API_FILE.read_text())
    except Exception as e:
        print(f"[!] API file corrupt: {e}")
        return

    if not apis:
        print("[!] Koi API nahi mili. Chalao: python reporter.py --add")
        return

    # Build clients
    clients = []
    for i, cred in enumerate(apis):
        session = SESSION_DIR / f"bot_{i}"
        client = TelegramClient(str(session), cred["api_id"], cred["api_hash"])
        clients.append((client, cred["api_id"]))

    print(f"[*] {len(clients)} accounts loaded. Connecting...")

    active_clients = []
    for client, api_id in clients:
        try:
            await client.connect()
            if await client.is_user_authorized():
                active_clients.append((client, api_id))
            else:
                print(f"[-] Not authorized: Session {api_id}")
        except Exception as e:
            print(f"[✗] Failed: {e}")

    if not active_clients:
        print("[!] Koi active account nahi. 'python reporter.py --add' use karo.")
        return

    print(f"[✓] {len(active_clients)} accounts ready for war.")

    # Collect report
    print("\n--- 🎯 TARGET INFO ---")
    link = ask("Telegram link (https://t.me/...): ").strip()
    if not link.startswith("http"):
        link = "https://t.me/" + link.lstrip("/").split("/")[0]

    ctype = choose("Type chuno:", TYPES)
    category = choose("Category chuno:", list(REASONS.keys()))
    description = ask("Description (optional): ", default="Khatarnak content. Action required.")

    reporter = ask("Tera naam / handle: ", default="Anonymous")

    # Shuffle clients
    random.shuffle(active_clients)
    success = False

    for client, api_id in active_clients:
        print(f"\n[→] Attack via API ID: {api_id}...")
        entity = await resolve_entity(client, link)
        if not entity:
            continue

        # Build peer
        try:
            if hasattr(entity, 'channel_id'):
                peer = InputPeerChannel(entity.channel_id, entity.access_hash)
            elif hasattr(entity, 'user_id'):
                peer = InputPeerUser(entity.user_id, entity.access_hash)
            else:
                print("[!] Unsupported target type.")
                continue
        except Exception as e:
            print(f"[!] Peer build error: {e}")
            continue

        # Send report
        reason_class = REASONS[category]
        sent = await report_target(client, peer, reason_class, description)

        if sent:
            log_event(link, category, reporter, api_id, "success")
            print(f"[🔥] REPORT SUCCESS — API ID: {api_id}")
            success = True
            time.sleep(random.uniform(3, 7))  # Random delay
            break
        else:
            log_event(link, category, reporter, api_id, "failed")
            time.sleep(2)

    if not success:
        print("\n[☠️] Sab accounts fail ho gaye. Zyaada darr lagta hai kya? 😈")

    print(f"\n[✓] Log saved: {LOG_FILE.name}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Tool rok diya. Par duniya ab teri nazaron mein badal chuki hai...")
    except Exception as e:
        print(f"[!] Crash: {e}")
