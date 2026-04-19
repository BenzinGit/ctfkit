import subprocess

def run(data, cred, args):
    # 1. Handle shorthand / positional share name
    share = getattr(args, "share", None)
    if not share and getattr(args, "extra", []):
        share = args.extra[0]

    if not share:
        print("[!] Share name required")
        return

    ip = data.get("ip")

    # 2. Determine Authentication (Credentials or Anonymous)
    if cred:
        user = cred.get("user")
        password = cred.get("secret")
        # Standard Authenticated Command
        cmd = f"smbclient //{ip}/'{share}' -U {user}%{password}"
    else:
        # Anonymous/Guest Command
        # Using % for an empty password is the smbclient standard for guest access
        print("[*] No credentials provided, attempting anonymous/guest access...")
        cmd = f"smbclient //{ip}/'{share}' -N"

    print(f"[*] Connecting to {share} on {ip}...")
    print(f"[*] Running: {cmd}\n")

    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n[*] Connection closed.")