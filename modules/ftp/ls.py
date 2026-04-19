import subprocess


def run(data, cred, args):
    """
    List files on FTP server

    Usage:
        ctf ftp.ls
        ctf ftp.ls anonymous
        ctf ftp.ls user pass
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    username = None
    password = None

    extra = getattr(args, "extra", []) or []

    if len(extra) >= 1:
        username = extra[0]

    if len(extra) >= 2:
        password = extra[1]

    # -------------------------
    # Fallback to creds
    # -------------------------
    if not username and cred:
        username = cred.get("user")

        if cred.get("type") == "password":
            password = cred.get("secret")

    # -------------------------
    # Defaults
    # -------------------------
    if not username:
        username = "anonymous"
        password = "anonymous"

    if not password:
        password = "anonymous"

    ip = data.get("ip")

    if not ip:
        print("[-] Target missing IP")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "ftp",
        "-inv",
        ip
    ]

    ftp_commands = f"""
user {username} {password}
ls
quit
"""

    print(f"[*] Running: ftp -inv {ip}")
    print(f"[*] Login: {username}:{password}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        result = subprocess.run(
            cmd,
            input=ftp_commands,
            text=True,
            capture_output=True
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    output = result.stdout + result.stderr

    print(output)

    return data