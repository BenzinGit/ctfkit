def run(data, cred, args):
    import subprocess
    from pathlib import Path

    domain = data.get("domain")
    dc = data.get("ip")

    if not domain:
        print("[!] Domain required")
        return

    users_file = args.users or "users.txt"
    output_file = args.out or f"valid_users_{dc}.txt"

    # ---------------- NO CREDS → KERBRUTE ----------------
    if args.no_auth or not cred:
        cmd = f"kerbrute userenum -d {domain} --dc {dc} {users_file}"

        print(f"[*] Using kerbrute (no auth)")
        print(f"[*] Running: {cmd}\n")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        print(result.stdout)

        valid_users = []
        for line in result.stdout.splitlines():
            if "VALID USERNAME" in line:
                user = line.split()[-1]
                valid_users.append(user)

    # ---------------- WITH CREDS → LDAP ----------------
    else:
        user = cred["user"]
        typ = cred["type"]
        secret = cred["secret"]

        print(f"[*] Using LDAP (authenticated)")

        if typ == "password":
            cmd = f"nxc ldap {dc} -u {user} -p {secret} --users"

        elif typ == "ntlm":
            cmd = f"nxc ldap {dc} -u {user} -H {secret} --users"

        elif typ == "ticket":
            cmd = f"KRB5CCNAME={secret} nxc ldap {dc} --use-kcache --users"

        else:
            print("[!] Unsupported auth type for LDAP")
            return

        print(f"[*] Running: {cmd}\n")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        print(result.stdout)

        # ---------------- PARSE USERS ----------------
        valid_users = []
        capture = False

        for line in result.stdout.splitlines():
            if "-Username-" in line:
                capture = True
                continue

            if not capture:
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Extract username (column after hostname junk)
            try:
                # Split by spaces, remove empty chunks
                parts = [p for p in line.split(" ") if p]

                # Username is always the LAST fixed column BEFORE timestamps
                # In your output it's around index 4–5, but safer:
                user = parts[4]

                # Skip machine accounts
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