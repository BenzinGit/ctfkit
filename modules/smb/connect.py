def run(data, cred, args):
    import subprocess
    import os
    from core.target import load_current_profile

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    # 1. Handle share name (Impacket prompts for share after connecting, 
    # but we can also handle it via the mini-shell if needed)
    share = getattr(args, "share", None)
    if not share and getattr(args, "extra", []):
        share = args.extra[0]

    ip = data.get("ip")
    hostname = data.get("hostname")
    domain = data.get("domain", "")
    
    # Kerberos REQUIRES the hostname/FQDN to find the ticket in the cache
    target_name = hostname if hostname else ip

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}CONNECTION ABORTED{W}\n{R}  └── {W}Target IP is missing.")
        return

    # ---------------- IMPACKET COMMAND BUILDER ----------------
    env = os.environ.copy()
    cmd_parts = ["impacket-smbclient"]
    auth_type = "ANONYMOUS"
    
    # We use -target-ip to force the connection to the IP while keeping the 
    # Name in the 'target' string for Kerberos SPN matching.
    cmd_parts += ["-target-ip", ip]

    if cred:
        user = cred.get("user", "")
        ctype = cred.get("type", "").lower()
        secret_val = cred.get("secret", "")
        ticket_path = cred.get("ccache") or (secret_val if str(secret_val).endswith(".ccache") else None)

        # ---- KERBEROS ----
        if ctype in ["ccache", "ticket"] or ticket_path:
            auth_type = f"KERBEROS ({user})"
            env["KRB5CCNAME"] = str(ticket_path)
            cmd_parts += ["-k", "-no-pass"]
            # Target format: domain/user@target
            target_str = f"{domain}/{user}@{target_name}"
        
        # ---- HASH ----
        elif ctype == "hash":
            auth_type = f"NTLM HASH ({user})"
            cmd_parts += ["-hashes", secret_val]
            target_str = f"{domain}/{user}@{ip}"
        
        # ---- PASSWORD ----
        else:
            auth_type = f"PASSWORD ({user})"
            target_str = f"{domain}/{user}:{secret_val}@{ip}"
    else:
        # Anonymous
        target_str = f"@{ip}"
        cmd_parts += ["-no-pass"]

    cmd_parts.append(target_str)
    cmd = " ".join(cmd_parts)

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: SMB INTERACTIVE (IMPACKET){W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target_name}{W} ({ip})")
    print(f"{B}  └── {B}Auth:{W}     {G}{auth_type}{W}")
    
    if "KERBEROS" in auth_type:
        print(f"{B}  └── {B}Ticket:{W}   {Y}{env.get('KRB5CCNAME')}{W}")
        if domain:
            cmd_parts += ["-dc-ip", domain] # Help Impacket find the KDC

    print(f"\n{B}[{G}*{B}]{W} {BOLD}Executing:{W} {Y}{cmd}{W}\n")

    # --- EXECUTION ---
    try:
        # Use the environment dictionary to ensure KRB5CCNAME is passed
        subprocess.run(cmd, shell=True, env=env)
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Session closed.")