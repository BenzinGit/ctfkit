def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import tempfile

    G, C, B, Y, W = '\033[92m','\033[96m','\033[94m','\033[93m','\033[0m'
    BOLD, DIM = '\033[1m','\033[2m'

    domain = data.get("domain", "N/A")
    dc = data.get("ip", "N/A")
    quiet = getattr(args, "quiet", False)
    keep_logs = getattr(args, "keep_logs", False)

    output_file = args.out or f"valid_users_{dc}.txt"
    log_file = Path(tempfile.mktemp(prefix="nxc_", suffix=".log"))

    user, typ, secret = cred["user"], cred["type"], cred["secret"]

    if typ == "password":
        cmd = f"nxc ldap {dc} -u {user} -p {secret} --users"
    elif typ == "ntlm":
        cmd = f"nxc ldap {dc} -u {user} -H {secret} --users"
    elif typ == "ticket":
        cmd = f"KRB5CCNAME={secret} nxc ldap {dc} --use-kcache --users"

    cmd += f" --log {log_file}"

    # --- BOX ---
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: USER ENUM (LDAP){W}{B} {'─'*(inner_w-26)}┐{W}")
    print(f"{B}│{W}  {B}Target:{W}   {C}{domain}{W} {B}@{W} {C}{dc}{W}{' '*(inner_w-len(domain+dc)-13)} {B}│{W}")
    print(f"{B}│{W}  {B}Method:{W}   {W}LDAP (Authenticated){W}{' '*(inner_w-30)} {B}│{W}")
    print(f"{B}│{W}  {B}Identity:{W} {C}{user:<{inner_w-10}}{W} {B}│{W}")
    print(f"{B}└{'─'*(inner_w+2)}─┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}] Executing:{W} {Y}{cmd}{W}\n")

    subprocess.run(cmd, shell=True, capture_output=True, text=True)

    users = []
    if log_file.exists():
        capture = False
        for raw in log_file.read_text().splitlines():
            line = raw.split(" - INFO - ",1)[1] if " - INFO - " in raw else raw

            if "-Username-" in line:
                capture = True
                continue

            if not capture or not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 5 and parts[0] == "LDAP":
                u = parts[4]
                if not u.endswith("$"):
                    users.append(u)

    users = sorted(set(users))

    if users:
        Path(output_file).write_text("\n".join(users))
        print(f"\n{G}[+] Found {len(users)} users → {output_file}{W}")
    else:
        print(f"\n{Y}[!] No users found{W}")

    if not keep_logs:
        log_file.unlink(missing_ok=True)