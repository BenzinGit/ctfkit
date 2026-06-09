import re
from pathlib import Path
from modules.crack.hashdb import HASH_TYPES


# =========================================================
# DETECTION
# =========================================================

def detect_hashes(path):
    """
    Return all matching hash candidates.
    """

    try:

        lines = Path(path).read_text(
            errors="ignore"
        ).splitlines()

        if not lines:
            return []

        sample = lines[0].strip()

    except Exception:
        return []

    matches = []

    for h in HASH_TYPES:

        try:

            if h["match"](sample):
                matches.append(h)

        except Exception:
            pass

    matches.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return matches


def detect_mode(path):
    """
    Return best matching mode.
    """

    matches = detect_hashes(path)

    if not matches:
        return None

    return matches[0]["mode"]


# =========================================================
# MODE HELPERS
# =========================================================

def resolve_mode(value):
    """
    Accept:
        NTLM
        nthash
        Kerberoast
        1000
        13100

    Return:
        Hashcat mode number
    """

    if value is None:
        return None

    value = str(value).strip()

    if value.isdigit():
        return value

    value_upper = value.upper()

    for h in HASH_TYPES:

        if value_upper == h["name"].upper():
            return h["mode"]

        for alias in h.get("aliases", []):

            if value_upper == alias.upper():
                return h["mode"]

    return None


def mode_name(mode):
    """
    Convert:
        1000 -> NTLM
        13100 -> Kerberoast
    """

    mode = str(mode)

    for h in HASH_TYPES:

        if h["mode"] == mode:
            return h["name"]

    return "Unknown"


def list_modes():
    """
    Return all supported modes.
    """

    return sorted(
        [
            {
                "name": h["name"],
                "mode": h["mode"],
            }
            for h in HASH_TYPES
        ],
        key=lambda x: x["name"]
    )


# =========================================================
# CLI MODULE
# =========================================================

def run(data, cred, args):

    G = "\033[92m"
    B = "\033[94m"
    W = "\033[0m"

    print(f"\n{G}[+] Supported Hash Modes{W}\n")

    for h in list_modes():

        print(
            f"  {B}├──{W} "
            f"{h['name']:<15} "
            f"{h['mode']}"
        )

    print()