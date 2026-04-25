def run(args):
    from core.runner import run_module_by_name
    from core.target import load_current_profile
    from core.paths import get_chain_artifacts_dir

    data, _ = load_current_profile()

    domain = data.get("domain")
    dc = data.get("ip")

    artifacts = get_chain_artifacts_dir(data["name"], "enum-users")
    users_file = artifacts / "enum_users.txt"

    found_users = set()

    # ---------------- DECISION LOGIC ----------------
    has_creds = getattr(args, "username", None) or getattr(args, "hash", None) or getattr(args, "password", None)
    has_list = getattr(args, "users", None)

    # ---------------- LDAP (priority if creds exist) ----------------
    if has_creds:
        print("[*] Enumerating users via LDAP (authenticated)...")

        ldap_args = []
        if args.username:
            ldap_args.extend(["-u", args.username])
        if args.password:
            ldap_args.extend(["-p", args.password])
        if args.hash:
            ldap_args.extend(["-H", args.hash])

        ldap_args.extend(["--out", str(users_file), "--quiet"])

        result = run_module_by_name("ad.user-enum.ldap", ldap_args, data)

        if result:
            found_users |= set(result)

    # ---------------- KERBRUTE (if list provided) ----------------
    if has_list:
        print("[*] Enumerating users via Kerbrute...")

        kb_args = [
            "--users", args.users,
            "--out", str(users_file),
            "--quiet"
        ]

        result = run_module_by_name("ad.user-enum.kerbrute", kb_args, data)

        if result:
            found_users |= set(result)

    # ---------------- LOOKUPSID (fallback) ----------------
    if not has_creds and not has_list:
        print("[*] Enumerating users via lookupsid (RID cycling)...")

        ls_args = [
            "--out", str(users_file),
            "--quiet"
        ]

        result = run_module_by_name("ad.user-enum.lookupsid", ls_args, data)

        if result:
            found_users |= set(result)

    # ---------------- OUTPUT ----------------

