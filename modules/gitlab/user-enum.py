def run(data, cred, args):
    import requests
    from pathlib import Path
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from core.target import get_current_url
    from core.paths import get_artifact

    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- CONFIG ----------------
    target = get_current_url(data)
    default_list = "/usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt"

    userlist = getattr(args, "file", None) or default_list
    userlist = Path(userlist).expanduser().resolve()

    out_file = get_artifact(data["name"], "gitlab_users.txt")

    # ---------------- VALIDATION ----------------
    if not target:
        print(f"{R}[!] {W}No target URL found")
        return data

    if not userlist.exists():
        print(f"{R}[!] {W}Userlist not found: {userlist}")
        return data

    # ---------------- NORMALIZE ----------------
    if not target.startswith("http"):
        target = f"http://{target}"

    if ":" not in target.split("//")[1]:
        target = f"{target}:8081"

    base = target.rstrip("/")

    # ---------------- LOAD USERS ----------------
    usernames = [u.strip() for u in userlist.read_text().splitlines() if u.strip()]

    # ---------------- HUD ----------------
    print(f"\n{B}┌── {BOLD}MODULE: GITLAB USER ENUM{W}{B} ─────────────────────┐{W}")
    print(f"{B}│{W}  {B}{'Target:':<12}{W} {C}{base:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'Wordlist:':<12}{W} {W}{userlist.name:<36}{W} {B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {DIM}Enumerating users (threaded)...{W}\n")

    # ---------------- WORKER ----------------
    session = requests.Session()

    def check_user(user):
        try:
            r = session.get(
                f"{base}/{user}",
                allow_redirects=False,   # 🔥 critical fix
                timeout=5
            )

            if r.status_code == 200:
                return user

        except:
            return None

        return None

    # ---------------- THREADING ----------------
    valid = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_user, u): u for u in usernames}

        for future in as_completed(futures):
            result = future.result()
            if result:
                valid.append(result)
                print(f"{G}[+] Found:{W} {result}")

    # ---------------- SAVE ----------------
    if not valid:
        print(f"\n{Y}[!] {W}No valid users found\n")
        return data

    out_file.write_text("\n".join(valid) + "\n")

    # ---------------- SUCCESS ----------------
    print(f"\n{G}┌── RESULTS ─────────────────────────────────────────────┐{W}")
    print(f"{G}│{W}  {B}Users Found:{W} {G}{len(valid):<33}{W} {G}│{W}")
    print(f"{G}│{W}  {B}Saved To:{W}   {Y}{str(out_file):<33}{W} {G}│{W}")
    print(f"{G}└────────────────────────────────────────────────────────┘{W}\n")

    return data