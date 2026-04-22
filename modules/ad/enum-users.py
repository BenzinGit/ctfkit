def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import tempfile

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    domain = data.get("domain", "N/A")
    dc = data.get("ip", "N/A")
    quiet = getattr(args, "quiet", False)
    keep_logs = getattr(args, "keep_logs", False)

    users_file = getattr(args, "users", None) or "users.txt"
    output_file = args.out or f"valid_users_{dc}.txt"
    log_file = Path(tempfile.mktemp(prefix="nxc_", suffix=".log"))

    # ---------------- PRE-EXECUTION LOGIC ----------------
    is_unauth = (args.no_auth or not cred)
    mode = "kerbrute" if is_unauth else "ldap"
    
    if is_unauth:
        cmd = f"kerbrute userenum -d {domain} --dc {dc} {users_file}"
    else:
        user, typ, secret = cred["user"], cred["type"], cred["secret"]
        if typ == "password":
            cmd = f"nxc ldap {dc} -u {user} -p {secret} --users"
        elif typ == "ntlm":
            cmd = f"nxc ldap {dc} -u {user} -H {secret} --users"
        elif typ == "ticket":
            cmd = f"KRB5CCNAME={secret} nxc ldap {dc} --use-kcache --users"
        cmd += f" --log {log_file}"

    # ---------------- THE BOX (FIXED ALIGNMENT) ----------------
    inner_w = 54 # Matching your AS-REP Roast box width
    
    print(f"\n{B}┌── {BOLD}MODULE: USER ENUMERATION{W}{B} {'─' * (inner_w - 25)}┐{W}")
    
    # Row 1: Target
    target_val = f"{C}{domain}{W} {B}@{W} {C}{dc}{W}"
    # We strip the ANSI codes to calculate real padding length
    target_plain = f"{domain} @ {dc}"
    print(f"{B}│{W}  {B}Target:{W}   {target_val}{' ' * (inner_w - len(target_plain) - 10)} {B}│{W}")
    
    if is_unauth:
        # Row 2: Method
        print(f"{B}│{W}  {B}Method:{W}   {Y}Kerbrute (Unauthenticated){W}{' ' * (inner_w - 36)} {B}│{W}")
        # Row 3: Wordlist
        print(f"{B}│{W}  {B}Wordlist:{W} {W}{users_file:<{inner_w - 11}}{W} {B}│{W}")
    else:
        # Row 2: Method
        print(f"{B}│{W}  {B}Method:{W}   {W}LDAP (Authenticated){W}{' ' * (inner_w - 30)} {B}│{W}")
        # Row 3: Identity
        print(f"{B}│{W}  {B}Identity:{W} {C}{user:<{inner_w - 10}}{W} {B}│{W}")
        
    print(f"{B}└{'─' * (inner_w + 2)}─┘{W}")

    # Command Transparency
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {B}Executing:{W} {Y}{cmd}{W}\n")

    # ---------------- EXECUTION & PARSING ----------------
    if mode == "kerbrute":
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if not quiet: print(result.stdout)
        lines = result.stdout.splitlines()
    else:
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        lines = log_file.read_text().splitlines() if log_file.exists() else []

    valid_users = []
    if mode == "kerbrute":
        for line in lines:
            if "VALID USERNAME" in line:
                valid_users.append(line.split()[-1].split('@')[0])
    else:
        capture = False
        for raw in lines:
            line = raw.split(" - INFO - ", 1)[1] if " - INFO - " in raw else raw
            if "-Username-" in line:
                capture = True; continue
            if not capture or not line.strip(): continue
            parts = line.split()
            if len(parts) >= 5 and parts[0] == "LDAP":
                u = parts[4]
                if not u.endswith("$"): valid_users.append(u)

    # ---------------- THE LOOT BOX ----------------
    valid_users = sorted(list(set(valid_users)))
    if valid_users:
        Path(output_file).write_text("\n".join(valid_users))
        
        print(f"\n{G}┌── DISCOVERED USERS ──────────────────────────────────────┐{W}")
        for u in valid_users[:10]:
            print(f"{G}│{W}  {G}USER:{W} {BOLD}{u:<49}{W} {G}│{W}")
        if len(valid_users) > 10:
            print(f"{G}│{W}  {DIM}... and {len(valid_users)-10} more{W}{' ':<41} {G}│{W}")
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")
        print(f"{B}  └── {B}Artifact:{W} {Y}{output_file}{W}")
    else:
        print(f"\n{Y}[!] {W}No valid users identified.")

    if mode == "ldap" and not keep_logs:
        log_file.unlink(missing_ok=True)