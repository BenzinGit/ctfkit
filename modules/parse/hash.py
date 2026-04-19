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
                user = parts[0].split('\\')[-1] # Strip domain if present
                nthash = parts[3] # Index 3 is the NT Hash
                
                # Only return if the NT hash actually exists and isn't empty
                if len(nthash) == 32: 
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
    file = getattr(args, "file", None)
    if not file: return []

    path = Path(file).expanduser().resolve()
    if not path.exists(): return []

    found_creds = []
    for line in path.read_text().splitlines():
        parsed = parse_line(line)
        if parsed:
            found_creds.append(parsed)
    
    # Return the list instead of calling target_add_cred
    return found_creds