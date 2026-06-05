import re
import runpy
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

MODULE_DIR = (
    BASE_DIR /
    "modules" /
    "privesc" /
    "windows" /
    "kernel-exploits"
)

# =========================================================
# HELPERS
# =========================================================

def ask(prompt):

    try:
        return input(prompt).strip()

    except (KeyboardInterrupt, EOFError):

        print()
        return None

# =========================================================
# PARSERS
# =========================================================

def parse_build(text):

    match = re.search(
        r"(\d{5})",
        text
    )

    if match:
        return int(match.group(1))

    return None


def parse_arch(text):

    text = text.lower()

    if "64" in text:
        return "x64"

    if "86" in text:
        return "x86"

    return None


def parse_hotfixes(text):

    return re.findall(
        r"(KB\d+)",
        text,
        re.I
    )


def parse_integrity(text):

    text = text.lower()

    if "system mandatory level" in text:
        return "system"

    if "high mandatory level" in text:
        return "high"

    if "medium mandatory level" in text:
        return "medium"

    if "low mandatory level" in text:
        return "low"

    return "unknown"

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

        meta = folder / "meta.yaml"

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

def build_match(
    target_build,
    exploit,
):

    build = exploit.get(
        "build",
        {}
    )

    min_v = build.get("min")
    max_v = build.get("max")

    if min_v:

        if target_build < min_v:
            return False

    if max_v:

        if target_build > max_v:
            return False

    return True


def arch_match(
    target_arch,
    exploit,
):

    exploit_arch = exploit.get(
        "arch"
    )

    if not exploit_arch:
        return True

    return (
        exploit_arch ==
        target_arch
    )


def hotfix_match(
    target_hotfixes,
    exploit,
):

    required_missing = exploit.get(
        "missing_kbs",
        []
    )

    for kb in required_missing:

        if kb in target_hotfixes:
            return False

    return True


def integrity_match(
    target_integrity,
    exploit,
):

    required = exploit.get(
        "integrity"
    )

    if not required:
        return True

    return (
        required ==
        target_integrity
    )


def exploit_matches(
    target,
    exploit,
):

    if not build_match(
        target["build"],
        exploit,
    ):
        return False

    if not arch_match(
        target["arch"],
        exploit,
    ):
        return False

    if not hotfix_match(
        target["hotfixes"],
        exploit,
    ):
        return False

    if not integrity_match(
        target["integrity"],
        exploit,
    ):
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
        f"integrity: "
        f"{Y}{target['integrity']}{W}"
    )

    print(
        f"  {G}└──{W} "
        f"hotfixes: "
        f"{Y}{len(target['hotfixes'])}{W}"
    )


def render_matches(matches):

    print(
        f"\n{B}[*]{W} "
        f"MATCHING KERNEL EXPLOITS\n"
    )

    for idx, exploit in enumerate(
        matches,
        start=1
    ):

        print(
            f"  [{idx}] "
            f"{W_BOLD}"
            f"{exploit.get('name')}"
            f"{W} "
            f"({Y}{exploit.get('cve')}{W})"
        )


def render_exploit(exploit):

    print(
        f"\n{G}"
        f"┌── EXPLOIT "
        f"─────────────────────────────────────────┐{W}"
    )

    print(
        f"{G}│{W} "
        f"name: "
        f"{exploit.get('name')}"
    )

    print(
        f"{G}│{W} "
        f"cve: "
        f"{exploit.get('cve')}"
    )

    build = exploit.get(
        "build",
        {}
    )

    print(
        f"{G}│{W} "
        f"builds: "
        f"{build.get('min')} - "
        f"{build.get('max')}"
    )

    print(
        f"{G}│{W} "
        f"arch: "
        f"{exploit.get('arch')}"
    )

    missing = exploit.get(
        "missing_kbs",
        []
    )

    if missing:

        print(
            f"{G}│{W} "
            f"requires missing:"
        )

        for kb in missing:

            print(
                f"{G}│{W} "
                f"  - {kb}"
            )

    module = exploit.get(
        "module"
    )

    if module:

        print(
            f"{G}│{W} "
            f"module: "
            f"{C}{module}{W}"
        )

    print(
        f"{G}"
        f"└──────────────────────────────────────────────────────────┘{W}"
    )

# =========================================================
# MODES
# =========================================================

def select_mode():

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS KERNEL EXPLOITS{W}\n"
    )

    print(
        f"  {G}├──{W} "
        f"[1] Match target"
    )

    print(
        f"  {G}└──{W} "
        f"[2] Browse exploits"
    )

    return ask(
        f"\n{B}select{W}> "
    )


