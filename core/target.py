import json
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
CURRENT_FILE = PROFILES_DIR / "current"

PROFILES_DIR.mkdir(exist_ok=True)


# ---------------------- Helpers ----------------------

def get_profile_path(name):
    return PROFILES_DIR / f"{name}.json"


def load_current_name():
    if not CURRENT_FILE.exists():
        return None
    return CURRENT_FILE.read_text().strip()


def load_current_profile():
    name = load_current_name()
    if not name:
        raise Exception("No target selected")
    path = get_profile_path(name)
    if not path.exists():
        raise Exception("Current profile missing")
    return json.loads(path.read_text()), path


def save_profile(data, path):
    path.write_text(json.dumps(data, indent=2))


def resolve_cred_index(data, identifier):
    creds = data.get("creds", [])

    try:
        idx = int(identifier)
        if 0 <= idx < len(creds):
            return idx
        else:
            raise Exception("Invalid credential index")
    except ValueError:
        for i, c in enumerate(creds):
            if c.get("user") == identifier:
                return i
        raise Exception("User not found in credentials")


def get_active_cred(data, override=None):
    creds = get_all_creds(data)

    if not creds:
        raise Exception("No credentials available")

    if override is not None:
        try:
            idx = int(override)
            return creds[idx]
        except:
            for c in creds:
                if c.get("user") == override:
                    return c
        raise Exception("Credential not found")

    idx = data.get("current_cred")

    if idx is None:
        raise Exception("No active credential set")

    if idx >= len(creds):
        raise Exception("Invalid active credential")

    return creds[idx]

# ---------------------- Domain Helpers ----------------------

DOMAINS_DIR = BASE_DIR / "domains"
DOMAINS_DIR.mkdir(exist_ok=True)


def get_domain_path(name):
    return DOMAINS_DIR / f"{name}.json"


def load_domain(name):
    path = get_domain_path(name)

    if not path.exists():
        return None, path

    return json.loads(path.read_text()), path


def save_domain(data, path):
    path.write_text(json.dumps(data, indent=2))




# ---------------------- Target Commands ----------------------

def target_use(args):
    path = get_profile_path(args.name)

    if not path.exists():
        print("[!] Target does not exist")
        return

    CURRENT_FILE.write_text(args.name)
    print(f"[+] Using target {args.name}")



def target_create(args):
    path = get_profile_path(args.name)

    if path.exists():
        print("[!] Target already exists")
        return

    data = {
        "name": args.name.lower(),
        "ip": args.ip,
        "domain": args.domain.lower() if args.domain else None,
        "creds": [],
        "notes": [],
        "current_cred": None
    }

    save_profile(data, path)
    CURRENT_FILE.write_text(args.name)

    print(f"[+] Created and using target {args.name}")

    # ---------------- DOMAIN AUTO-CREATE ----------------
    if args.domain:
        domain_data, domain_path = load_domain(args.domain.lower())

        if not domain_data:
            domain_data = {
                "name": args.domain.lower(),
                "dc": None,
                "creds": [],
                "notes": []
            }

            save_domain(domain_data, get_domain_path(args.domain))
            print(f"[+] Auto-created domain {args.domain}")

def target_add_domain(args):
    try:
        data, path = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    domain_name = args.domain.lower()

    # set domain on target
    data["domain"] = domain_name
    save_profile(data, path)

    print(f"[+] Set domain for target to {domain_name}")

    domain_data, domain_path = load_domain(domain_name)

    if not domain_data:
        domain_data = {
            "name": domain_name.lower(),
            "dc": None,
            "creds": [],
            "notes": []
        }

        save_domain(domain_data, get_domain_path(domain_name))
        print(f"[+] Auto-created domain {domain_name}")



def target_list(args):
    for f in PROFILES_DIR.glob("*.json"):
        print(f.stem)


def target_show(args):
    try:
        data, _ = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    print(f"Name: {data['name']}")
    print(f"IP: {data['ip']}")
    print(f"Domain: {data['domain']}")

    all_creds = get_all_creds(data)
    active_idx = data.get("current_cred")

    print_creds_table(all_creds, active_idx)





