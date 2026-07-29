import subprocess

from core.target import get_current_url


NAME = "app.wordpress.enum"
DESCRIPTION = "Enumerate a WordPress installation."


G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[0m"


def run_cmd(cmd):

    print(f"\n{Y}$ {cmd}{W}\n")

    subprocess.run(
        cmd,
        shell=True,
    )


def run(data, cred, args):

    url = get_current_url(data)

    if not url:
        print(f"{R}[-] No target URL configured.{W}")
        return

    print(f"{G}[+] WordPress Enumeration{W}")

    run_cmd(f'curl -s "{url}" | grep WordPress')

    run_cmd(f'curl -s "{url}" | grep themes')

    run_cmd(f'curl -s "{url}" | grep plugins')

    run_cmd(f'sudo wpscan --url "{url}" --enumerate')