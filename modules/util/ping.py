def run(data, cred, args):
    ip = data.get("ip")

    cmd = f"ping -c 3 {ip}"

    print(f"[*] Running: {cmd}\n")

    import subprocess
    subprocess.run(cmd, shell=True)