import subprocess


def run(data, cred, args):
    """
    Find vulnerable ADCS templates using certipy

    Usage:
        ctf ad.certfind
    """

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")
    domain = data.get("domain")

    if not ip:
        print("[-] Target missing IP")
        return data

    if not domain:
        print("[-] No domain set")
        return data

    # -------------------------
    # Validate credential
    # -------------------------
    if not cred:
        print("[-] No active credential")
        return data

    username = cred.get("user")
    password = cred.get("secret") if cred.get("type") == "password" else None

    if not username or not password:
        print("[-] Need password-based credential")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy",
        "find",
        "-u", f"{username}@{domain}",
        "-p", password,
        "-dc-ip", ip,
        "-vulnerable",
    ]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute (preserve color)
    # -------------------------
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    return data