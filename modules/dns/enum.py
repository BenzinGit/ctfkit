import subprocess


PROVIDES = []
REQUIRES = ["ip"]


def run(data, cred, args):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    M = '\033[95m'

    reference = getattr(
        args,
        "reference",
        False
    )

    menu = getattr(
        args,
        "menu",
        False
    )

    # -----------------------------
    # REFERENCE
    # -----------------------------

    if reference:

        print(
            f"\n{B}┌── REFERENCE "
            f"──────────────────────────────────────┐{W}"
        )

        print()

        print(
            f"{Y}dig ns {M}<DOMAIN>{W} @{M}<DNS>{W}"
        )

        print()

        print(
            f"{Y}dig any {M}<DOMAIN>{W} @{M}<DNS>{W}"
        )

        print()

        print(
            f"{Y}dig axfr {M}<DOMAIN>{W} @{M}<DNS>{W}"
        )

        print()

        print(
            f"{Y}dig CH TXT version.bind {M}<DNS>{W}"
        )

        print()

        print(
            f"{Y}dnsenum "
            f"--dnsserver {M}<DNS>{W} "
            f"--enum "
            f"-p 0 "
            f"-s 0 "
            f"-f /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt "
            f"{M}<DOMAIN>{W}"
        )

        print(
            f"\n{B}└──────────────────────────────────────────────┘{W}\n"
        )

        return

    # -----------------------------
    # TARGET
    # -----------------------------

    dns = data.get("ip")
    domain = data.get("domain")
    if not dns:

        print(
            f"\n{R}[!]{W} "
            f"No target IP loaded."
        )

        return

    if not domain: 
        domain = input(
            "\nDomain: "
        ).strip()

        if not domain:

            print(
                f"\n{R}[!]{W} "
                f"Domain required."
            )

            return

    # -----------------------------
    # MENU
    # -----------------------------

    mode = "full"

    if menu:

        print()

        print(
            "[1] Full Enumeration"
        )

        print(
            "[2] Zone Transfer"
        )

        print(
            "[3] Subdomain Brute Force"
        )

        print()

        choice = input(
            "> "
        ).strip()

        if choice == "2":

            mode = "axfr"

        elif choice == "3":

            mode = "brute"

    # -----------------------------
    # HEADER
    # -----------------------------

    print(
        f"\n{B}┌── MODULE: DNS ENUMERATION "
        f"────────────────────┐{W}"
    )

    print(
        f"{B}│{W} "
        f"DNS:    "
        f"{C}{dns:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W} "
        f"DOMAIN: "
        f"{C}{domain:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────────┘{W}"
    )

    # -----------------------------
    # AXFR ONLY
    # -----------------------------

    if mode == "axfr":

        cmd = (
            f"dig axfr "
            f"{domain} "
            f"@{dns}"
        )

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"ZONE TRANSFER\n"
        )

        print(
            f"{Y}{cmd}{W}\n"
        )

        subprocess.run(
            cmd,
            shell=True
        )

        return

    # -----------------------------
    # BRUTE ONLY
    # -----------------------------

    if mode == "brute":

        cmd = (
            f"dnsenum "
            f"--dnsserver {dns} "
            f"--enum "
            f"-p 0 "
            f"-s 0 "
            f"-f "
            f"/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt "
            f"{domain}"
        )

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"SUBDOMAIN ENUMERATION\n"
        )

        print(
            f"{Y}{cmd}{W}\n"
        )

        subprocess.run(
            cmd,
            shell=True
        )

        return

    # -----------------------------
    # FULL ENUM
    # -----------------------------

    commands = [

        (
            "NAME SERVERS",
            f"dig ns {domain} @{dns}"
        ),

        (
            "ANY RECORDS",
            f"dig any {domain} @{dns}"
        ),

        (
            "VERSION",
            f"dig CH TXT version.bind {dns}"
        ),

        (
            "ZONE TRANSFER",
            f"dig axfr {domain} @{dns}"
        ),

        (
            "SUBDOMAIN ENUMERATION",
            f"dnsenum "
            f"--dnsserver {dns} "
            f"--enum "
            f"-p 0 "
            f"-s 0 "
            f"-f "
            f"/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt "
            f"{domain}"
        )

    ]

    # -----------------------------
    # EXECUTE
    # -----------------------------

    for title, cmd in commands:

        print(
            f"\n{B}[{W}{G}*{W}{B}]{W} "
            f"{title}\n"
        )

        print(
            f"{Y}{cmd}{W}\n"
        )

        subprocess.run(
            cmd,
            shell=True
        )

        print()
