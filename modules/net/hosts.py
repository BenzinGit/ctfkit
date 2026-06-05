PROVIDES = ["domain"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    import json
    from pathlib import Path

    from core.target import load_current_profile, save_profile
    from core.paths import get_domains_dir

    # ---------------- ANSI ----------------
    G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m'
    )
    BOLD = '\033[1m'

    quiet = getattr(args, "quiet", False)

    ip = data.get("ip")
    if not ip:
        print(f"\n{R}[!] {W}{BOLD}RECONNAISSANCE ABORTED{W}")
        print(f"{R}  └── {W}Target IP is not set.")
        return

    output = getattr(args, "out", None) or "hosts.txt"
    output_file = Path(output).expanduser().resolve()

    # ---------------- CLEAN OLD FILE ----------------

    if output_file.exists():
        output_file.unlink()

    # ---------------- STEP 1 ----------------

    cmd = f"nxc smb {ip} --generate-hosts-file {output_file}"

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 1: NETWORK ENUMERATION{W}")

    if not quiet:
        print(f"{B}  └── Running: {Y}{cmd}{W}")

    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None
    )

    if not output_file.exists():
        print(f"{R}  └── {W}NetExec failed to generate hosts file")
        return

    content = output_file.read_text().strip()

    if not content:
        print(f"{R}  └── {W}Generated hosts file is empty")
        return

    # ---------------- STEP 2 ----------------

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 2: SYSTEM RESOLUTION{W}")

    try:
        hosts_path = Path("/etc/hosts")
        existing_lines = set(
            line.strip()
            for line in hosts_path.read_text().splitlines()
            if line.strip()
        )

        new_lines = []

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line not in existing_lines:
                new_lines.append(line)

        if new_lines:
            temp_file = Path("/tmp/ctf_hosts_append.txt")
            temp_file.write_text("\n".join(new_lines) + "\n")

            subprocess.run(
                f"sudo sh -c 'cat {temp_file} >> /etc/hosts'",
                shell=True
            )

            print(
                f"{G}  [+]{W} Injected "
                f"{C}{len(new_lines)}{W} entries into "
                f"{C}/etc/hosts{W}"
            )
        else:
            print(f"{B}  [*]{W} Hosts file already synchronized")

    except Exception:
        print(f"{Y}  [!]{W} Unable to update /etc/hosts automatically")

    # ---------------- STEP 3 ----------------

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}STEP 3: IDENTITY EXTRACTION{W}")

    hostname = None
    domain = None
    fqdn = None

    matched_line = None

    for line in content.splitlines():
        parts = line.split()

        if len(parts) < 2:
            continue

        line_ip = parts[0]

        if line_ip != ip:
            continue

        matched_line = line

        names = parts[1:]

        fqdn = next(
            (
                n
                for n in names
                if "." in n and n.upper() != n
            ),
            None
        )

        if not fqdn:
            fqdn = next(
                (n for n in names if "." in n),
                None
            )

        if fqdn:
            fqdn = fqdn.lower()

            hostname = fqdn.split(".", 1)[0]

            if "." in fqdn:
                domain = fqdn.split(".", 1)[1]

        break

    if not matched_line:
        print(f"{R}  └── {W}Could not locate target IP in hosts file")
        return

    if not domain:
        print(f"{R}  └── {W}Could not determine domain")
        print(f"{Y}      Matched:{W} {matched_line}")
        return

    # ---------------- PROFILE UPDATE ----------------

    data, path = load_current_profile()

    data["domain"] = domain

    if hostname:
        data["hostname"] = hostname.upper()

    save_profile(data, path)

    # ---------------- DOMAIN REGISTRATION ----------------

    domains_dir = get_domains_dir()
    domains_dir.mkdir(parents=True, exist_ok=True)

    domain_file = domains_dir / f"{domain}.json"

    if not domain_file.exists():
        domain_file.write_text(
            json.dumps(
                {
                    "name": domain,
                    "dc": None,
                    "creds": [],
                    "notes": []
                },
                indent=2
            )
        )

    # ---------------- HUD ----------------

    print(f"\n{G}┌── DOMAIN DISCOVERY COMPLETE ─────────────────────────────┐{W}")
    print(
        f"{G}│{W}  {B}Domain:{W}   "
        f"{C}{domain:<28}{W}"
        f"{B}Status:{W} {G}RESOLVED{W} {G}│{W}"
    )
    print(
        f"{G}│{W}  {B}Hostname:{W} "
        f"{C}{(hostname or 'N/A'):<28}{W}"
        f"{B}DB:{W} {G}UPDATED{W} {G}│{W}"
    )
    print(f"{G}└──────────────────────────────────────────────────────────┘{W}\n")