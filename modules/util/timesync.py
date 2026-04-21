import subprocess


def run(data, cred, args):
    """
    Sync local time with target (NTP)

    Usage:
        ctf util.timesync
        ctf util.timesync 10.10.10.10
    """

    # -------------------------
    # Parse arguments
    # -------------------------
    extra = getattr(args, "extra", []) or []

    ip = None

    if len(extra) >= 1:
        ip = extra[0]
    else:
        ip = data.get("ip")

    if not ip:
        print("[-] No target IP provided")
        return data

    # -------------------------
    # Build command
    # -------------------------
    cmd = ["sudo", "ntpdate", ip]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute (preserve output)
    # -------------------------
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    return data