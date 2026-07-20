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
# WORDLISTS
# =========================================================

WORDLISTS = {
    "1": (
        "Burp Parameters",
        "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt",
    ),
    "2": (
        "Assetnote Parameters",
        "/usr/share/seclists/Discovery/Web-Content/raft-small-words.txt",
    ),
}

DEFAULT = {
    "wordlist": WORDLISTS["1"][1],
    "threads": "40",
    "autocal": True,
    "value": "test",
}

# =========================================================
# MENU
# =========================================================

def show_menu():

    config = DEFAULT.copy()

    print()

    print(
        f"{B}┌── {BOLD}GET PARAMETER FUZZING{W}{B} ─────────────────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────┘{W}\n"
    )

    print(f"{BOLD}Wordlist{W}\n")

    for k, v in WORDLISTS.items():

        print(
            f"  {B}[{C}{k}{B}]{W} {v[0]}"
        )

    print(
        f"  {B}[{C}3{B}]{W} Custom\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    if choice == "3":

        wl = input(
            f"{Y}Wordlist> {W}"
        ).strip()

        if wl:
            config["wordlist"] = wl

    elif choice in WORDLISTS:

        config["wordlist"] = WORDLISTS[choice][1]

    value = input(
        f"{Y}Parameter Value [{config['value']}]> {W}"
    ).strip()

    if value:

        config["value"] = value

    threads = input(
        f"{Y}Threads [40]> {W}"
    ).strip()

    if threads:

        config["threads"] = threads

    ac = input(
        f"{Y}Auto Calibration [Y]> {W}"
    ).strip().lower()

    config["autocal"] = ac not in (
        "n",
        "no",
    )

    return config


# =========================================================
# HELPERS
# =========================================================

def get_baseline_size(url):

    try:

        r = subprocess.run(
            [
                "curl",
                "-ks",
                url,
            ],
            capture_output=True,
        )

        return len(r.stdout)

    except Exception:

        return None


# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    #
# ---------------------------------------------------------
# TARGET
# ---------------------------------------------------------
#

    ip = get_current_url(data)

    if not ip:

        print(
            f"\n{R}[!] No target selected.{W}\n"
        )

        return

    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip

    page = input(
        f"{Y}Page []> {W}"
    ).strip()

    if page:

        url = (
            url.rstrip("/")
            + "/"
            + page.lstrip("/")
        )

    #
    # Config
    #

    if getattr(args, "menu", False):

        config = show_menu()

    else:

        config = DEFAULT.copy()

    #
    # Baseline
    #

    print()

    print(
        f"{B}[*]{W} Measuring baseline..."
    )

    baseline = get_baseline_size(url)

    if baseline is None:

        print(
            f"{R}[!] Failed to determine baseline size.{W}\n"
        )

        return

    print(
        f"{G}[+] Baseline:{W} {baseline} bytes\n"
    )

    #
    # Artifact
    #

    artifact_dir = (
        get_artifacts_dir("web")
        /
        "ffuf"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    outfile = (
        artifact_dir
        /
        f"param_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    #
    # Command
    #

    fuzz_url = (
        f"{url}?FUZZ={config['value']}"
    )

    

    cmd = [
        "ffuf",
        "-w",
        f"{config['wordlist']}:FUZZ",
        "-u",
        fuzz_url,
        "-fs",
        str(baseline),
        "-t",
        config["threads"],
        "-of",
        "json",
        "-o",
        str(outfile),
    ]

    if config["autocal"]:

        cmd.append("-ac")

    #
    # HUD
    #

    print()

    print(
        f"{B}┌── {BOLD}MODULE: GET PARAMETER FUZZING{W}{B} ─────────┐{W}"
    )

    print(
        f"{B}│{W} URL:      {C}{url:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Value:    {C}{config['value']:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Filter:   {C}{baseline:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Threads:  {C}{config['threads']:<37}{W}{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────┘{W}"
    )

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
    )

    #
    # Parse Results
    #

    try:

        with open(outfile) as f:

            results = json.load(f)["results"]

    except Exception:

        print(
            f"{R}[!] Failed reading output.{W}\n"
        )

        return

    print()

    print(
        f"{G}[+] Results{W}\n"
    )

    if not results:

        print(
            f"  {R}No parameters discovered.{W}"
        )

    else:

        results = sorted(
            results,
            key=lambda x: (
                x["status"],
                x["length"],
            )
        )

        for r in results:

            print(
                f"  {B}├──{W} "
                f"{C}{r['input']['FUZZ']:<25}{W}"
                f"{Y}[{r['status']}] {W}"
                f"{C}{r['length']} bytes{W}"
            )

    print()

    print(
        f"{G}[+] Saved{W}"
    )

    print(
        f"{B}  └── {C}{outfile}{W}\n"
    )

    return [
        {
            "type": "artifact",
            "data": {
                "tool": "ffuf",
                "output": str(outfile),
            },
        }
    ]
