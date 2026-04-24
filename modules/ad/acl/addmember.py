def run(data, cred, args):
    import subprocess

    if not args.extra:
        print("Usage: ad.group.addmember <group> [user]")
        return {"success": False}

    group = args.extra[0]
    user = args.extra[1] if len(args.extra) > 1 else cred["user"]

    cmd = [
        "bloodyAD",
        "-d", data["domain"],
        "--host", data["ip"],
        "-u", cred["user"],
        "-p", cred["secret"],
        "add", "groupMember",
        group,
        user
    ]

    print("[*] " + " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("[+] " + user + " added to " + group)
        return {"success": True, "group": group, "user": user}

    print(result.stdout + result.stderr)
    return {"success": False}