def target_add_cred(args):
    try:
        data, path = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    # ---------------- DETERMINE TYPE ----------------
    if args.hash:
        cred_type = "ntlm"
        secret = args.hash

    elif args.aes:
        cred_type = "aes"
        secret = args.aes

    elif args.ccache:
        cred_type = "ticket"
        secret = args.ccache

    elif args.password:
        cred_type = "password"
        secret = args.password

    else:
        print("[!] You must provide password or --hash/--aes/--ccache")
        return

    # ---------------- BUILD CRED ----------------
    new_cred = {
        "user": args.user,
        "type": cred_type
    }

    if cred_type == "ticket":
        new_cred["ccache"] = secret
    else:
        new_cred["secret"] = secret

    # ---------------- SAVE LOCAL ----------------
    data["creds"].append(new_cred)
    data["current_cred"] = len(get_all_creds(data)) - 1

    save_profile(data, path)

    print(f"[+] Added {cred_type} credential for {args.user}")

    # ---------------- DOMAIN SYNC ----------------
    domain_name = data.get("domain")

    if domain_name:
        domain_data, domain_path = load_domain(domain_name)

        if domain_data:
            exists = any(
                c.get("user") == args.user and
                c.get("type") == cred_type and
                (
                    c.get("secret") == secret or
                    c.get("ccache") == secret
                )
                for c in domain_data.get("creds", [])
            )

            if not exists:
                domain_data["creds"].append(new_cred)
                save_domain(domain_data, domain_path)
                print(f"[+] Synced to domain")
            else:
                print("[*] Credential already exists in domain")

    target_creds(argparse.Namespace(local=False, domain=False))


def target_set_cred(args):
    try:
        data, path = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    creds = get_all_creds(data)

    if not creds:
        print("[!] No credentials available")
        return

    identifier = args.identifier

    # try index
    try:
        idx = int(identifier)
        if idx < 0 or idx >= len(creds):
            raise Exception
    except:
        # fallback: username
        matches = [i for i, c in enumerate(creds) if c["user"] == identifier]

        if not matches:
            print("[!] Credential not found")
            return

        idx = matches[0]

    data["current_cred"] = idx
    save_profile(data, path)

    c = creds[idx]
    typ = c.get("type", "unknown")
    source = c.get("source", "local")

    source_str = "Domain" if source == "domain" else "Local"

    print(f"[+] Active credential set to [{idx}] {c['user']} ({typ}, {source_str})")


def target_creds(args):
    try:
        data, _ = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    all_creds = get_all_creds(data)
    active_idx = data.get("current_cred")

    # filtering
    if getattr(args, "local", False):
        creds = [c for c in all_creds if c["source"] == "local"]

    elif getattr(args, "domain", False):
        # domain = everything usable in domain (local + domain)
        creds = all_creds

    else:
        # default = same as domain view
        creds = all_creds

    if not creds:
        print("[!] No credentials found")
        return

    print_creds_table(creds, active_idx)

def print_creds_table(creds, active_idx):
    if not creds:
        print("[!] No credentials found")
        return

    print("\nID  User          Type      Secret")
    print("--  ------------  --------  ------------------")

    for display_idx, c in enumerate(creds):
        marker = "[*]" if c["index"] == active_idx else "   "

        user = c.get("user", "")
        typ = c.get("type", "")
        secret = c.get("secret", "")

        print(f"{marker} {display_idx:<2} {user:<12} {typ:<8} {secret}")

def get_all_creds(data):
    combined = []
    seen = set()

    def make_key(c):
        return (
            c.get("user"),
            c.get("type"),
            c.get("secret") or c.get("ccache")
        )

    # local
    for c in data.get("creds", []):
        key = make_key(c)
        if key in seen:
            continue
        seen.add(key)

        combined.append({
            "user": c["user"],
            "type": c["type"],
            "secret": c.get("secret") or c.get("ccache"),
            "source": "local",
            "index": len(combined)
        })

    # domain
    domain_name = data.get("domain")
    if domain_name:
        domain_data, _ = load_domain(domain_name)
        if domain_data:
            for c in domain_data.get("creds", []):
                key = make_key(c)
                if key in seen:
                    continue
                seen.add(key)

                combined.append({
                    "user": c["user"],
                    "type": c["type"],
                    "secret": c.get("secret") or c.get("ccache"),
                    "source": "domain",
                    "index": len(combined)
                })

    return combined




def target_whoami(args):
    try:
        data, _ = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    try:
        cred = get_active_cred(data)
    except Exception as e:
        print(f"[!] {e}")
        return

    user = cred["user"]
    typ = cred.get("type", "unknown")
    secret = cred.get("secret", "N/A")
    source = cred.get("source", "local")

    host = data.get("name")
    ip = data.get("ip")
    domain = data.get("domain") or "N/A"

    source = cred.get("source", "local")
    source_str = "Domain" if source == "domain" else "Local"

    # short mode
    if getattr(args, "short", False):
        print(f"{user}@{host}")
        return

    # table mode
    if getattr(args, "table", False):
        print("\n[*] Current Credential:\n")
        print(" ID  User           Auth      Secret")
        print(" --  -------------  --------  ------------------")
        print(f"[*] 0   {user:<13} {typ:<8} {secret}")
        return


    print(f"User:     {user}")
    print(f"Auth:     {typ} ({source_str})\n")

    print(f"Host:     {host} ({ip})")
    print(f"Domain:   {domain}\n")

    print(f"Secret:   {secret}")

