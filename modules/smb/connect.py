def run(data, cred, args):
    import subprocess
    import os
    from core.target import load_current_profile

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    # --- SHARE HANDLING ---
    share = getattr(args, "share", None)
    if not share and getattr(args, "extra", []):
        share = args.extra[0]

    # --- TARGET INFO ---
    ip = data.get("ip")
    hostname = data.get("hostname")
    domain = data.get("domain", "")

    target_name = hostname if hostname else ip

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}CONNECTION ABORTED{W}\n{R}  └── {W}Target IP is missing.")
        return

    # --- ENV SETUP ---
    env = os.environ.copy()
    auth_type = "ANONYMOUS"

    # =========================================================
    # =============== AUTHENTICATED (IMPACKET) =================
    # =========================================================
    if cred:
        cmd_parts = ["impacket-smbclient", "-target-ip", ip]

        user = cred.get("user", "")
        ctype = cred.get("type", "").lower()
        secret_val = cred.get("secret", "")
        ticket_path = cred.get("ccache") or (
            secret_val if str(secret_val).endswith(".ccache") else None
        )

        # ---- KERBEROS ----
        if ctype in ["ccache", "ticket"] or ticket_path:
            auth_type = f"KERBEROS ({user})"
            env["KRB5CCNAME"] = str(ticket_path)
            cmd_parts += ["-k", "-no-pass"]
            target_str = f"{domain}/{user}@{target_name}"

            if domain:
                cmd_parts += ["-dc-ip", domain]

        # ---- HASH ----
        elif ctype == "hash":
            auth_type = f"NTLM HASH ({user})"
            cmd_parts += ["-hashes", secret_val]
            target_str = f"{domain}/{user}@{ip}"

        # ---- PASSWORD ----
        else:
            auth_type = f"PASSWORD ({user})"
            target_str = f"{domain}/{user}:{secret_val}@{ip}"

        cmd_parts.append(target_str)
        cmd = " ".join(cmd_parts)

        phase_label = "SMB INTERACTIVE (IMPACKET)"

    # =========================================================
    # ================== ANONYMOUS (SMBCLIENT) =================
    # =========================================================
    else:
        auth_type = "ANONYMOUS (smbclient)"

        if share:
            cmd = f"smbclient -N //{ip}/{share}"
        else:
            cmd = f"smbclient -N -L //{ip}"

        phase_label = "SMB INTERACTIVE (SMBCLIENT)"

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: {phase_label}{W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target_name}{W} ({ip})")
    print(f"{B}  └── {B}Auth:{W}     {G}{auth_type}{W}")

    if "KERBEROS" in auth_type:
        print(f"{B}  └── {B}Ticket:{W}   {Y}{env.get('KRB5CCNAME')}{W}")

    print(f"\n{B}[{G}*{B}]{W} {BOLD}Executing:{W} {Y}{cmd}{W}\n")

    # --- EXECUTION ---
    try:
        subprocess.run(cmd, shell=True, env=env)
    except KeyboardInterrupt:
        print(f"\n{R}[!] {W}Session closed.")