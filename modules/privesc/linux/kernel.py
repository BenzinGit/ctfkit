import re
import shutil
import subprocess
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

EXPLOIT_DIR = BASE_DIR / "exploits" / "kernel"

CACHE_DIR = Path.home() / ".ctfkit" / "cache" / "kernel"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# PARSERS
# =========================================================

def parse_kernel(text):

    match = re.search(r"(\d+)\.(\d+)", text)

    if not match:
        return None

    return f"{match.group(1)}.{match.group(2)}"


def parse_distro(text):

    text = text.lower().strip()

    if not text:
        return None

    known = [
        "ubuntu",
        "debian",
        "kali",
        "arch",
        "fedora",
        "centos",
        "redhat",
        "rhel",
        "parrot"
    ]

    for distro in known:

        if distro in text:
            return distro

    return None


def parse_version(text):

    match = re.search(r"(\d+\.\d+)", text)

    if not match:
        return None

    return match.group(1)

# =========================================================
# HELPERS
# =========================================================

def version_to_tuple(version):

    try:
        return tuple(map(int, version.split(".")))

    except:
        return (0, 0)


def kernel_in_range(kernel, min_v=None, max_v=None):

    kernel_t = version_to_tuple(kernel)

    if min_v:

        if kernel_t < version_to_tuple(min_v):
            return False

    if max_v:

        if kernel_t > version_to_tuple(max_v):
            return False

    return True

# =========================================================
# LOADER
# =========================================================

def load_exploits():

    exploits = []

    if not EXPLOIT_DIR.exists():
        return exploits

    for folder in EXPLOIT_DIR.iterdir():

        if not folder.is_dir():
            continue

        meta_path = folder / "meta.yaml"

        if not meta_path.exists():
            continue

        try:

            meta = yaml.safe_load(meta_path.read_text())

            if not meta:
                continue

            meta["folder"] = folder

            exploits.append(meta)

        except Exception:
            continue

    return exploits

# =========================================================
# MATCHER
# =========================================================

def exploit_matches(target, exploit):

    # -------------------------
    # DISTRO
    # -------------------------

    exploit_distros = exploit.get("distro", [])

    if exploit_distros:

        if target["distro"] not in exploit_distros:
            return False

    # -------------------------
    # KERNEL RANGE
    # -------------------------

    kernel = exploit.get("kernel", {})

    min_v = kernel.get("min")
    max_v = kernel.get("max")

    if not kernel_in_range(
        target["kernel"],
        min_v,
        max_v
    ):
        return False

    return True


def find_matches(target, exploits):

    matches = []

    for exploit in exploits:

        if exploit_matches(target, exploit):
            matches.append(exploit)

    return matches

# =========================================================
# CACHE / LOCAL
# =========================================================

def cache_path(exploit):

    cve = exploit.get("cve", "unknown")

    return CACHE_DIR / cve


def exploit_is_cached(exploit):

    return cache_path(exploit).exists()


def exploit_has_local_files(folder):

    for item in folder.iterdir():

        if item.name == "meta.yaml":
            continue

        return True

    return False

# =========================================================
# RENDER
# =========================================================

def render_target(target):

    print(f"\n{B}[*]{W} TARGET\n")

    print(f"  {G}├──{W} kernel:  {Y}{target['kernel']}{W}")
    print(f"  {G}├──{W} distro: {Y}{target['distro']}{W}")
    print(f"  {G}└──{W} version: {Y}{target['version']}{W}")


def render_matches(matches):

    print(f"\n{B}[*]{W} MATCHING EXPLOITS\n")

    for idx, exploit in enumerate(matches, start=1):

        name = exploit.get("name", "unknown")
        cve = exploit.get("cve", "unknown")

        if exploit_is_cached(exploit):
            status = f"{G}CACHED{W}"

        elif exploit_has_local_files(exploit["folder"]):
            status = f"{G}LOCAL{W}"

        else:
            status = f"{Y}REMOTE{W}"

        print(
            f"  [{idx}] "
            f"{W_BOLD}{name}{W} "
            f"({Y}{cve}{W}) "
            f"[{status}]"
        )


