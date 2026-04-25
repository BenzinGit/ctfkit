import subprocess
import os


def run(data, cred, args):
    domain = data.get("domain")
    dc_ip = data.get("ip")
    ca = data.get("adcs", {}).get("ca")

    if not domain or not dc_ip or not ca:
        print("[-] Missing domain, DC IP, or CA")
        return None

    username = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not username:
        print("[-] Missing username")
        return None

    # -------------------------
    # Build command
    # -------------------------
    cmd = [
        "certipy-ad", "ca",
        "-ca", ca,
        "-dc-ip", dc_ip,
        "-list-templates",
        "-u", f"{username}@{domain}"
    ]

    env = os.environ.copy()

    # -------------------------
    # Auth
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
        return None

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
        return None

    output = result.stdout + result.stderr
    print(output)

    # -------------------------
    # Parse templates
    # -------------------------
    templates = []

    for line in output.splitlines():
        # crude but works: template names are usually standalone words
        if "Template Name" in line:
            name = line.split(":")[-1].strip()
            templates.append(name)

    return {
        "success": True,
        "templates": templates,
        "raw": output
    }