import subprocess

def run(data, cred, args):
    ip = data.get("ip")

    if not ip:
        print("[!] Target IP required")
        return

    # 1. Determine authentication
    if cred:
        user = cred.get("user")
        password = cred.get("secret")

        if not user or not password:
            print("[!] Invalid credentials")
            return

        target = f"{user}:{password}@{ip}"
    else:
        print("[*] No credentials provided, attempting anonymous/guest access...")
        target = ip  # impacket allows some fallback behavior

    # 2. Optional flags (keep minimal for now)
    extra = ""
    if getattr(args, "windows_auth", False):
        extra += " -windows-auth"

    # 3. Build command
    cmd = f"impacket-mssqlclient {target}{extra}"

    print(f"[*] Connecting to MSSQL on {ip}...")
    print(f"[*] Running: {cmd}\n")

    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n[*] Connection closed.")