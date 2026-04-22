def run(data, cred, args):
    import subprocess

    # ---------------- DEFAULTS ----------------
    lport_raw = getattr(args, "lport", None)
    lport = int(lport_raw) if lport_raw is not None else 4444

    method = getattr(args, "method", None) or "nc"

    # ---------------- COMMAND ----------------
    if method == "ncat":
        cmd = ["ncat", "-lvnp", str(lport)]

    elif method == "nc":
        cmd = ["nc", "-lvnp", str(lport)]

    elif method == "rlwrap":
        cmd = ["rlwrap", "nc", "-lvnp", str(lport)]

    elif method == "socat":
        cmd = [
            "socat",
            f"TCP-LISTEN:{lport},reuseaddr,fork",
            "FILE:`tty`,raw,echo=0"
        ]

    else:
        print(f"[!] Unknown method: {method}")
        return

    # ---------------- OUTPUT ----------------
    print(f"[+] Listening on port {lport} ({method})")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[!] Listener stopped")

    return [{
        "type": "listener",
        "data": {
            "port": lport,
            "method": method
        }
    }]