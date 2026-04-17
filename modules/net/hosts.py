PROVIDES = ["domain"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import json
    from core.target import load_current_profile, save_profile
    from core.paths import get_domains_dir

    quiet = getattr(args, "quiet", False)

    ip = data.get("ip")

    if not ip:
        print("[!] No target IP set")
        return

    output = getattr(args, "out", None) or "hosts.txt"
    output_file = Path(output).expanduser().resolve()

    # ---------------- RUN NXC ----------------
    cmd = f"nxc smb {ip} --generate-hosts-file {output_file}"

    if not quiet:
        print(f"[*] Running: {cmd}\n")

    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None
    )

    if not output_file.exists():
        print("[!] Failed to generate hosts file")
        return

    print(f"[+] Hosts file generated → {output_file}")

    content = output_file.read_text().strip()

    if not content:
        print("[!] Hosts file is empty")
        return

    # ---------------- UPDATE /etc/hosts (SAFE WAY) ----------------
    try:
        hosts_path = Path("/etc/hosts")
        existing = hosts_path.read_text()

        new_lines = []
        for line in content.splitlines():
            if line not in existing:
                new_lines.append(line)

        if new_lines:
            temp_file = Path("/tmp/ctf_hosts_append.txt")
            temp_file.write_text("\n".join(new_lines) + "\n")

            subprocess.run(
                f"sudo sh -c 'cat {temp_file} >> /etc/hosts'",
                shell=True
            )

            print(f"[+] Added {len(new_lines)} new entries to /etc/hosts")

        else:
            print("[*] All entries already exist in /etc/hosts")

    except Exception as e:
        print("[!] Failed to update /etc/hosts")
        print(f"[!] {e}")
        print("[*] Run manually:")
        print(f"sudo sh -c 'cat {output_file} >> /etc/hosts'")

    # ---------------- EXTRACT DOMAIN + HOSTNAME ----------------
    domain = None
    hostname = None

    for line in content.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        names = parts[1:]

        for name in names:
            if "." in name:
                domain = name.lower()  
            else:
                hostname = name.lower()

        if domain:
            break

    if not domain:
        print("[!] Could not extract domain")
        return

    print(f"[+] Detected domain → {domain}")

    if hostname:
        print(f"[+] Detected hostname → {hostname}")

    # ---------------- UPDATE TARGET PROFILE ----------------
    data, path = load_current_profile()

    data["domain"] = domain

    if hostname:
        data["hostname"] = hostname

    save_profile(data, path)

    print("[+] Updated target profile")

    # ---------------- REGISTER DOMAIN ----------------
    domains_dir = get_domains_dir()
    domains_dir.mkdir(parents=True, exist_ok=True)

    domain_file = domains_dir / f"{domain}.json"

    if not domain_file.exists():
        domain_data = {
            "name": domain,
            "dc": None,
            "creds": [],
            "notes": []
        }

        domain_file.write_text(json.dumps(domain_data, indent=2))

        print(f"[+] Created domain → {domain}")

    else:
        print(f"[*] Domain already exists → {domain}")