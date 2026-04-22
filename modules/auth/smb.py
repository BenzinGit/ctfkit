import subprocess
import os

def run(data, cred, args):
    from core.target import load_current_profile

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    ip = data.get("ip")
    hostname = data.get("hostname")
    domain = data.get("domain")
    target = hostname if hostname else ip

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}AUTH FAILURE{W}\n{R}  └── {W}Target IP missing.")
        return data

    if not cred:
        print(f"\n{R}[!] {W}{BOLD}AUTH FAILURE{W}\n{R}  └── {W}No credential loaded.")
        return data

    # -------------------------
    # AUTH LOGIC & COMMAND
    # -------------------------
    cmd = ["netexec", "smb", target]
    env = os.environ.copy()
    
    user = cred.get("user")
    ctype = cred.get("type", "").lower()
    secret = cred.get("secret")
    ccache = cred.get("ccache")
    
    auth_label = "PASSWORD"

    # 1. Kerberos Logic
    if ctype in ["ticket", "ccache"] or ccache:
        auth_label = "KERBEROS"
        env["KRB5CCNAME"] = str(ccache if ccache else secret)
        cmd += ["-u", user, "-p", "''", "-k", "--use-kcache"]
    
    # 2. Hash Logic
    elif ctype in ["ntlm", "hash"]:
        auth_label = "NTLM HASH"
        cmd += ["-u", user, "-H", secret]
    
    # 3. Plaintext Logic
    else:
        cmd += ["-u", user, "-p", secret]

    if domain:
        cmd += ["-d", domain]

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: SMB AUTHENTICATION ({auth_label}){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")
    print(f"{B}  └── {B}User:{W}     {G}{user}{W}")
    
    if auth_label == "KERBEROS":
        print(f"{B}  └── {B}Ticket:{W}   {Y}{env.get('KRB5CCNAME')}{W}")

    print(f"\n{B}[{G}*{B}]{W} {BOLD}Executing:{W} {Y}{' '.join(cmd)}{W}\n")

    # -------------------------
    # EXECUTION
    # -------------------------
    try:
        # Straight execution, no capturing, no double-runs.
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Cancelled.")

    return data