def run(data, cred, args):
    import subprocess
    import os
    from core.target import load_current_profile

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    ip = data.get("ip")
    domain = data.get("domain")
    hostname = data.get("hostname")
    
    # For Kerberos, NetExec prefers the Hostname/FQDN to match the ticket SPN
    target = hostname if hostname else ip

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}ENUMERATION ABORTED{W}\n{R}  └── {W}Target IP is not set.")
        return

    # Base command: --shares lists everything and tests access
    cmd_parts = ["netexec", "smb", target, "--shares"]
    env = os.environ.copy()
    auth_type = "ANONYMOUS"

    if cred:
        user = cred.get("user")
        ctype = cred.get("type", "").lower()
        secret_val = cred.get("secret", "")
        ticket_path = cred.get("ccache") or (secret_val if secret_val.endswith(".ccache") else None)

        # ---------------- KERBEROS LOGIC (The NXC Way) ----------------
        if ctype in ["ccache", "ticket"] or ticket_path:
            auth_type = f"KERBEROS ({user})"
            env["KRB5CCNAME"] = str(ticket_path)
            # -k uses Kerberos, --use-kcache tells NXC to look at KRB5CCNAME
            cmd_parts += ["-u", user, "-p", "''", "-k", "--use-kcache"]
        
        # ---------------- HASH LOGIC ----------------
        elif ctype == "hash":
            auth_type = f"NTLM HASH ({user})"
            cmd_parts += ["-u", user, "-H", secret_val]
        
        # ---------------- PASSWORD LOGIC ----------------
        else:
            auth_type = f"PASSWORD ({user})"
            cmd_parts += ["-u", user, "-p", secret_val]
    else:
        # Null Session
        cmd = f"smbclient -L //{ip} -N"

         # --- UI OUTPUT ---
        print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}SMB SHARE ENUMERATION SMBCLIENT NULL SESSION{W}")
        print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")
        print(f"{B}  └── {B}Auth:{W}     {G}{auth_type}{W}")
        print(f"\n{W}[*] Executing:{Y} {cmd}\n{W}")

        try:
            # NetExec output is already beautiful, so we just let it rip
            subprocess.run(cmd, shell=True, env=env)
            return
        except KeyboardInterrupt:
            print(f"\n{R}[!] {W}Cancelled by operator.")
            return

    # Add domain if we have it
    if domain:
        cmd_parts += ["-d", domain]


    cmd = " ".join(cmd_parts)

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: SMB SHARE ENUMERATION (NETEXEC){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target}{W}")
    print(f"{B}  └── {B}Auth:{W}     {G}{auth_type}{W}")
    
    if "KERBEROS" in auth_type:
        print(f"{B}  └── {B}Ticket:{W}   {Y}{env.get('KRB5CCNAME')}{W}")
    print(f"\n{W}[*] Executing:{Y} {cmd}\n{W}")

    # --- EXECUTION ---
    try:
        # NetExec output is already beautiful, so we just let it rip
        subprocess.run(cmd, shell=True, env=env)
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Cancelled by operator.")