import subprocess
from datetime import datetime

from core.paths import get_artifacts_dir
from core.target import get_current_url
import json


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
# DEFAULTS
# =========================================================

WORDLISTS = {
    "1": (
        "RAFT Small",
        "/usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt",
    ),
    "2": (
        "RAFT Medium",
        "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt",
    ),
    "3": (
        "RAFT Large",
        "/usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt",
    ),
    "4": (
        "Directory List 2.3 Small",
        "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt",
    ),
    "5": (
        "Directory List 2.3 Medium",
        "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt",
    ),
}

DEFAULT = {
    "wordlist": WORDLISTS["1"][1],
    "threads": "40",
    "extensions": "",
    "status": "404",
    "recursion": False,
    "depth": "1",
    "autocal": True,
    "verbose": True,
}


# =========================================================
# MENU
# =========================================================

def show_menu():

    config = DEFAULT.copy()

    print()

    print(
        f"{B}┌── {BOLD}DIRECTORY FUZZING{W}{B} ──────────────────────┐{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────┘{W}"
    )

    print()

    print(f"{BOLD}Wordlist{W}\n")

    for k, v in WORDLISTS.items():

        print(
            f"  {B}[{C}{k}{B}]{W} {v[0]}"
        )

    print(
        f"  {B}[{C}6{B}]{W} Custom\n"
    )

    choice = input(
        f"{Y}Select> {W}"
    ).strip()

    if choice == "6":

        wl = input(
            f"{Y}Wordlist> {W}"
        ).strip()

        if wl:
            config["wordlist"] = wl

    elif choice in WORDLISTS:

        config["wordlist"] = WORDLISTS[choice][1]

    ext = input(
        f"{Y}Extensions []> {W}"
    ).strip()

    if ext:
        config["extensions"] = ext

    threads = input(
        f"{Y}Threads [40]> {W}"
    ).strip()

    if threads:
        config["threads"] = threads

    status = input(
        f"{Y}Filter Status [404]> {W}"
    ).strip()

    if status:
        config["status"] = status

    rec = input(
        f"{Y}Recursion [N]> {W}"
    ).strip().lower()

    config["recursion"] = rec in ("y", "yes")

    if config["recursion"]:

        depth = input(
            f"{Y}Recursion Depth [1]> {W}"
        ).strip()

        if depth:
            config["depth"] = depth

    return config


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
    
    url = ip


    url = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip() or ip
    print(url)

    #
    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------
    #

    if getattr(args, "menu", False):

        config = show_menu()

    else:

        config = DEFAULT.copy()

    #
    # ---------------------------------------------------------
    # ARTIFACTS
    # ---------------------------------------------------------
    #

    artifact_dir = (
        get_artifacts_dir(
            data["name"]
        )
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
        f"dir_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    #
    # ---------------------------------------------------------
    # COMMAND
    # ---------------------------------------------------------
    #

    cmd = [
        "ffuf",
        "-w",
        f"{config['wordlist']}:FUZZ",
        "-u",
        f"{url.rstrip('/')}/FUZZ",
        "-t",
        config["threads"],
        "-fc",
        config["status"],
        "-of",
        "json",
        "-o",
        str(outfile),
    ]

    if config["autocal"]:

        cmd.append("-ac")

    if config["recursion"]:

        cmd.extend([
        "-recursion",
        "-recursion-depth",
        config["depth"],
    ])

    if config["extensions"]:

        cmd.extend([
            "-e",
            ",".join(
                "." + x.strip().lstrip(".")
                for x in config["extensions"].split(",")
            ),
        ])

    #
    # ---------------------------------------------------------
    # HUD
    # ---------------------------------------------------------
    #

    print()

    print(
        f"{B}┌── {BOLD}MODULE: DIRECTORY FUZZING{W}{B} ──────────────┐{W}"
    )

    print(
        f"{B}│{W} URL:      {C}{url:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Threads:  {C}{config['threads']:<37}{W}{B}│{W}"
    )

    print(
        f"{B}│{W} Output:   {C}{outfile.name:<37}{W}{B}│{W}"
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

    subprocess.run(cmd, stdout=subprocess.DEVNULL)
    with open(outfile) as f:
        results = json.load(f)["results"]

    dirs = []
    files = []

    for r in results:

        url = r["url"]
        status = r["status"]

        if url.endswith("/"):
            dirs.append((url, status))
        else:
            files.append((url, status))
    print()

    print(f"{G}[+] Results{W}\n")

    if dirs:

        print(f"{B}Directories{W}")

        for url, status in sorted(dirs):

            print(
                f"  {B}├──{W} {C}{url}{W} {Y}[{status}]{W}"
            )

        print()

    if files:

        print(f"{B}Files{W}")

        for url, status in sorted(files):

            print(
                f"  {B}├──{W} {C}{url}{W} {Y}[{status}]{W}"
            )

        print()

    print()

    print(
        f"{G}[+] Results Saved{W}"
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