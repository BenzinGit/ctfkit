PROVIDES = ["usernames"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import shutil

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TOOLS_DIR = BASE_DIR / "tools"

    # ---------------- HELPERS ----------------
    def require_file(value, name):
        if not value:
            print(f"[!] Missing --{name}")
            return None

        path = Path(value).expanduser().resolve()

        if not path.exists():
            print(f"[!] File not found: {path}")
            return None

        return path

    # ---------------- INPUT ----------------
    input_file = require_file(args.file, "file")
    if not input_file:
        return

    # ---------------- OUTPUT ----------------
    output_path = args.out or "usernames.txt"
    output_file = Path(output_path).expanduser().resolve()


    # ---------------- FORMATS ----------------
    formats = getattr(args, "format", None) or ",".join([
        "first",
        "last",
        "first.last",
        "flast",
        "firstl",
        "f.last",
        "firstlast",
        "last.first",
        "lfirst",
        "first1"
    ])

    # ---------------- TOOL ----------------
    tool = shutil.which("username-anarchy")

    if not tool:
        tool = TOOLS_DIR / "username-anarchy" / "username-anarchy"

    if not Path(tool).exists():
        print("[!] username-anarchy not found")
        print("[*] Run: ctf doctor --install")
        return

    # ----------input_file = require_file(getattr(args, "file", None), "file")------ RUN ----------------
    cmd = f"{tool} --input-file {input_file} --select-format {formats}"

    print(f"[*] Running: {cmd}\n")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stderr:
        print(result.stderr)

    usernames = result.stdout.splitlines()

    if not usernames:
        print("[!] No usernames generated")
        return

    usernames = sorted(set(usernames))

    output_file.write_text("\n".join(usernames))

    print(f"[+] Generated {len(usernames)} usernames → {output_file}")