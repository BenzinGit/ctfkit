def parse_line(line):
    try:
        if not line or line.startswith("["):
            return None

        # -------------------
        # 1. DCSync (MOST SPECIFIC)
        # -------------------
        if ":::" in line:
            parts = line.split(":")

            if len(parts) >= 4:
                user = parts[0]
                rid = parts[1]
                nthash = parts[3]

                if rid.isdigit():
                    if nthash and nthash != "aad3b435b51404eeaad3b435b51404ee":
                        return {"user": user, "type": "ntlm", "secret": nthash}

        # -------------------
        # 2. AS-REP
        # -------------------
        if "$krb5asrep$" in line:
            hash_part, password = line.rsplit(":", 1)
            user = hash_part.split("$")[3].split("@")[0]
            return {"user": user, "type": "password", "secret": password}

        # -------------------
        # 3. Kerberoast
        # -------------------
        if "$krb5tgs$" in line:
            hash_part, password = line.rsplit(":", 1)
            user = hash_part.split("$")[3].split("@")[0].lstrip("*")
            return {"user": user, "type": "password", "secret": password}

        # -------------------
        # 4. NetNTLMv2
        # -------------------
        if "::" in line and "$" not in line:
            user = line.split("::")[0]
            password = line.rsplit(":", 1)[1]
            return {"user": user, "type": "password", "secret": password}

        # -------------------
        # 5. Fallback (VERY strict)
        # -------------------
        if line.count(":") == 1:
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