def run(data, cred, args):
    import subprocess
    from pathlib import Path

    G, C, B, Y, W = '\033[92m','\033[96m','\033[94m','\033[93m','\033[0m'
    BOLD, DIM = '\033[1m','\033[2m'

    domain = data.get("domain", "N/A")
    dc = data.get("ip", "N/A")
    quiet = getattr(args, "quiet", False)

    output_file = args.out or f"valid_users_{dc}.txt"

    target = dc if dc != "N/A" else domain
    cmd = f"impacket-lookupsid anonymous@{target} -no-pass"

    # --- BOX ---
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: USER ENUM (LOOKUPSID){W}{B} {'─'*(inner_w-32)}┐{W}")
    print(f"{B}│{W}  {B}Target:{W}   {C}{target}{W}{' '*(inner_w-len(target)-10)} {B}│{W}")
    print(f"{B}│{W}  {B}Method:{W}   {Y}Impacket lookupsid{W}{' '*(inner_w-29)} {B}│{W}")
    print(f"{B}└{'─'*(inner_w+2)}─┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}] Executing:{W} {Y}{cmd}{W}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if not quiet:
        print(result.stdout)

    # --- ALWAYS PARSE ---
    users = []
    for line in result.stdout.splitlines():
        if "SidTypeUser" in line:
            try:
                raw = line.split(":")[1].split("(")[0].strip()

                # remove DOMAIN\
                if "\\" in raw:
                    raw = raw.split("\\", 1)[1]

                # skip machine accounts
                if not raw.endswith("$"):
                    users.append(raw)

            except:
                pass

    users = sorted(set(users))

    # --- OUTPUT ---
    if users:
        Path(output_file).write_text("\n".join(users))
        print(f"\n{G}[+] Found {len(users)} users → {output_file}{W}")
    else:
        print(f"\n{Y}[!] No users found{W}")

    return users