def render_metadata(exploit):

    compile_cmd = exploit.get("compile")
    run_cmd = exploit.get("run")
    notes = exploit.get("notes", [])
    source = exploit.get("source", {})

    print(f"\n{G}┌── EXPLOIT METADATA ─────────────────────────────────────┐{W}")

    if compile_cmd:
        print(f"{G}│{W} compile: {Y}{compile_cmd}{W}")

    if run_cmd:

        if isinstance(run_cmd, list):

            for cmd in run_cmd:
                print(f"{G}│{W} run:     {Y}{cmd}{W}")

        else:
            print(f"{G}│{W} run:     {Y}{run_cmd}{W}")

    github = source.get("github")

    if github:
        print(f"{G}│{W} source:  {C}{github}{W}")

    if notes:

        print(f"{G}│{W}")

        for note in notes:
            print(f"{G}│{W} note: {DIM}{note}{W}")

    print(f"{G}└──────────────────────────────────────────────────────────┘{W}")

# =========================================================
# STAGING
# =========================================================

def stage_folder(folder):

    copied = []

    for item in folder.iterdir():

        if not item.is_file():
            continue

        if item.name == "meta.yaml":
            continue

        destination = Path.cwd() / item.name

        shutil.copy(item, destination)

        copied.append(item.name)

    return copied


def stage_exploit(exploit):

    # -------------------------
    # CACHE
    # -------------------------

    cache = cache_path(exploit)

    if cache.exists():

        copied = stage_folder(cache)

        print(f"\n{G}[+]{W} staged from cache")

    # -------------------------
    # LOCAL
    # -------------------------

    elif exploit_has_local_files(exploit["folder"]):

        copied = stage_folder(exploit["folder"])

        print(f"\n{G}[+]{W} staged local exploit")

    # -------------------------
    # REMOTE
    # -------------------------

    else:

        source = exploit.get("source", {})
        github = source.get("github")

        if not github:

            print(f"\n{R}[!] No source available.{W}")
            return

        print(f"\n{B}[*]{W} downloading exploit")

        try:

            subprocess.run(
                [
                    "git",
                    "clone",
                    github,
                    str(cache)
                ],
                check=True
            )

        except Exception as e:

            print(f"\n{R}[!] download failed:{W} {e}")
            return

        copied = stage_folder(cache)

    # -------------------------
    # RENDER
    # -------------------------

    print(f"\n{B}[*]{W} STAGED FILES\n")

    for item in copied:
        print(f"  {G}├──{W} {item}")

    render_metadata(exploit)

# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(f"\n{W_BOLD}[*] KERNEL EXPLOIT MATCHER{W}\n")

    # -------------------------
    # KERNEL
    # -------------------------

    try:

        uname = input(f"{B}uname{W}> ").strip()

    except (KeyboardInterrupt, EOFError):
        print()
        return data

    kernel = parse_kernel(uname)

    if not kernel:

        print(f"\n{R}[!] Failed to parse kernel.{W}")
        return data

    # -------------------------
    # DISTRO
    # -------------------------

    try:

        os_release = input(f"{B}os-release{W}> ").strip()

    except (KeyboardInterrupt, EOFError):
        print()
        return data

    distro = parse_distro(os_release)
    version = parse_version(os_release)


    target = {
        "kernel": kernel,
        "distro": distro,
        "version": version
    }

    render_target(target)

    # -------------------------
    # LOAD
    # -------------------------

    exploits = load_exploits()

    if not exploits:

        print(f"\n{R}[!] No exploits loaded.{W}")
        return data

    # -------------------------
    # MATCH
    # -------------------------

    matches = find_matches(target, exploits)

    if not matches:

        print(f"\n{R}[!] No matching exploits found.{W}")
        return data

    render_matches(matches)

    # -------------------------
    # SELECT
    # -------------------------

    print()

    try:

        choice = input(f"{B}select{W}> ").strip()

    except (KeyboardInterrupt, EOFError):
        print()
        return data

    if not choice.isdigit():
        return data

    choice = int(choice)

    if choice < 1 or choice > len(matches):
        return data

    exploit = matches[choice - 1]

    stage_exploit(exploit)

    return data