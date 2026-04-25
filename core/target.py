import json
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
CURRENT_FILE = PROFILES_DIR / "current"

PROFILES_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)

G, C, B, W = '\033[92m', '\033[96m', '\033[94m', '\033[0m'
BOLD, DIM = '\033[1m', '\033[2m'
Y, R = '\033[93m', '\033[91m'

# ---------------------- Helpers ----------------------

def rel(path):
    try:
        return path.relative_to(BASE_DIR)
    except ValueError:
        return path  


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

 


# ---------------------- Target Commands ----------------------

def target_use(args):
    path = get_profile_path(args.name)

    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'

    if not path.exists():
        # Using RED for Failure Header, BLUE for tree
        print(f"\n{R}[!] {W}{BOLD}MOUNT FAILED{W}")
        print(f"{B}  └── {B}Error:{W} Target {C}'{args.name}'{W} not found in artifacts.")
        return

    CURRENT_FILE.write_text(args.name)
    
    # Using BOLD WHITE for Header, BLUE for tree, GREEN for success values
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}TARGET SELECTION{W}")
    print(f"{B}  └── {B}Active Target:{W} {C}{args.name}{W}")



def target_create(args):
    path = get_profile_path(args.name)
    url = getattr(args, "url", None)

    if path.exists():
        # Using RED for Aborted, Blue for structure, Yellow for commands
        print(f"\n{R}[!] {W}{BOLD}DEPLOYMENT ABORTED{W}")
        print(f"{B}  ├── {B}Error:{W}  Target {C}'{args.name}'{W} already exists.")
        print(f"{B}  └── {B}Hint:{W}   Use {Y}ctf use {args.name}{W} to switch context.\n")
        return

    data = {
        "name": args.name.lower(),
        "ip": args.ip,
        "domain": args.domain.lower() if args.domain else None,
        "creds": [],
        "notes": [],
        "current_cred": None,
        "hostname": None,
        "urls": [url] if url else [],
        "current_url": 0 if url else None,
    }

    save_profile(data, path)
    CURRENT_FILE.write_text(args.name)

    


    # Standard Phase Header
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}TARGET CREATED{W}")
    print(f"{B}  ├── {B}Name:{W}    {C}{args.name}{W}")
    print(f"{B}  ├── {B}IP:{W}      {C}{args.ip}{W}")

    if args.domain:
        print(f"{B}  ├── {B}Domain:{W}  {C}{args.domain.lower()}{W}")
    else:
        print(f"{B}  ├── {B}Domain:{W}  None{W}")

    if url:
        print(f"{B}  └── {B}URL:{W}     {C}{url}{W}")
    else:
        print(f"{B}  └── {B}URL:{W}     None{W}")

    print(f"\n{G}┌── CONTEXT CHANGED ───────────────────────────────────────┐{W}")
    print(f"{G}│{W}  Target context has been set to: {C}{args.name:<24}{W}{G}│{W}")
    print(f"{G}└──────────────────────────────────────────────────────────┘{W}\n")


