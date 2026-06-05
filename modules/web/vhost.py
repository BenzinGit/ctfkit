PROVIDES = []
REQUIRES = ["domain"]


def run(data, cred, args):
    import json
    import subprocess
    from pathlib import Path

    # --- ANSI ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    domain = data.get("domain")
    ip = data.get("ip")

    if not domain:
        print(f"\n{R}[!] {W}{BOLD}NO DOMAIN CONFIGURED{W}")
        return

    if not ip:
        print(f"\n{R}[!] {W}{BOLD}NO TARGET IP CONFIGURED{W}")
        return

    wordlist = (
        "/usr/share/seclists/"
        "Discovery/DNS/"
        "subdomains-top1million-5000.txt"
    )

    loot_dir = Path("loot/web")
    loot_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_json = loot_dir / "vhosts.json"
    output_txt = loot_dir / "vhosts.txt"

    cmd = [
        "ffuf",
        "-u", f"http://{ip}",
        "-H", f"Host: FUZZ.{domain}",
        "-w", wordlist,
        "-ac",
        "-of", "json",
        "-o", str(output_json)
    ]

    # ---------------- RUN FFUF ----------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}VHOST ENUMERATION{W}"
    )

    print(
        f"{B}  └── {W}"
        f"Target: {Y}{ip}{W}"
    )

    print(
        f"{B}  └── {W}"
        f"Domain: {Y}{domain}{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}COMMAND{W}\n"
    )

    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(
            f"\n{R}[!] FFUF FAILED{W}"
        )
        return

    if not output_json.exists():
        print(
            f"\n{R}[!] NO OUTPUT GENERATED{W}"
        )
        return

    # ---------------- PARSE RESULTS ----------------

    data_json = json.loads(
        output_json.read_text()
    )

    results = data_json.get(
        "results",
        []
    )

    if not results:
        print(
            f"\n{Y}[!] No VHosts discovered{W}"
        )
        return

    discovered = []

    for result in results:

        host = (
            result
            .get("input", {})
            .get("FUZZ")
        )

        if not host:
            continue

        fqdn = f"{host}.{domain}"

        discovered.append(
            (
                host,
                fqdn
            )
        )

    discovered = sorted(
        set(discovered)
    )

    output_txt.write_text(
        "\n".join(
            fqdn
            for _, fqdn in discovered
        ) + "\n"
    )

    # ---------------- UPDATE HOSTS ----------------

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}UPDATING /etc/hosts{W}"
    )

    try:

        hosts_path = Path(
            "/etc/hosts"
        )

        existing = (
            hosts_path
            .read_text()
        )

        new_entries = []

        for host, fqdn in discovered:

            entry = (
                f"{ip} "
                f"{fqdn} "
                f"{host}"
            )

            if entry not in existing:
                new_entries.append(
                    entry
                )

        if new_entries:

            temp = Path(
                "/tmp/ctf_vhosts.txt"
            )

            temp.write_text(
                "\n".join(
                    new_entries
                ) + "\n"
            )

            subprocess.run(
                f"sudo sh -c 'cat {temp} >> /etc/hosts'",
                shell=True
            )

            print(
                f"{G}[+]{W} Added "
                f"{Y}{len(new_entries)}{W} "
                f"entries"
            )

        else:

            print(
                f"{B}[*]{W} "
                f"/etc/hosts already synchronized"
            )

    except Exception as e:

        print(
            f"{Y}[!]{W} "
            f"Could not update hosts file: {e}"
        )

    # ---------------- RESULTS ----------------

    print(
        f"\n{G}┌── VHOST ENUMERATION COMPLETE ───────────────────────────┐{W}"
    )
    print(
        f"{G}│{W} "
        f"{B}Domain:{W} "
        f"{C}{domain:<46}{W}"
        f"{G}│{W}"
    )
    print(
        f"{G}│{W} "
        f"{B}Found:{W} "
        f"{C}{len(discovered):<47}{W}"
        f"{G}│{W}"
    )
    print(
        f"{G}│{W} "
        f"{B}Loot:{W} "
        f"{C}{str(output_txt):<48}{W}"
        f"{G}│{W}"
    )
    print(
        f"{G}└─────────────────────────────────────────────────────────┘{W}\n"
    )

    for host, fqdn in discovered:

        print(
            f"{G}[+]{W} "
            f"{fqdn}"
        )

    print()
