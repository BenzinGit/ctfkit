def run(data, cred, args):
    import subprocess
    from pathlib import Path

    domain = data.get("domain")
    dc = data.get("ip")
    quiet = getattr(args, "quiet", False)

    if not domain:
        print("[!] Domain required")
        return

    users_file = getattr(args, "users", None) or "users.txt"
    output_file = args.out or f"valid_users_{dc}.txt"

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

        mode = "ldap"

    print(f"[*] Running: {cmd}\n")

    # ---------------- RUN ----------------
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if not quiet and result.stdout:
        print(result.stdout)

    # ---------------- PARSE ----------------
    valid_users = []

    if mode == "kerbrute":
        for line in result.stdout.splitlines():
            if "VALID USERNAME" in line:
                user = line.split()[-1]
                valid_users.append(user)

    elif mode == "ldap":
        capture = False

        for line in result.stdout.splitlines():
            if "-Username-" in line:
                capture = True
                continue

            if not capture:
                continue

            if not line.strip():
                continue

            try:
                parts = [p for p in line.split(" ") if p]
                user = parts[4]

                if user.endswith("$"):
                    continue

                valid_users.append(user)

            except:
                continue

    # ---------------- SAVE ----------------
    if valid_users:
        Path(output_file).write_text("\n".join(sorted(set(valid_users))))
        print(f"\n[+] Saved {len(valid_users)} users to {output_file}")
    else:
        print("[!] No users found")