def target_delete(args):
    import shutil
    import json

    name = args.name or load_current_name()

    if not name:
        print(f"\n{R}[!] {W}{BOLD}ACTION DENIED{W}")
        print(f"{R}  └── {W}No target specified and no current session active.")
        return

    name = name.lower()
    profile_path = get_profile_path(name)

    if not profile_path.exists():
        print(f"\n{R}[!] {W}{BOLD}TARGET NOT FOUND{W}")
        print(f"{R}  └── {W}The profile {R}'{name}'{W} does not exist in the database.")
        return

    # Load for metadata
    data = json.loads(profile_path.read_text())
    artifact_path = ARTIFACTS_DIR / name

    # --- DESTRUCTION HEADER ---
    print(f"\n{R}┌── {BOLD}DESTRUCTION WARNING{W} ─────────────────────────────────────┐")
    print(f"{R}│{W}  You are about to purge target: {BOLD}{name.upper()}{W}")
    print(f"{R}│{W}  The following data will be permanently removed:   ")
    print(f"{R}│{W}  {B}•{W} Profile:   {rel(profile_path)}")
    print(f"{R}│{W}  {B}•{W} Artifacts: {rel(artifact_path)}")
    print(f"{R}└─────────────────────────────────────────────────────────────┘")

    if not getattr(args, "force", False):
        confirm = input(f"\n    {R}{BOLD}![?]{W} Type {R}'yes'{W} to confirm wipe: ")
        if confirm.lower() != "yes":
            print(f"\n{B}[{G}*{B}]{W} Operation {G}aborted{W}. Data preserved.")
            return

    # ---------------- EXECUTION ----------------
    print(f"\n{Y}[*] Initiating purge sequence...{W}")

    # Delete Profile
    if profile_path.exists():
        profile_path.unlink()
        print(f"{Y}  ├── {Y}Database:{W}  {R}DELETED{W}")
    else:
        print(f"{Y}  ├── {Y}Database:{W}  {DIM}Not Found (Skipped){W}")

    # Delete Artifacts
    if artifact_path.exists():
        shutil.rmtree(artifact_path)
        print(f"{Y}  ├── {Y}Artifacts:{W} {R}WIPED{W}")
    else:
        print(f"{Y}  ├── {Y}Artifacts:{W} {DIM}Not Found{W}")

    # Handle Current Context
    current = load_current_name()
    if current == name:
        CURRENT_FILE.unlink(missing_ok=True)
        print(f"{Y}  └── {Y}Context:{W}   {R}CLEARED{W}")
    else:
        print(f"{Y}  └── {Y}Context:{W}   {G}STABLE{W}")

    

def target_list(args):
    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    profiles = list(PROFILES_DIR.glob("*.json"))
    current = load_current_name()

    # --- HEADER ---
    print(f"\n{B}┌── {BOLD}TARGET DIRECTORY{W}{B} ──────────────────────────────────────┐{W}")
    
    if not profiles:
        print(f"{B}│{W}  {Y}[!] No targets found. Run: {W}{BOLD}ctf create <name>{W}    {B}│{W}")
    else:
        for f in sorted(profiles):
            name = f.stem
            is_active = (name == current)
            
            # 1. Indicator Logic
            # Active gets the Green Pointer, inactive gets a Dim Blue Pipe
            marker = f"{G}▶{W}" if is_active else f"{B}│{W}"
            
            # 2. Status Label
            # Labels (Status:) stay Blue, Values (READY/ACTIVE) get Green/Cyan
            if is_active:
                status_label = f"{G}ACTIVE{W}"
                display_name = f"{BOLD}{C}{name.upper():<20}{W}"
            else:
                status_label = f"{B}READY {W}"
                display_name = f"{W}{name:<20}{W}"
            
            # 3. Row Construction
            # Using the Blue Pipe character to keep the box edges solid
            print(f"{B}│{W}  {marker} {status_label}  {display_name}  {B}│{W}")

    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")
    
    # --- SUMMARY FOOTER ---
    count = len(profiles)
    print(f"  {B}└──{W} {BOLD}Total Targets:{W} {G}{count}{W}\n")


