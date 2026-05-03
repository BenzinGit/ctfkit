def run(data, cred, args):
    import subprocess
    from pathlib import Path
    from core.paths import get_artifacts_dir
    from core.target import get_current_url
    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD, DIM = '\033[1m', '\033[2m'

    # ---------------- HELPERS ----------------
    def resolve_wordlist(path):
        if not path:
            # default wordlist
            return Path("/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")

        p = Path(path).expanduser().resolve()
        if not p.exists():
            print(f"\n{R}[!] WORDLIST NOT FOUND{W}")
            print(f"{B}  └── {W}{p}")
            return None
        return p

    # ---------------- INPUT ----------------
    url = get_current_url(data)
    if getattr(args, "url", None):
        url = args.url

    if not url:
        print(f"\n{R}[!] NO URL SET{W}")
        print(f"{B}  └── Use: {C}ctf target add-url <url>{W}")
        return

    wordlist = resolve_wordlist(getattr(args, "wordlist", None))
    if not wordlist:
        return

    threads = getattr(args, "threads", 50)
    extensions = getattr(args, "ext", None)

    # ---------------- OUTPUT ----------------
    target_name = data.get("name", "unknown")
    out_dir = get_artifacts_dir(target_name) / "gobuster"
    out_dir.mkdir(parents=True, exist_ok=True)

    output_file = Path(getattr(args, "out", None) or out_dir / "dirs.txt")

    # ---------------- HUD ----------------
    print(f"\n{B}┌── {BOLD}MODULE: GOBUSTER DIR ENUM{W}{B} ─────────────────────────────┐{W}")
    print(f"{B}│{W}  {B}{'URL:':<12}{W} {C}{url:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'Wordlist:':<12}{W} {W}{wordlist.name:<36}{W} {B}│{W}")
    print(f"{B}│{W}  {B}{'Threads:':<12}{W} {Y}{threads:<36}{W} {B}│{W}")

    if extensions:
        print(f"{B}│{W}  {B}{'Extensions:':<12}{W} {W}{extensions:<36}{W} {B}│{W}")

    print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

    # ---------------- COMMAND ----------------
    cmd = [
        "gobuster",
        "dir",
        "-u", url,
        "-w", str(wordlist),
        "-t", str(threads),
        "-o", str(output_file) 
       ]
    import shlex
    if extensions:
        cmd += ["-x", extensions]

    import shlex
    # ---------------- EXECUTION ----------------
    print(f"{B}[*] Running:{Y} {shlex.join(cmd)}{W}\n")
    found = run_live(cmd)  
  # ---------------- RESULTS ----------------
   

    print(f"\n{B}  └── {G}{BOLD}ENUMERATION COMPLETE{W}")
    print(f"{B}      ├── {B}Entries Found:{W} {G}{len(found)}{W}")
    print(f"{B}      └── {B}Output File:{W} {Y}{output_file}{W}\n")



import os
import pty
import subprocess

def run_live(cmd):
    import os
    import pty
    import subprocess

    master, slave = pty.openpty()

    process = subprocess.Popen(
        cmd,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        text=True
    )

    os.close(slave)

    found = []

    while True:
        try:
            output = os.read(master, 1024).decode()
            if not output:
                break

            print(output, end="")

            for line in output.splitlines():
                if "/" in line and "Status:" in line:
                    found.append(line)

        except OSError:
            break

    process.wait()
    return found
