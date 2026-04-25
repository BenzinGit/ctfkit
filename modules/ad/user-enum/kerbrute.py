def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import tempfile

    G, C, B, Y, W = '\033[92m','\033[96m','\033[94m','\033[93m','\033[0m'
    BOLD, DIM = '\033[1m','\033[2m'

    domain = data.get("domain", "N/A")
    dc = data.get("ip", "N/A")
    quiet = getattr(args, "quiet", False)

    users_file = getattr(args, "users", None) or "users.txt"
    output_file = args.out or f"valid_users_{dc}.txt"

    cmd = f"kerbrute userenum -d {domain} --dc {dc} {users_file}"

    # --- BOX ---
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: USER ENUM (KERBRUTE){W}{B} {'─'*(inner_w-30)}┐{W}")
    print(f"{B}│{W}  {B}Target:{W}   {C}{domain}{W} {B}@{W} {C}{dc}{W}{' '*(inner_w-len(domain+dc)-13)} {B}│{W}")
    print(f"{B}│{W}  {B}Method:{W}   {Y}Kerbrute{W}{' '*(inner_w-20)} {B}│{W}")
    print(f"{B}│{W}  {B}Wordlist:{W} {users_file:<{inner_w-11}} {B}│{W}")
    print(f"{B}└{'─'*(inner_w+2)}─┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}] Executing:{W} {Y}{cmd}{W}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not quiet:
        print(result.stdout)

    users = []
    for line in result.stdout.splitlines():
        if "VALID USERNAME" in line:
            users.append(line.split()[-1].split("@")[0])

    users = sorted(set(users))

    if users:
        Path(output_file).write_text("\n".join(users))
        print(f"\n{G}[+] Found {len(users)} users → {output_file}{W}")
    else:
        print(f"\n{Y}[!] No users found{W}")