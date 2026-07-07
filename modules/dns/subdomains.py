from core.paths import get_chain_artifacts_dir
from datetime import datetime
import subprocess


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    domain = data.get("domain")

    if not domain:

        print(
            f"\n{R}[!] {W}No domain configured\n"
        )

        return data

    artifact_dir = get_chain_artifacts_dir(
        data["name"],
        "dns"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    logfile = (
        artifact_dir /
        f"subfinder_{timestamp}.log"
    )

    output_file = (
        artifact_dir /
        "subdomains.txt"
    )

    cmd = [
        "subfinder",
        "-d",
        domain,
        "-v"
    ]

    print(
        f"\n{B}┌── {BOLD}MODULE: DNS SUBDOMAIN ENUM{W}{B} ─────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{domain:<32}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd
    )

    logfile.write_text(
        result.stdout +
        result.stderr
    )

    subdomains = set()

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("["):
            continue

        if domain not in line:
            continue

        subdomains.add(
            line
        )

    subdomains = sorted(
        subdomains
    )

    if not subdomains:

        print(
            f"{Y}[-]{W} No subdomains found\n"
        )

        return data

    output_file.write_text(
        "\n".join(subdomains)
    )

    print(
        f"{G}[+] {W}"
        f"{len(subdomains)} subdomain(s) recovered\n"
    )

    for subdomain in subdomains[:20]:

        print(
            f"  {B}├──{W} "
            f"{C}{subdomain}{W}"
        )

    if len(subdomains) > 20:

        print(
            f"\n  {B}└──{W} "
            f"{C}+{len(subdomains)-20}{W} more"
        )

    print()

    print(
        f"{G}[+] {W}Artifacts"
    )

    print(
        f"{B}  ├── {C}{output_file}{W}"
    )

    print(
        f"{B}  └── {C}{logfile}{W}\n"
    )

    data["subdomains"] = subdomains

    return data
