def run(data, cred, args):
    if not args.share:
        print("[!] --share required")
        return

    ip = data.get("ip")

    cmd = f"smbclient //{ip}/{args.share} -U {cred['user']}%{cred['pass']}"

    print(f"[*] Running: {cmd}\n")

    import subprocess
    subprocess.run(cmd, shell=True)