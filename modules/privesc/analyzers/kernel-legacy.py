import re
from pathlib import Path

import yaml

# =========================================================
# UI
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'

W_BOLD = '\033[1m'
DIM = '\033[2m'

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

EXPLOIT_DIR = (
    BASE_DIR /
    "exploits" /
    "windows" /
    "kernel"
)

# =========================================================
# MULTILINE INPUT
# =========================================================

def multiline_input(prompt):

    print(f"\n{prompt}")

    print(
        f"{DIM}"
        f"(finish with CTRL+D / CTRL+Z)"
        f"{W}"
    )

    lines = []

    try:

        while True:

            lines.append(input())

    except EOFError:

        pass

    return "\n".join(lines)

# =========================================================
# PARSERS
# =========================================================

def parse_build(text):

    match = re.search(
        r"Build\s+(\d+)",
        text,
        re.I
    )

    if match:
        return int(match.group(1))

    match = re.search(
        r"(\d{5})",
        text
    )

    if match:
        return int(match.group(1))

    return None


def parse_arch(text):

    text = text.lower()

    if (
        "x64" in text or
        "64-based" in text or
        "amd64" in text
    ):
        return "x64"

    if (
        "x86" in text or
        "32" in text
    ):
        return "x86"

    return None


def parse_hotfixes(text):

    return re.findall(
        r"(KB\d+)",
        text,
        re.I
    )


def parse_privs(text):

    found = []

    known = [

        "SeImpersonatePrivilege",
        "SeAssignPrimaryTokenPrivilege",
        "SeLoadDriverPrivilege",
        "SeBackupPrivilege",
        "SeRestorePrivilege",
        "SeDebugPrivilege",
        "SeTakeOwnershipPrivilege",

    ]

    for priv in known:

        if priv.lower() in text.lower():

            found.append(priv)

    return found


def parse_uac(text):

    result = {

        "EnableLUA": None,
        "ConsentPromptBehaviorAdmin": None,

    }

    enable = re.search(
        r"EnableLUA\s+REG_DWORD\s+(0x\d+)",
        text,
        re.I
    )

    if enable:

        result["EnableLUA"] = (
            enable.group(1)
        )

    consent = re.search(
        r"ConsentPromptBehaviorAdmin\s+REG_DWORD\s+(0x\d+)",
        text,
        re.I
    )

    if consent:

        result["ConsentPromptBehaviorAdmin"] = (
            consent.group(1)
        )

    return result


def parse_spooler(text):

    return (
        "running" in text.lower()
    )


# =========================================================
# HELPERS
# =========================================================

def build_in_range(
    build,
    min_v=None,
    max_v=None,
):

    if min_v:

        if build < min_v:
            return False

    if max_v:

        if build > max_v:
            return False

    return True

# =========================================================
# LOAD
# =========================================================

def load_exploits():

    exploits = []

    if not EXPLOIT_DIR.exists():
        return exploits

    for folder in EXPLOIT_DIR.iterdir():

        if not folder.is_dir():
            continue

        meta = (
            folder /
            "meta.yaml"
        )

        if not meta.exists():
            continue

        try:

            data = yaml.safe_load(
                meta.read_text()
            )

            if not data:
                continue

            data["folder"] = folder

            exploits.append(data)

        except Exception:
            continue

    return exploits

# =========================================================
# MATCHING
# =========================================================

def exploit_matches(
    target,
    exploit,
):

    # -----------------------------------------------------
    # BUILD
    # -----------------------------------------------------

    build = exploit.get(
        "build",
        {}
    )

    min_v = build.get("min")
    max_v = build.get("max")

    if not build_in_range(
        target["build"],
        min_v,
        max_v,
    ):
        return False

    # -----------------------------------------------------
    # ARCH
    # -----------------------------------------------------

    arch = exploit.get("arch")

    if arch:

        if arch != target["arch"]:
            return False

    # -----------------------------------------------------
    # REQUIRED
    # -----------------------------------------------------

    required = exploit.get(
        "requires",
        []
    )

    for item in required:

        # -------------------------------------------------
        # PRIVS
        # -------------------------------------------------

        if item.startswith("priv:"):

            priv = item.split(
                ":",
                1
            )[1]

            if priv not in target["privs"]:
                return False

        # -------------------------------------------------
        # SPOOLER
        # -------------------------------------------------

        elif item == "spooler":

            if not target["spooler"]:
                return False

        # -------------------------------------------------
        # UAC
        # -------------------------------------------------

        elif item == "uac":

            if (
                target["uac"]
                .get("EnableLUA")
                != "0x1"
            ):
                return False

        # -------------------------------------------------
        # HOTFIX MISSING
        # -------------------------------------------------

        elif item.startswith("missing:"):

            kb = item.split(
                ":",
                1
            )[1]

            if kb in target["hotfixes"]:
                return False

    return True


def find_matches(
    target,
    exploits,
):

    matches = []

    for exploit in exploits:

        if exploit_matches(
            target,
            exploit,
        ):
            matches.append(exploit)

    return matches

# =========================================================
# RENDER
# =========================================================