def browse_exploits(
    exploits,
):

    print(
        f"\n{B}[*]{W} "
        f"AVAILABLE KERNEL EXPLOITS\n"
    )

    for idx, exploit in enumerate(
        exploits,
        start=1
    ):

        print(
            f"  [{idx}] "
            f"{W_BOLD}"
            f"{exploit.get('name')}"
            f"{W} "
            f"({Y}{exploit.get('cve')}{W})"
        )

    choice = ask(
        f"\n{B}select{W}> "
    )

    if not choice:
        return None

    if not choice.isdigit():
        return None

    choice = int(choice)

    if (
        choice < 1 or
        choice > len(exploits)
    ):
        return None

    return exploits[
        choice - 1
    ]


def match_target(
    exploits,
):

    # =====================================================
    # BUILD
    # =====================================================

    print(
        f"\n{B}[*]{W} BUILD\n"
    )

    print(
        f"  {B}└──{W} "
        f"wmic os get Caption,Version,BuildNumber"
    )

    build_text = ask(
        f"\n{B}build{W}> "
    )

    if not build_text:
        return None

    build = parse_build(
        build_text
    )

    if not build:

        print(
            f"\n{R}[!] "
            f"Failed to parse build.{W}"
        )

        return None

    # =====================================================
    # ARCH
    # =====================================================

    print(
        f"\n{B}[*]{W} ARCHITECTURE\n"
    )

    print(
        f"  {B}└──{W} "
        f"echo %PROCESSOR_ARCHITECTURE%"
    )

    arch_text = ask(
        f"\n{B}arch{W}> "
    )

    if not arch_text:
        return None

    arch = parse_arch(
        arch_text
    )

    # =====================================================
    # HOTFIXES
    # =====================================================

    print(
        f"\n{B}[*]{W} HOTFIXES\n"
    )

    print(
        f"  {B}└──{W} "
        f"wmic qfe list brief"
    )

    hotfix_text = ask(
        f"\n{B}hotfixes{W}> "
    )

    if hotfix_text is None:
        return None

    hotfixes = parse_hotfixes(
        hotfix_text
    )

    # =====================================================
    # INTEGRITY
    # =====================================================

    print(
        f"\n{B}[*]{W} INTEGRITY\n"
    )

    print(
        f"  {B}└──{W} "
        f"whoami /groups"
    )

    integrity_text = ask(
        f"\n{B}groups{W}> "
    )

    if integrity_text is None:
        return None

    integrity = parse_integrity(
        integrity_text
    )

    # =====================================================
    # TARGET
    # =====================================================

    target = {

        "build": build,
        "arch": arch,
        "hotfixes": hotfixes,
        "integrity": integrity,

    }

    render_target(target)

    matches = find_matches(
        target,
        exploits,
    )

    if not matches:

        print(
            f"\n{R}[!] "
            f"No matching kernel exploits found.{W}"
        )

        return None

    render_matches(matches)

    choice = ask(
        f"\n{B}select{W}> "
    )

    if not choice:
        return None

    if not choice.isdigit():
        return None

    choice = int(choice)

    if (
        choice < 1 or
        choice > len(matches)
    ):
        return None

    return matches[
        choice - 1
    ]

# =========================================================
# MODULE RUNNER
# =========================================================

def run_module(exploit):

    module_name = exploit.get(
        "module"
    )

    if not module_name:

        print(
            f"\n{R}[!] "
            f"No exploit module defined.{W}"
        )

        return

    module_path = (
        MODULE_DIR /
        f"{module_name}.py"
    )

    if not module_path.exists():

        print(
            f"\n{R}[!] "
            f"Exploit module not found:{W}"
        )

        print(
            f"  {module_path}"
        )

        return

    print(
        f"\n{G}[+]{W} "
        f"Launching exploit module:\n"
    )

    print(
        f"  {C}{module_name}{W}"
    )

    print()

    try:

        runpy.run_path(
            str(module_path),
            run_name="__main__"
        )

    except Exception as e:

        print(
            f"\n{R}[!] "
            f"Exploit module crashed:{W}"
        )

        print(
            f"  {e}"
        )

# =========================================================
# MAIN
# =========================================================

def run(
    data=None,
    cred=None,
    args=None,
):

    exploits = load_exploits()

    if not exploits:

        print(
            f"\n{R}[!] "
            f"No kernel exploits loaded.{W}"
        )

        return data

    mode = select_mode()

    if not mode:
        return data

    selected = None

    # =====================================================
    # MATCH MODE
    # =====================================================

    if mode == "1":

        selected = match_target(
            exploits
        )

    # =====================================================
    # BROWSE MODE
    # =====================================================

    elif mode == "2":

        selected = browse_exploits(
            exploits
        )

    else:

        return data

    if not selected:
        return data

    render_exploit(
        selected
    )

    # =====================================================
    # RUN MODULE
    # =====================================================

    run_choice = ask(
        f"\n{B}run exploit module? (y/n){W}> "
    )

    if not run_choice:
        return data

    if run_choice.lower() != "y":
        return data

    run_module(
        selected
    )

    return data