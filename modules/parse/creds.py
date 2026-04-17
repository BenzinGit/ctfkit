def parse_line(line):
    try:
        # AS-REP
        if "$krb5asrep$" in line:
            hash_part, password = line.rsplit(":", 1)
            user = hash_part.split("$")[3].split("@")[0]
            return {"user": user, "type": "password", "secret": password}

        # Kerberoast
        if "$krb5tgs$" in line:
            hash_part, password = line.rsplit(":", 1)
            user = hash_part.split("$")[3].split("@")[0]
            user = user.lstrip("*")  
            return {"user": user, "type": "password", "secret": password}

        # NetNTLMv2
        if "::" in line:
            user = line.split("::")[0]
            password = line.rsplit(":", 1)[1]
            return {"user": user, "type": "password", "secret": password}

        # Fallback: user:pass
        if ":" in line:
            user, password = line.split(":", 1)
            return {"user": user, "type": "password", "secret": password}

    except Exception:
        return None

    return None

def run(data, cred, args):
    from pathlib import Path
    import argparse
    from core import target

    file = getattr(args, "file", None)

    if not file:
        print("[!] Missing --file")
        return

    path = Path(file).expanduser().resolve()

    if not path.exists():
        print(f"[!] File not found: {path}")
        return

    lines = path.read_text().splitlines()

    if not lines:
        print("[!] No credentials found")
        return

    print("[*] Parsing credentials...\n")

    added = 0

    for line in lines:
        parsed = parse_line(line)

        if not parsed:
            print(f"[!] Skipping: {line}")
            continue

        user = parsed["user"]
        typ = parsed["type"]
        secret = parsed["secret"]

        print(f"[+] {user} ({typ}): {secret}")

        target.target_add_cred(
            argparse.Namespace(
                user=user,
                password=secret if typ == "password" else None,
                hash=secret if typ == "ntlm" else None,
                aes=None,
                ccache=None
            )
        )

        added += 1