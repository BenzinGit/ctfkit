def run(data, cred, args):
    ip = data.get("ip")

    if cred:
        cmd = f"smbclient -L //{ip} -U {cred['user']}%{cred['pass']}"
    else:
        cmd = f"smbclient -L //{ip} -N"

    print(f"[*] Running: {cmd}\n")

    import subprocess
    subprocess.run(cmd, shell=True)
