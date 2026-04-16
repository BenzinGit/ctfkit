def run(data, cred, args):
    import subprocess

    ip = data.get("ip")

    cmd = f"nxc smb {ip} --generate-hosts-file hosts.txt"

    print(f"[*] Running: {cmd}\n")
    subprocess.run(cmd, shell=True)

    # parse hosts.txt
    try:
        with open("hosts.txt", "r") as f:
            line = f.readline().strip()
    except FileNotFoundError:
        print("[!] hosts.txt not found")
        return

    if not line:
        print("[!] hosts.txt is empty")
        return

    parts = line.split()

    if len(parts) < 3:
        print("[!] Unexpected hosts.txt format")
        return

    ip = parts[0]
    dc = parts[1]
    domain = parts[2]

    print(f"[+] Found domain: {domain}")
    print(f"[+] Found DC: {dc}")

    # update profile
    data["domain"] = domain
    data["dc"] = dc

    entry = f"{ip} {dc} {domain}"

    print(f"\n[*] Adding to /etc/hosts: {entry}")

    # check if entry already exists (avoid duplicates)
    try:
        with open("/etc/hosts", "r") as f:
            if entry in f.read():
                print("[*] Entry already exists in /etc/hosts")
                return data
    except:
        print("[!] Could not read /etc/hosts")
        return data

    # write to /etc/hosts
    write_cmd = f'echo "{entry}" | sudo tee -a /etc/hosts'

    print(f"[*] Running: {write_cmd}\n")
    subprocess.run(write_cmd, shell=True)

    return data
