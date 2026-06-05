import re
from pathlib import Path


HASH_TYPES = [
    {
        "name": "ASREP",
        "mode": "18200",
        "confidence": 100,
        "match": lambda s: "$krb5asrep$" in s,
    },
    {
        "name": "Kerberoast",
        "mode": "13100",
        "confidence": 100,
        "match": lambda s: "$krb5tgs$" in s,
    },
    {
        "name": "NetNTLMv2",
        "mode": "5600",
        "confidence": 95,
        "match": lambda s: "::" in s,
    },
    {
        "name": "NTLM",
        "mode": "1000",
        "confidence": 60,
        "match": lambda s: re.fullmatch(r"[a-fA-F0-9]{32}", s),
    },
    {
        "name": "MD5",
        "mode": "0",
        "confidence": 40,
        "match": lambda s: re.fullmatch(r"[a-fA-F0-9]{32}", s),
    },
]


def detect_hashes(path):
    try:
        lines = Path(path).read_text(errors="ignore").splitlines()

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

    matches.sort(key=lambda x: x["confidence"], reverse=True)

    return matches


def detect_mode(path):
    matches = detect_hashes(path)

    if not matches:
        return None

    return matches[0]["mode"]


def run(data, cred, args):
    from pathlib import Path

    file = getattr(args, "file", None)

    # positional fallback
    if not file and hasattr(args, "extra") and args.extra:
        file = args.extra[0]

    if not file:
        print("[!] Missing --file")
        return

    path = Path(file).expanduser().resolve()

    if not path.exists():
        print(f"[!] File not found: {path}")
        return

    matches = detect_hashes(path)

    if not matches:
        print("[!] Could not detect hash type")
        return

    print("\n[+] Candidate Hash Types:\n")

    for h in matches:
        print(
            f"  - {h['name']:<15} "
            f"Mode: {h['mode']:<8} "
            f"Confidence: {h['confidence']}%"
        )

    print()