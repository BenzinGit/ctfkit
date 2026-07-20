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

EXTENSIONS = (
    "/usr/share/seclists/Discovery/Web-Content/"
    "web-extensions.txt"
)

PAGES = (
    "/usr/share/seclists/Discovery/Web-Content/"
    "raft-small-directories.txt"
)

# =========================================================
# HELPERS
# =========================================================

def discover_extension(url):

    cmd = [
        "ffuf",
        "-w",
        f"{EXTENSIONS}:FUZZ",
        "-u",
        f"{url.rstrip('/')}/indexFUZZ",
        "-of",
        "json",
        "-o",
        "/tmp/ffuf_ext.json",
    ]

    subprocess.run(
        cmd
    )

    try:

        with open("/tmp/ffuf_ext.json") as f:

            data = json.load(f)

    except Exception:

        return None

    hits = []

    for r in data["results"]:

        status = r["status"]

        if status not in (
            200,
            204,
            301,
            302,
            307,
            401,
            403,
        ):
            continue

        hits.append(
            r["input"]["FUZZ"]
        )

    if not hits:

        return None

    #
    # Prefer 200
    #

    for r in data["results"]:

        if r["status"] == 200:

            return r["input"]["FUZZ"].lstrip(".")

    return hits[0].lstrip(".")


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

    base = input(
        f"{Y}Base URL [{ip}]> {W}"
    ).strip()

    if not base:

        base = f"{ip}"

    path = input(
        f"{Y}Directory []> {W}"
    ).strip()

    if path:

        base = (
            base.rstrip("/")
            + "/"
            + path.strip("/")
        )

    print()

    print(
        f"{B}┌── {BOLD}PAGE FUZZING{W}{B} ─────────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} URL:{C} {base:<45}{W}{B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────────────────────┘{W}"
    )

    #
    # ---------------------------------------------------------
    # EXTENSION
    # ---------------------------------------------------------
    #

    print()

    print(
        f"{B}[*]{W} Discovering extension..."
    )

    ext = discover_extension(base)

    if not ext:

        print(
            f"{R}[!] Failed to identify extension.{W}\n"
        )

        return

    print(
        f"{G}[+] Found .{ext}{W}\n"
    )

    #
    # ---------------------------------------------------------
    # ARTIFACT
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
        f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    #
    # ---------------------------------------------------------
    # FUZZ
    # ---------------------------------------------------------
    #

    cmd = [
        "ffuf",
        "-w",
        f"{PAGES}:FUZZ",
        "-u",
        f"{base.rstrip('/')}/FUZZ.{ext}",
        "-ac",
        "-fc",
        "404",
        "-t",
        "40",
        "-of",
        "json",
        "-o",
        str(outfile),
    ]

    print(
        f"{G}[+] Running{W}\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)

    #
    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------
    #

    try:

        with open(outfile) as f:

            results = json.load(f)

    except Exception:

        return

    print()

    print(
        f"{G}[+] Results{W}\n"
    )

    for r in results["results"]:

        print(
            f"  {B}├──{W} "
            f"{C}{r['input']['FUZZ']}.{ext:<25}{W} "
            f"{Y}[{r['status']}]{W}"
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
            }
        }
    ]
