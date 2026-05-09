def run(data, cred, args):
    import subprocess
    import os
    from core.target import load_current_profile, save_profile

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    ip = data.get("ip")
    domain = data.get("domain")
    hostname = data.get("hostname")
    target_host = hostname if hostname else ip

    if not ip or not domain:
        print(f"\n{R}[!] {W}{BOLD}RECON FAILURE{W}\n{R}  └── {W}Missing IP or Domain in profile.")
        return None

    if not cred:
        print(f"\n{R}[!] {W}{BOLD}AUTH REQUIRED{W}\n{R}  └── {W}No active credential loaded.")
        return None

    username = cred.get("user")
    env = os.environ.copy()
    auth_type = "UNKNOWN"

    # -------------------------
    # AUTH HANDLING & COMMAND
    # -------------------------
    cmd = ["impacket-lookupsid"]
    
    # We use -target-ip to keep DNS happy during Kerberos
    cmd += ["-target-ip", ip]

    ctype = cred.get("type", "").lower()
    secret = cred.get("secret", "")
    ccache = cred.get("ccache") or (secret if str(secret).endswith(".ccache") else None)

    if ctype == "password":
        auth_type = f"PASSWORD ({username})"
        target_str = f"{domain}/{username}:{secret}@{target_host}"
        cmd.append(target_str)

    elif ctype in ["ntlm", "hash"]:
        auth_type = f"NTLM HASH ({username})"
        target_str = f"{domain}/{username}@{target_host}"
        cmd += [target_str, "-hashes", f":{secret}"]

    elif ctype in ["ticket", "ccache"] or ccache:
        auth_type = f"KERBEROS ({username})"
        env["KRB5CCNAME"] = str(ccache)
        target_str = f"{domain}/{username}@{target_host}"
        cmd += [target_str, "-k", "-no-pass"]
    else:
        print(f"{R}  └── {W}Unsupported credential type: {ctype}")
        return None

    # --- UI OUTPUT ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}PHASE: SID ENUMERATION{W}")
    print(f"{B}  ├── {B}Target:{W}   {C}{target_host}{W} ({ip})")
    print(f"{B}  └── {B}Auth:{W}     {G}{auth_type}{W}")
    
    if "KERBEROS" in auth_type:
        print(f"{B}  └── {B}Ticket:{W}   {Y}{env.get('KRB5CCNAME')}{W}")

    print(f"\n{B}[{G}*{B}]{W} {BOLD}Executing:{W} {Y}{' '.join(cmd)}{W}\n")

    # -------------------------
    # EXECUTION & PARSING
    # -------------------------
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        output = result.stdout + result.stderr
    except Exception as e:
        print(f"{R}[!] {W}Execution failed: {e}")
        return None

    domain_sid = None
    # Primary Parser
    for line in output.splitlines():
        if "Domain SID is:" in line:
            domain_sid = line.split("Domain SID is:")[-1].strip()
            break
    
    # Fallback Parser
    if not domain_sid:
        for line in output.splitlines():
            if "S-1-5-21-" in line:
                sid_parts = line.split()[0].split("-")
                if len(sid_parts) > 4:
                    domain_sid = "-".join(sid_parts[:-1])
                    break

    if not domain_sid:
        print(f"{R}[!] {W}Failed to extract Domain SID from output.")
        if "Access Denied" in output:
            print(f"{R}  └── {W}Status: Access Denied (Check your privileges)")
        return None

    # -------------------------
    # SAVE & HUD
    # -------------------------
    data["domain_sid"] = domain_sid
    _, path = load_current_profile()
    save_profile(data, path)

    print(f"{G}┌── EXTRACTION COMPLETE ───────────────────────────────────┐{W}")
    print(f"{G}│{W}  {B}Object:{W}   {C}DOMAIN SID{W}                                {G}│{W}")
    print(f"{G}│{W}  {B}Value:{W}    {G}{domain_sid:<42}{W} {G}│{W}")
    print(f"{G}│{W}  {B}Status:{W}   {G}SAVED TO PROFILE{W}                           {G}│{W}")
    print(f"{G}└──────────────────────────────────────────────────────────┘{W}\n")

    return {"domain_sid": domain_sid}