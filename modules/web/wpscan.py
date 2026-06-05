import subprocess


PROVIDES = []
REQUIRES = []


def run(data, cred, args):

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    target = getattr(args, "file", None)

    if not target:

        domain = data.get("domain")

        if domain:
            target = f"http://{domain}"
        else:

            ip = data.get("ip")

            if not ip:
                print(
                    f"\n{R}[!] {W}{BOLD}NO TARGET CONFIGURED{W}"
                )
                return

            target = f"http://{ip}"

    cmd = [
        "sudo",
        "wpscan",
        "-e",
        "ap,u",
        "-t",
        "500",
        "--url",
        target
    ]

    print(
        f"\n{B}┌── {BOLD}WORDPRESS ENUMERATION{W}{B} ───────────────────────┐{W}"
    )
    print(
        f"{B}│{W}  {B}Target:{W} {C}{target:<40}{W}{B}│{W}"
    )
    print(
        f"{B}└──────────────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}COMMAND{W}\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)
