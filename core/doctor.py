def doctor_run(args):
    import shutil
    from pathlib import Path
    import subprocess

    BASE_DIR = Path(__file__).resolve().parent.parent
    TOOLS_DIR = BASE_DIR / "tools"

    tools = {
        "kerbrute": {
            "check": "kerbrute",
            "install": "https://github.com/ropnop/kerbrute"
        },
        "username-anarchy": {
            "check": "username-anarchy",
            "install": "https://github.com/urbanadventurer/username-anarchy"
        },
        "nxc": {
            "check": "nxc",
            "install": "https://github.com/Pennyw0rth/NetExec"
        }
    }

    print("\n=== CTF Doctor ===\n")

    missing = []

    for name, info in tools.items():
        system_path = shutil.which(info["check"])
        local_path = TOOLS_DIR / name

        if system_path:
            print(f"[+] {name:<20} FOUND (system)")
        elif local_path.exists():
            print(f"[+] {name:<20} FOUND (local)")
        else:
            print(f"[!] {name:<20} MISSING")
            missing.append(name)

    # ---------------- INSTALL ----------------
    if args.install and missing:
        print("\n[*] Installing missing tools...\n")

        TOOLS_DIR.mkdir(exist_ok=True)

        for name in missing:
            repo = tools[name]["install"]
            dest = TOOLS_DIR / name

            print(f"[*] Cloning {name}...")

            subprocess.run(f"git clone {repo} {dest}", shell=True)

            # Special case: username-anarchy binary location
            if name == "username-anarchy":
                binary = dest / "username-anarchy"
                if binary.exists():
                    binary.chmod(0o755)

        print("\n[+] Installation complete")

    elif args.install:
        print("\n[+] All tools already installed")

    print("")