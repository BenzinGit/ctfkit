PROVIDES = ["usernames"]
REQUIRES = []

def run(data, cred, args):
    import subprocess
    from pathlib import Path
    import shutil
    from core.loot import get_loot_path, require_input

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TOOLS_DIR = BASE_DIR / "tools"

    # ---------------- INPUT ----------------
    input_file = require_input(data, args, "names", "fullnames", "full names file")
    if not input_file:
        return

    # ---------------- OUTPUT ----------------
    output_file = get_loot_path(data, "usernames")

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

    # ---------------- RUN ----------------
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