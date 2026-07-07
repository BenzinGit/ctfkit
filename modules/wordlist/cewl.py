from pathlib import Path
from urllib.parse import urlparse
import subprocess

from core.target import get_current_url
from core.paths import get_artifacts_dir


def run(data, cred, args):

    # =========================================================
    # COLORS
    # =========================================================

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    W = '\033[0m'
    R = '\033[91m'
    BOLD = '\033[1m'

    # =========================================================
    # TARGET URL
    # =========================================================

    url = None

    if hasattr(args, "extra") and args.extra:
        url = args.extra[0]

    if not url:
        url = get_current_url(data)

    if not url:

        print(f"\n{R}[!] {W}{BOLD}NO TARGET URL{W}")
        print(f"{B}  └── Usage:{W} ctf wordlist.cewl https://target.com")
        return

    # =========================================================
    # OPTIONS
    # =========================================================

    depth = getattr(args, "depth", None) or 4
    minimum = getattr(args, "min", None) or 6

    # =========================================================
    # OUTPUT FILE
    # =========================================================

    parsed = urlparse(url)
    name = data.get("name")
    hostname = parsed.netloc

    if not hostname:
        hostname = url.replace("https://", "").replace("http://", "")


    artifact_dir = (
        get_artifacts_dir(name)
        / "cewl"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    outfile = artifact_dir / f"{hostname}.txt"

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        cmd = (
            f"cewl {url} "
            f"-d {depth} "
            f"-m {minimum} "
            f"--lowercase "
            f"--with-numbers "
            f"-w {outfile}"
        )

        print(f"\n{B}┌── {BOLD}MODULE: CEWL WORDLIST{W}{B} ─────────────────────┐{W}")
        print(f"{B}└───────────────────────────────────────────────────────┘{W}")

        print(f"\n{B}[*]{W} Reference Command\n")
        print(f"{Y}{cmd}{W}\n")

        return

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: CEWL WORDLIST{W}{B} "
        f"{'─' * 23}┐{W}"
    )

    print(
        f"{B}│{W}  {B}URL:{W}      "
        f"{C}{url:<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Depth:{W}    "
        f"{C}{str(depth):<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Min Len:{W}  "
        f"{C}{str(minimum):<42}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└{'─' * 56}┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = [
        "cewl",
        url,
        "-d",
        str(depth),
        "-m",
        str(minimum),
        "--lowercase",
        "--with-numbers",
        "-w",
        str(outfile)
    ]

    print(f"\n{B}[*]{W} Running\n")
    print(f"{Y}{' '.join(cmd)}{W}\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(f"{R}[!] {W}CeWL failed\n")

        if result.stderr:
            print(result.stderr)

        return

    # =========================================================
    # STATS
    # =========================================================

    count = 0

    try:

        count = len(
            [
                x.strip()
                for x in outfile.read_text(
                    errors="ignore"
                ).splitlines()
                if x.strip()
            ]
        )

    except Exception:
        pass

    print(
        f"{G}[+] {W}Collected "
        f"{C}{count}{W} words"
    )

    print(
        f"{G}[+] {W}Saved: "
        f"{C}{outfile}{W}\n"
    )


    print(
        f"{B}[*]{W} Next Step\n"
    )

    print(
        f"  {B}├──{W} Generate mutations:\n"
    )

    print(
        f"      {Y}ctf wordlist.rules {outfile}{W}\n"
    )

    print(
        f"  {B}└──{W} Use for cracking:\n"
    )

    print(
        f"      {Y}ctf crack.hash <hash> -w {outfile}{W}\n"
    )     
            

    return [
        {
            "type": "wordlist",
            "data": {
                "file": str(outfile),
                "count": count,
                "source": url
            }
        }
    ]

   
