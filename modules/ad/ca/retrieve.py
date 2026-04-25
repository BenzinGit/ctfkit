import subprocess
import os
from pathlib import Path


def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Input
    # -------------------------
    if len(extra) < 1:
        print("[-] Missing request ID")
        return {"success": False}

    request_id = str(extra[0])

    domain = data.get("domain")
    dc_ip = data.get("ip")
    ca = data.get("adcs", {}).get("ca")

    if not domain or not dc_ip or not ca:
        print("[-] Missing domain, DC IP, or CA")
        return {"success": False}

    username = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not username:
        print("[-] Missing username")
        return {"success": False}

    # optional output dir
    out_dir = None
    if "--out" in extra:
        idx = extra.index("--out")
        if idx + 1 < len(extra):
            out_dir = Path(extra[idx + 1]).expanduser().resolve()

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy-ad", "req",
        "-retrieve", request_id,
        "-ca", ca,
        "-dc-ip", dc_ip,
        "-username", f"{username}@{domain}"
    ]

    env = os.environ.copy()

    # -------------------------
    # Auth handling
    # -------------------------
    if typ == "password":
        cmd += ["-password", secret]

    elif typ == "ntlm":
        ntlm = secret if ":" in secret else f":{secret}"
        cmd += ["-hashes", ntlm]

    elif typ == "ticket":
        env["KRB5CCNAME"] = secret
        cmd += ["-k", "-no-pass"]

    else:
        print("[-] Unsupported credential type")
        return {"success": False}

    cmd += ["-debug"]
    cmd = [str(x) for x in cmd]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # Execute
    # -------------------------
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=out_dir
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return {"success": False}

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # Detect PFX
    # -------------------------
    pfx_path = None

    for line in output.splitlines():
        if ".pfx" in line.lower() and ("saved" in line.lower() or "written" in line.lower()):
            # try to extract filename
            parts = line.split("'")
            if len(parts) >= 2:
                pfx_path = parts[1]
                break

    # fallback: look in cwd
    if not pfx_path:
        for f in Path(out_dir or ".").glob("*.pfx"):
            pfx_path = str(f)

    success = pfx_path is not None

    if success:
        print(f"[+] Retrieved certificate: {pfx_path}")
    else:
        print("[-] Failed to retrieve certificate")

    return {
        "success": success,
        "pfx": pfx_path,
        "request_id": request_id,
        "output": output
    }