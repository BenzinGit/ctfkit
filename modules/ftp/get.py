import subprocess
from pathlib import Path


def run(data, cred, args):
    """
    Download files from FTP server

    Usage:
        ctf ftp.get file.txt
        ctf ftp.get --all
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    filename = None
    download_all = getattr(args, "all", False)

    if not download_all and len(extra) >= 1:
        filename = extra[0]

    if not filename and not download_all:
        print("[-] Specify a file or use --all")
        return data

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")

    if not ip:
        print("[-] Target missing IP")
        return data

    # -------------------------
    # Resolve credentials
    # -------------------------
    username = None
    password = None

    if cred:
        username = cred.get("user")

        if cred.get("type") == "password":
            password = cred.get("secret")

    if not username:
        username = "anonymous"
        password = "anonymous"

    if not password:
        password = "anonymous"

    # -------------------------
    # Output directory
    # -------------------------
    out_dir = getattr(args, "out", None)

    if out_dir:
        out_path = Path(out_dir).expanduser()
        out_path.mkdir(parents=True, exist_ok=True)
    else:
        out_path = Path.cwd()

    # -------------------------
    # Build FTP commands
    # -------------------------
    if download_all:
        ftp_commands = f"""
prompt off
user {username} {password}
mget *
quit
"""
        print(f"[*] Running: ftp -inv {ip} (download all)")

    else:
        ftp_commands = f"""
user {username} {password}
get {filename}
quit
"""
        print(f"[*] Running: ftp -inv {ip} (get {filename})")

    print(f"[*] Login: {username}:{password}")
    print(f"[*] Output: {out_path}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        result = subprocess.run(
            ["ftp", "-inv", ip],
            input=ftp_commands,
            text=True,
            capture_output=True,
            cwd=out_path
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    output = result.stdout + result.stderr

    print(output)

    return data