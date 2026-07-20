import json
import subprocess
from datetime import datetime

from core.paths import get_artifacts_dir

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
        "Top 5k",
        "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt",
    ),
    "2": (
        "Top 20k",
        "/usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt",
    ),
    "3": (
        "Top 110k",
        "/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt",
    ),
}

DEFAULT = {
    "wordlist": WORDLISTS["1"][1],
    "threads": "40",
    "autocal": True,
}

# =========================================================
# MENU
# =========================================================

def show_menu():

    config = DEFAULT.copy()

    print()

    print(
        f"{B}┌── {BOLD}VHOST FUZZING{W}{B} ─────────────────────────┐{W}"
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
        f"  {B}[{C}4{B}]{W} Custom\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    if choice == "4":

        wl = input(
            f"{Y}Wordlist> {W}"
        ).strip()

        if wl:
            config["wordlist"] = wl

    elif choice in WORDLISTS:

        config["wordlist"] = WORDLISTS[choice][1]

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
            text=False,
        )

        return len(r.stdout)

    except Exception:

        return None

# =========================================================
# MAIN
# =========================================================

def run(data, cred, args):

    url = input(
        f"{Y}Base URL> {W}"
    ).strip()

    if not url:

        print(
            f"\n{R}[!] Base URL required.{W}\n"
        )

        return

    domain = input(
        f"{Y}Host Header Domain> {W}"
    ).strip()

    if not domain:

        print(
            f"\n{R}[!] Host header required.{W}\n"
        )

        return

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
        f"{B}[*]{W} Measuring baseline response..."
    )

    baseline = get_baseline_size(url)

    if baseline is None:

        print(
            f"{R}[!] Failed to determine baseline size.{W}\n"
        )

        return

    print(
        f"{G}[+] Baseline size:{W} {baseline}\n"
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
        f"vhost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    #
    # Command
    #

    cmd = [
        "ffuf",
        "-w",
        f"{config['wordlist']}:FUZZ",
        "-u",
        url,
        "-H",
        f"Host: FUZZ.{domain}",
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
        f"{B}┌── {BOLD}MODULE: VHOST FUZZING{W}{B} ─────────────────┐{W}"
    )

    print(
        f"{B}│{W} URL:      {C}{url:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Domain:   {C}{domain:<37}{W}{B}│{W}"
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
    # Results
    #

    try:

        with open(outfile) as f:

            results = json.load(f)["results"]

    except Exception:

        print(
            f"{R}[!] Failed to read results.{W}\n"
        )

        return

    print()

    print(
        f"{G}[+] Results{W}\n"
    )

    if not results:

        print(
            f"  {R}No virtual hosts discovered.{W}"
        )

    else:

        for r in sorted(
            results,
            key=lambda x: (
                x["status"],
                x["length"],
            ),
        ):

            host = (
                r["input"]["FUZZ"]
                + "."
                + domain
            )

            print(
                f"  {B}├──{W} "
                f"{C}{host:<35}{W}"
                f"{Y}[{r['status']}] "
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