def render_target(target):

    print(
        f"\n{B}[*]{W} TARGET\n"
    )

    print(
        f"  {G}├──{W} "
        f"build: "
        f"{Y}{target['build']}{W}"
    )

    print(
        f"  {G}├──{W} "
        f"arch: "
        f"{Y}{target['arch']}{W}"
    )

    print(
        f"  {G}├──{W} "
        f"spooler: "
        f"{Y}{target['spooler']}{W}"
    )

    print(
        f"  {G}├──{W} "
        f"UAC: "
        f"{Y}{target['uac']['EnableLUA']}{W}"
    )

    print(
        f"  {G}├──{W} "
        f"hotfixes: "
        f"{Y}{len(target['hotfixes'])}{W}"
    )

    if target["privs"]:

        print(
            f"  {G}└──{W} "
            f"privs: "
            f"{Y}{', '.join(target['privs'])}{W}"
        )

    else:

        print(
            f"  {G}└──{W} "
            f"privs: "
            f"{R}none parsed{W}"
        )


def render_matches(matches):

    print(
        f"\n{B}[*]{W} "
        f"MATCHING EXPLOITS\n"
    )

    for idx, exploit in enumerate(
        matches,
        start=1
    ):

        name = exploit.get(
            "name",
            "unknown"
        )

        cve = exploit.get(
            "cve",
            "unknown"
        )

        print(
            f"  [{idx}] "
            f"{W_BOLD}{name}{W} "
            f"({Y}{cve}{W})"
        )


def render_metadata(exploit):

    print(
        f"\n{G}"
        f"┌── EXPLOIT METADATA "
        f"────────────────────────────────────┐{W}"
    )

    build = exploit.get(
        "build",
        {}
    )

    print(
        f"{G}│{W} "
        f"build range: "
        f"{build.get('min')} - "
        f"{build.get('max')}"
    )

    arch = exploit.get("arch")

    if arch:

        print(
            f"{G}│{W} "
            f"arch: "
            f"{arch}"
        )

    requires = exploit.get(
        "requires",
        []
    )

    if requires:

        print(
            f"{G}│{W} "
            f"requires:"
        )

        for item in requires:

            print(
                f"{G}│{W} "
                f"  - {item}"
            )

    notes = exploit.get(
        "notes",
        []
    )

    if notes:

        print(f"{G}│{W}")

        for note in notes:

            print(
                f"{G}│{W} "
                f"note: "
                f"{DIM}{note}{W}"
            )

    source = exploit.get(
        "source",
        {}
    )

    github = source.get("github")

    if github:

        print(
            f"{G}│{W} "
            f"source: "
            f"{C}{github}{W}"
        )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────────────┘{W}"
    )

# =========================================================
# MAIN
# =========================================================

def run(
    data=None,
    cred=None,
    args=None,
):

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS KERNEL MATCHER{W}"
    )

    # =====================================================
    # SYSTEMINFO
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"SYSTEMINFO\n"
    )

    print(
        f"  {B}└──{W} "
        f"systeminfo"
    )

    systeminfo = multiline_input(
        f"{B}paste systeminfo{W}"
    )

    build = parse_build(
        systeminfo
    )

    if not build:

        print(
            f"\n{R}[!] "
            f"Failed to parse build.{W}"
        )

        return data

    arch = parse_arch(
        systeminfo
    )

    hotfixes = parse_hotfixes(
        systeminfo
    )

    # =====================================================
    # PRIVILEGES
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"PRIVILEGES\n"
    )

    print(
        f"  {B}└──{W} "
        f"whoami /priv"
    )

    priv_text = multiline_input(
        f"{B}paste whoami /priv{W}"
    )

    privs = parse_privs(
        priv_text
    )

    # =====================================================
    # SPOOLER
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"SPOOLER\n"
    )

    print(
        f"  {B}└──{W} "
        f"sc query spooler"
    )

    spooler_text = multiline_input(
        f"{B}paste spooler output{W}"
    )

    spooler = parse_spooler(
        spooler_text
    )

    # =====================================================
    # UAC
    # =====================================================

    print(
        f"\n{B}[*]{W} "
        f"UAC\n"
    )

    print(
        f"  {B}├──{W} "
        f"REG QUERY "
        f"HKLM\\...\\Policies\\System "
        f"/v EnableLUA"
    )

    print(
        f"  {B}└──{W} "
        f"REG QUERY "
        f"HKLM\\...\\Policies\\System "
        f"/v ConsentPromptBehaviorAdmin"
    )

    uac_text = multiline_input(
        f"{B}paste UAC registry output{W}"
    )

    uac = parse_uac(
        uac_text
    )

    # =====================================================
    # TARGET
    # =====================================================

    target = {

        "build": build,
        "arch": arch,
        "hotfixes": hotfixes,
        "privs": privs,
        "spooler": spooler,
        "uac": uac,

    }

    render_target(target)

    # =====================================================
    # LOAD
    # =====================================================

    exploits = load_exploits()

    if not exploits:

        print(
            f"\n{R}[!] "
            f"No exploits loaded.{W}"
        )

        return data

    # =====================================================
    # MATCH
    # =====================================================

    matches = find_matches(
        target,
        exploits,
    )

    if not matches:

        print(
            f"\n{R}[!] "
            f"No matching exploits found.{W}"
        )

        return data

    render_matches(matches)

    # =====================================================
    # SELECT
    # =====================================================

    print()

    try:

        choice = input(
            f"{B}select{W}> "
        ).strip()

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    if not choice.isdigit():
        return data

    choice = int(choice)

    if (
        choice < 1 or
        choice > len(matches)
    ):
        return data

    exploit = matches[
        choice - 1
    ]

    render_metadata(
        exploit
    )

    return data