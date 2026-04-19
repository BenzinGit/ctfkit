def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import tempfile

    domain = data.get("domain")
    dc = data.get("ip")
    quiet = getattr(args, "quiet", False)
    keep_logs = getattr(args, "keep_logs", False)

    if not domain:
        print("[!] Domain required")
        return

    users_file = getattr(args, "users", None) or "users.txt"
    output_file = args.out or f"valid_users_{dc}.txt"

    # temp log file (safer than hardcoding)
    log_file = Path(tempfile.mktemp(prefix="nxc_", suffix=".log"))

    # ---------------- SELECT COMMAND ----------------
    if args.no_auth or not cred:
        print("[*] Using kerbrute (no auth)")
        cmd = f"kerbrute userenum -d {domain} --dc {dc} {users_file}"
        mode = "kerbrute"
    else:
        user = cred["user"]
        typ = cred["type"]
        secret = cred["secret"]

        print("[*] Using LDAP (authenticated)")

        if typ == "password":
            cmd = f"nxc ldap {dc} -u {user} -p {secret} --users"
        elif typ == "ntlm":
            cmd = f"nxc ldap {dc} -u {user} -H {secret} --users"
        elif typ == "ticket":
            cmd = f"KRB5CCNAME={secret} nxc ldap {dc} --use-kcache --users"
        else:
            print("[!] Unsupported auth type for LDAP")
            return

        # attach log only for LDAP
        cmd += f" --log {log_file}"
        mode = "ldap"

    print(f"[*] Running: {cmd}\n")

    # ---------------- RUN (preserve color) ----------------
    subprocess.run(cmd, shell=True)

    # ---------------- PARSE ----------------
    valid_users = []

    # ---- kerbrute: fallback to stdout capture (no log support) ----
    if mode == "kerbrute":
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "VALID USERNAME" in line:
                valid_users.append(line.split()[-1])

    # ---- ldap: parse log file ----
    elif mode == "ldap":
        if not log_file.exists():
            print("[!] Log file missing, cannot parse")
            return

        def strip_prefix(line):
            if " - INFO - " in line:
                return line.split(" - INFO - ", 1)[1]
            return line

        capture = False

        for raw in log_file.read_text().splitlines():
            line = strip_prefix(raw)

            if "-Username-" in line:
                capture = True
                continue

            if not capture or not line.strip():
                continue

            parts = line.split()

            # expected: LDAP IP PORT DC USER ...
            if len(parts) >= 5 and parts[0] == "LDAP":
                user = parts[4]

                if not user.endswith("$"):
                    valid_users.append(user)

    # ---------------- SAVE ----------------
    if valid_users:
        Path(output_file).write_text("\n".join(sorted(set(valid_users))))
        print(f"\n[+] Saved {len(valid_users)} users to {output_file}")
    else:
        print("[!] No users found")

    # ---------------- CLEANUP ----------------
    if mode == "ldap" and not keep_logs:
        log_file.unlink(missing_ok=True)