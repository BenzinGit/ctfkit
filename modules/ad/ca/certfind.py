import subprocess
from pathlib import Path
import os


def run(data, cred, args):
    """
    Find vulnerable ADCS templates using certipy

    Supports:
        - password auth
        - kerberos auth (-k -no-pass)
        - NTLM hash auth (-hashes :NT)

    Usage:
        ctf ad.certfind
        ctf ad.certfind --artifacts-dir <path>
    """

    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Parse args
    # -------------------------
    artifacts_dir = None

    for i in range(len(extra)):
        if extra[i] == "--artifacts-dir" and i + 1 < len(extra):
            artifacts_dir = extra[i + 1]

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")
    domain = data.get("domain")
    hostname = data.get("hostname") or data.get("name")

    if not ip:
        print("[-] Target missing IP")
        return data

    if not domain:
        print("[-] No domain set")
        return data

    if not cred:
        print("[-] No active credential")
        return data

    username = cred.get("user")

    if not username:
        print("[-] Missing username")
        return data

    # -------------------------
    # Prepare cwd
    # -------------------------
    cwd = None
    if artifacts_dir:
        cwd = Path(artifacts_dir)
        cwd.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Build base command
    # -------------------------
    cmd = [
        "certipy",
        "find",
        "-u", f"{username}@{domain}",
        "-vulnerable",
        "-json",
        "-stdout"
    ]

    # -------------------------
    # Auth mode
    # -------------------------

    # ---- PASSWORD ----
    if cred.get("type") == "password":
        password = cred.get("secret")

        if not password:
            print("[-] Missing password")
            return data

        cmd += ["-p", password, "-dc-ip", ip]

    # ---- NTLM HASH ----
    elif cred.get("type") == "ntlm":
        ntlm = cred.get("secret")

        if not ntlm:
            print("[-] Missing NTLM hash")
            return data

        cmd += [
            "-hashes", f":{ntlm}",
            "-dc-ip", ip
        ]

        print("[*] Using NTLM hash authentication")

    # ---- KERBEROS ----
    elif cred.get("type") == "ticket" or cred.get("ccache"):
        ccache = cred.get("ccache") or os.environ.get("KRB5CCNAME")

        if not ccache:
            print("[-] No ccache found for Kerberos")
            return data

        os.environ["KRB5CCNAME"] = ccache

        if not hostname:
            print("[-] Missing hostname (needed for Kerberos)")
            return data

        cmd += [
            "-k",
            "-no-pass",
            "-target", f"{hostname}.{domain}",
            "-dc-ip", ip
        ]

        print("[*] Using Kerberos authentication")

    else:
        print("[-] Unsupported credential type")
        return data

    # -------------------------
    # Execute
    # -------------------------
    print(f"[*] Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, cwd=cwd)
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    return data