def target_show(args):
    # --- ANSI PALETTE ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    try:
        data, _ = load_current_profile()
    except:
        print(f"\n{R}[!] {W}No active profile loaded.")
        return

    name = data.get("name", "UNKNOWN").upper()

    # ---------------- GENERAL FIELDS ----------------
    fields = {
        "Hostname": data.get("hostname"),
        "IP Address": data.get("ip"),
        "Domain": data.get("domain"),
        "OS Version": data.get("os"),
        "Role": data.get("role"),
    }

    # ---------------- HEADER ----------------
    print(f"\n{B}┌── {BOLD}TARGET INFO: {C}{name}{W}{B} ────────────────────────────────┐{W}")

    # ---------------- GENERAL INFO ----------------
    for label, val in fields.items():
        if val:
            display_val = f"{C}{val:<36}{W}"
        else:
            display_val = f"{DIM}{'N/A':<36}{W}"

        print(f"{B}│{W}  {B}{label+':':<14}{W} {display_val} {B}│{W}")

    print(f"{B}└──────────────────────────────────────────────────────┘{W}")

    urls = data.get("urls", [])

    if urls:
        print_urls_table(data)
    

    # ---------------- NOTES SECTION ----------------
    notes = data.get("notes", [])

    if notes:
        print(f"\n{B}┌── {BOLD}NOTES{W}{B} ─────────────────────────────────────────────┐{W}")

        for n in notes:
            print(f"{B}│{W}  {W}{n:<46}{W} {B}│{W}")

        print(f"{B}└──────────────────────────────────────────────────────────┘{W}")


    # ---------------- CREDS ----------------
    all_creds = get_all_creds(data)

    if all_creds:
        print_creds_table(all_creds, data.get("current_cred"))
    else:
        print(f"\n  {B}└──{W} {DIM}No credentials stored in profile.{W}\n")





def target_add_cred(args, switch=True, show=True):
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
        print(f"\n{R}[!] {W}{BOLD}INCOMPLETE AUTHENTICATION DATA{W}")
        print(f"{R}  ├── {R}Error:{W}   You must provide at least one secret provider.")
        print(f"{R}  ├── {R}Options:{W} {Y}password{W}, {Y}--hash{W}, {Y}--aes{W}, or {Y}--ccache{W}")
        print(f"{R}  └── {R}Usage:{W}   {C}ctf target add-cred <user> [secret]{W}\n")
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


    save_profile(data, path)


    
    
    # ---------------- OPTIONAL SWITCH ----------------
    if switch:
        target_set_cred(argparse.Namespace(identifier=args.user))

    # ---------------- OPTIONAL DISPLAY ----------------
    if show:
        pass
    

def target_set_cred(args):


    try:
        data, path = load_current_profile()
    except Exception as e:
        print(f"\n{R}[!] {W}{BOLD}FS ERROR{W}\n{R}  └── {R}Error:{W} {e}")
        return

    creds = get_all_creds(data)

    if not creds:
        print(f"\n{R}[!] {W}{BOLD}AUTH ERROR{W}\n{R}  └── {R}Status:{W} No credentials available for this target.")
        return

    identifier = args.identifier

    # try index
    try:
        idx = int(identifier)
        if idx < 0 or idx >= len(creds):
            raise Exception
    except:
        # fallback: username match
        matches = [i for i, c in enumerate(creds) if c["user"] == identifier]

        if not matches:
            print(f"\n{R}[!] {W}{BOLD}QUERY FAILURE{W}")
            print(f"{R}  ├── {R}Search Term:{W} {Y}'{identifier}'{W}")
            print(f"{R}  ├── {R}Status:{W}      No matching credential found.")
            print(f"{R}  └── {R}Hint:{W}        Use {Y}ctf creds{W} to list identities.\n")
            return

        # Use most recently added match
        idx = matches[-1] 

    data["current_cred"] = idx
    save_profile(data, path)

    # UI Output Data
    c = creds[idx]
    user = c.get('user', 'Unknown')
    typ = c.get("type", "Unknown")
    secret = c.get("secret", "N/A")

    # --- SUCCESS HUD ---
    print(f"\n{B}[{W}{G}*{W}{B}]{W} {BOLD}CREDENTIAL CONTEXT SET{W}")

    all_creds = get_all_creds(data)
    if all_creds:
        print_creds_table(all_creds, data.get("current_cred"))

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
        print(f"\n{Y}[!] {W}{BOLD}DATABASE EMPTY{W}")
        print(f"{R}  └── {R}Status:{W}  No credentials stored for this target.")
        return

    print_creds_table(creds, active_idx)

