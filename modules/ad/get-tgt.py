import subprocess
from pathlib import Path


def run(data, cred, args):
    """
    Get TGT using password

    Usage:
        ctf ad.gettgt
        ctf ad.gettgt user
        ctf ad.gettgt user password
    """

    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Defaults
    # -------------------------
    domain = data.get("domain")

    if not domain:
        print("[-] Missing domain")
        return data

    # -------------------------
    # Active credential
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
    # Overrides (optional)
    # -------------------------
    if len(extra) >= 1:
        username = extra[0]

    if len(extra) >= 2:
        password = extra[1]

    # -------------------------
    # Build command
    # -------------------------
    target = f"{domain}/{username}:{password}"

    cmd = [
        "impacket-getTGT",
        target
    ]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # Find generated ccache
    # -------------------------
    ccache_files = list(Path(".").glob("*.ccache"))

    if not ccache_files:
        print("[-] No ticket generated")
        return data

    # pick most recent file
    latest = max(ccache_files, key=lambda f: f.stat().st_mtime)

    print(f"[+] Got TGT: {latest.name}")

    return [{
        "user": username,
        "type": "ticket",
        "ccache": str(latest)
    }]