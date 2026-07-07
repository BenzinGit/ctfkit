PROVIDES = ["usernames"]
REQUIRES = []

def run(data, cred, args):

    import subprocess
    import shutil

    from pathlib import Path

    from core.paths import get_artifacts_dir

    # =========================================================
    # COLORS
    # =========================================================

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    M = '\033[95m'
    BOLD = '\033[1m'

    # =========================================================
    # INPUT
    # =========================================================

    input_arg = getattr(args, "file", None)

    if not input_arg:

        print(
            f"\n{R}[!] {W}{BOLD}MISSING INPUT FILE{W}\n"
        )

        return

    input_file = Path(
        input_arg
    ).expanduser().resolve()

    if not input_file.exists():

        print(
            f"\n{R}[!] {W}{BOLD}FILE NOT FOUND{W}"
        )

        print(
            f"{B}  └── {C}{input_file}{W}\n"
        )

        return

    # =========================================================
    # FORMATS
    # =========================================================

    formats = getattr(args, "format", None)

    if not formats:

        formats = ",".join([
            "first",
            "firstlast",
            "first.last",
            "firstlast[8]",
            "first[4]last[4]",
            "firstl",
            "f.last",
            "flast",
            "lfirst",
            "l.first",
            "lastf",
            "last",
            "last.f",
            "last.first",
            "FLast",
            "first1",
            "fl",
            "fmlast",
            "firstmiddlelast",
            "fml",
            "FL",
            "FirstLast",
            "First.Last",
            "Last"
        ])

    # =========================================================
    # TOOL
    # =========================================================

    base_dir = Path(__file__).resolve().parent.parent.parent

    tool = shutil.which(
        "username-anarchy"
    )

    if not tool:

        tool = (
            base_dir /
            "tools" /
            "username-anarchy" /
            "username-anarchy"
        )

    if not Path(tool).exists():

        print(
            f"\n{R}[!] {W}{BOLD}USERNAME-ANARCHY NOT FOUND{W}"
        )

        print(
            f"{B}  └── {W}Run: "
            f"{Y}ctf doctor --install{W}\n"
        )

        return

    # =========================================================
    # ARTIFACTS
    # =========================================================

    name = data.get("name")
    artifact_dir = (
        get_artifacts_dir(f"{name}/wordlists")
        / "users"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = Path(
        getattr(args, "out", "")
        or artifact_dir / "usernames.txt"
    ).expanduser().resolve()

    # =========================================================
    # REFERENCE MODE
    # =========================================================

    if getattr(args, "ref", False):

        print(
            f"\n{B}┌── {BOLD}MODULE: USERNAME GENERATION{W}{B} ───────────────┐{W}"
        )

        print(
            f"{B}└──────────────────────────────────────────────────────┘{W}"
        )

        print(
            f"\n{B}[*]{W} Example\n"
        )

        print(
            f"{Y}username-anarchy "
            f"--input-file {M}<names.txt>{Y} "
            f"--select-format "
            f"{M}<formats>{W}\n"
        )

        return

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: USERNAME GENERATION{W}{B} ──────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Input:{W}   "
        f"{C}{input_file.name:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}│{W}  {B}Output:{W}  "
        f"{C}{output_file.name:<38}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└─────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = (
        f"{tool} "
        f"--input-file {input_file} "
        f"--select-format {formats} "
    )

    print(
        f"\n{B}[*]{W} Running\n"
    )

    print(
        f"{Y}{cmd}{W}\n"
    )

    # =========================================================
    # EXECUTE
    # =========================================================

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    usernames = [

        x.strip()

        for x in result.stdout.splitlines()

        if x.strip()

    ]

    usernames = sorted(
        set(usernames)
    )

    if not usernames:

        print(
            f"{Y}[-] {W}No usernames generated\n"
        )

        return

    output_file.write_text(
        "\n".join(usernames)
    )

    # =========================================================
    # RESULTS
    # =========================================================

    print(
        f"{G}[+] {W}Generated "
        f"{C}{len(usernames)}{W} username(s)"
    )

    print(
        f"{B}  └── {C}{output_file}{W}\n"
    )

    return {
        "usernames": usernames
    }