def print_creds_table(creds, active_idx):
    # --- ANSI PALETTE ---
    ORANGE = '\033[38;5;208m'  # Punchy, aggressive orange
    AMBER  = '\033[38;5;172m'  # Dark yellow / Gold
    DKBLUE = '\033[38;5;75m'   # Deep, professional navy
    GREY   = '\033[38;5;244m'  # Tactical medium grey
    DKGREY = '\033[38;5;239m'  # Very dim grey (good for borders)

    if not creds:
        print(f"\n{B}  └── {Y}[!] No credentials found.{W}")
        return

    # 1. Calculate Widths
    # Note: id_w is the width of the ID number column
    id_w = max(len(str(len(creds))), 2)
    u_w  = max(max(len(str(c.get("user", ""))) for c in creds), 12)
    t_w  = max(max(len(str(c.get("type", ""))) for c in creds), 8)
    s_w  = max(max(len(str(c.get("secret") or "N/A")) for c in creds), 20)

    # 2. Build the Header String (Matching the data row spacing exactly)
    # [Space][Space][Space][ID][Space][Space][User]...
    # We use 3 spaces at start to account for the marker column (▶ + space)
    header_text = f"   {'ID':<{id_w}}  {'User':<{u_w}}  {'Type':<{t_w}}  {'Secret':<{s_w}}"
    
    # Calculate box width based on the header text length
    total_w = len(header_text) + 2

    # 3. Print the Box
    print(f"\n{B}┌── IDENTITIES {'─' * (total_w - 14)}┐{W}")
    print(f"{B}│{W} {BOLD}{header_text} {B}│{W}")
    print(f"{B}├{'─' * (total_w)}┤{W}")

    # 4. Rows
    for i, c in enumerate(creds):
        is_active = (c["index"] == active_idx)
        
        # Indicator: Green pointer or empty spaces
        marker = f"{G}▶{W}" if is_active else " "
        
        # Format values as plain strings first for padding, then add color
        user_str = c.get('user', '')
        type_str = c.get('type', '')
        sec_str  = str(c.get('secret') or 'N/A')

        # Construct Row: [marker] [id] [user] [type] [secret]
        # Spacing: 1 space after marker, 2 spaces between every other column
        id_part = f"{(BOLD+G if is_active else GREY)}{str(i):<{id_w}}{W}"

        user_part = f"{(BOLD+W if is_active else GREY)}{user_str:<{u_w}}{W}"
        type_part = f"{(BOLD+B if is_active else GREY)}{type_str:<{t_w}}{W}"
        sec_part = f"{(BOLD+Y if is_active else GREY)}{sec_str:<{s_w}}{W}"

        print(f"{B}│{W}  {marker} {id_part}  {user_part}  {type_part}  {sec_part} {B}│{W}")

    print(f"{B}└{'─' * (total_w)}┘{W}")
    
    # Summary Footer
    count = len(creds)
    print(f"  {B}└──{W} {BOLD}Total Identities:{W} {G}{count}{W}\n")

def get_all_creds(data):
    combined = []

    for i, c in enumerate(data.get("creds", [])):
        combined.append({
            "user": c["user"],
            "type": c["type"],
            "secret": c.get("secret") or c.get("ccache"),
            "source": "local",
            "index": i
        })

    return combined

