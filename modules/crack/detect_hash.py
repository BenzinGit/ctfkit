def detect_mode(path):
    import re

    try:
        lines = path.read_text().splitlines()
        if not lines:
            return None
        sample = lines[0]
    except Exception:
        return None

    if "$krb5asrep$" in sample:
        return "18200"

    if "$krb5tgs$" in sample:
        return "13100"

    if "::" in sample:
        return "5600"

    if re.fullmatch(r"[a-fA-F0-9]{32}", sample):
        return "1000"

    return None


def run(data, cred, args):
    from pathlib import Path

    file = getattr(args, "file", None)

    # fallback to positional
    if not file and hasattr(args, "extra") and args.extra:
        file = args.extra[0]

    if not file:
        print("[!] Missing --file")
        return

    path = Path(file).expanduser().resolve()

    if not path.exists():
        print(f"[!] File not found: {path}")
        return

    mode = detect_mode(path)

    if not mode:
        print("[!] Could not detect hash type")
        return

    print(f"[+] Detected mode: {mode}")