def print_urls_table(data):
    # --- ANSI PALETTE ---
    G, C, B, Y, W = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m'
    BOLD, DIM = '\033[1m', '\033[2m'
    GREY = '\033[38;5;244m'

    urls = data.get("urls", [])
    active_idx = data.get("current_url")

    if not urls:
        print(f"\n{B}  └── {DIM}No URLs found.{W}")
        return

    # ---------------- WIDTHS ----------------
    id_w = max(len(str(len(urls))), 2)
    url_w = max(max(len(u) for u in urls), 30)

    # ---------------- HEADER ----------------
    header_text = f"   {'ID':<{id_w}}  {'URL':<{url_w}}"
    total_w = len(header_text) + 2

    print(f"\n{B}┌── TARGET URLS {'─' * (total_w - 15)}┐{W}")
    print(f"{B}│{W} {BOLD}{header_text} {B}│{W}")
    print(f"{B}├{'─' * (total_w)}┤{W}")

    # ---------------- ROWS ----------------
    for i, url in enumerate(urls):
        is_active = (i == active_idx)

        marker = f"{G}▶{W}" if is_active else " "

        id_part = f"{(BOLD+G if is_active else GREY)}{str(i):<{id_w}}{W}"
        url_part = f"{(BOLD+C if is_active else GREY)}{url:<{url_w}}{W}"

        print(f"{B}│{W}  {marker} {id_part}  {url_part} {B}│{W}")

    print(f"{B}└{'─' * (total_w)}┘{W}")

    # ---------------- FOOTER ----------------
    print(f"  {B}└──{W} {BOLD}Total URLs:{W} {G}{len(urls)}{W}\n")


def target_whoami(args):
    # --- CORE PALETTE ONLY ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    try:
        data, _ = load_current_profile()
        cred = get_active_cred(data) # Assumes helper to get active dict
    except:
        print(f"\n{R}[!] {W}{BOLD}IDENTITY ERROR{W}")
        return

    # Data Parsing
    user   = cred.get("user", "N/A")
    typ    = cred.get("type", "password").capitalize()
    secret = str(cred.get("secret") or "N/A")
    host   = data.get("hostname") or "N/A"
    ip     = data.get("ip") or "N/A"
    domain = data.get("domain") or "N/A"

    # Box Width to match your Mission Brief
    width = 54

    print(f"\n{B}┌── ACTIVE SESSION: ───────────────────────────────────┐{W}")
    
    # 1. Identity Section
    print(f"{B}│{W}  {B}{'Username:':<14}{W} {W}{BOLD}{user:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{typ + ':':<14}{W} {Y}{BOLD}{secret:<36}{W} {B}│{W}")
    
    # 2. Context Divider
    print(f"{B}├── TARGET CONTEXT ────────────────────────────────────┤{W}")
    
    # 3. Target Section
    print(f"{B}│{W}  {B}{'Hostname:':<14}{W} {C}{host:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'IP Address:':<14}{W} {C}{ip:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'Domain:':<14}{W} {B}{domain:<36}{W} {B}│{W}")
    
    print(f"{B}└──────────────────────────────────────────────────────┘{W}\n")


def target_set_url(args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'

    try:
        data, path = load_current_profile()
    except:
        print(f"{R}[!] No active target{W}")
        return

    idx = args.index
    urls = data.get("urls", [])

    if idx < 0 or idx >= len(urls):
        print(f"{R}[!] Invalid index{W}")
        return

    data["current_url"] = idx
    save_profile(data, path)

    print(f"{G}[+] Active URL set:{W} {C}{urls[idx]}{W}")


def target_add_url(args):
    # --- ANSI ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'

    try:
        data, path = load_current_profile()
    except:
        print(f"\n{R}[!] {W}No active target selected.")
        return

    url = args.url.strip()

    if not url:
        print(f"{R}[!] Invalid URL")
        return

    # init if missing (backward compatibility)
    if "urls" not in data:
        data["urls"] = []

    if "current_url" not in data:
        data["current_url"] = None

    # prevent duplicates
    if url in data["urls"]:
        print(f"{Y}[!] URL already exists:{W} {C}{url}{W}")
        return

    data["urls"].append(url)

    # set as active
    data["current_url"] = len(data["urls"]) - 1

    save_profile(data, path)

    print(f"\n{G}[+] URL added{W}")
    print(f"{B}  ├── {B}URL:{W}     {C}{url}{W}")
    print(f"{B}  └── {B}Active:{W}  index {data['current_url']}")    



def get_current_url(data):
    urls = data.get("urls", [])
    idx = data.get("current_url")

    if not urls:
        return None

    # fallback safety
    if idx is None or idx >= len(urls):
        return urls[0]

    return urls[idx]