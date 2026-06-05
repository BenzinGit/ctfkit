import re

# =========================================================
# COLORS
# =========================================================

G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
R = '\033[91m'
W = '\033[0m'
W_BOLD = '\033[1m'

# =========================================================
# PRIVILEGE DATABASE
# =========================================================

PRIVS = {

    # -----------------------------------------------------
    # TOKEN IMPERSONATION
    # -----------------------------------------------------

    "SeImpersonatePrivilege": {

        "description":
            "token impersonation attacks",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.tokens",

                "reason":
                    "potato family impersonation attacks",
            },

        ],

        "abuse": [
            "PrintSpoofer",
            "JuicyPotato",
            "RoguePotato",
            "GodPotato",
        ],
    },

    "SeAssignPrimaryTokenPrivilege": {

        "description":
            "token impersonation attacks",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.tokens",

                "reason":
                    "primary token abuse",
            },

        ],

        "abuse": [
            "JuicyPotato",
        ],
    },

    # -----------------------------------------------------
    # OWNERSHIP
    # -----------------------------------------------------

    "SeTakeOwnershipPrivilege": {

        "description":
            "take ownership of sensitive files",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.ownership",

                "reason":
                    "ownership abuse",
            },

        ],

        "abuse": [
            "takeown",
            "icacls",
        ],
    },

    # -----------------------------------------------------
    # BACKUP / RESTORE
    # -----------------------------------------------------

    "SeBackupPrivilege": {

        "description":
            "backup operators and protected file abuse",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.backup",

                "reason":
                    "registry hives and protected files",
            },

            {
                "name":
                    "ctf privesc.windows.services",

                "reason":
                    "service control abuse",
            },

        ],

        "abuse": [
            "reg save",
            "diskshadow",
            "robocopy /b",
            "service abuse",
        ],
    },

    "SeRestorePrivilege": {

        "description":
            "restore abuse and service control attacks",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.backup",

                "reason":
                    "registry restore and overwrite abuse",
            },

            {
                "name":
                    "ctf privesc.windows.serveroperators",

                "reason":
                    "service control abuse",
            },

        ],

        "abuse": [
            "registry restore",
            "overwrite protected files",
            "service abuse",
        ],
    },

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    "SeDebugPrivilege": {

        "description":
            "debug and access SYSTEM processes",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.debug",

                "reason":
                    "SYSTEM process interaction",
            },

        ],

        "abuse": [
            "lsass dumping",
            "token theft",
        ],
    },

    # -----------------------------------------------------
    # LOAD DRIVER
    # -----------------------------------------------------

    "SeLoadDriverPrivilege": {

        "description":
            "load vulnerable kernel drivers",

        "modules": [

            {
                "name":
                    "ctf privesc.windows.drivers",

                "reason":
                    "Capcom.sys driver exploitation",
            },

        ],

        "abuse": [
            "Capcom.sys",
            "EoPLoadDriver",
            "SYSTEM shell",
        ],
    },
}

# =========================================================
# HELPERS
# =========================================================

def parse_privileges(text):

    found = []

    lines = text.splitlines()

    for line in lines:

        for priv in PRIVS:

            if priv.lower() not in line.lower():
                continue

            enabled = (
                "enabled" in line.lower()
            )

            found.append({

                "name": priv,

                "enabled": enabled,

                "meta": PRIVS[priv],

            })

    return found


# =========================================================
# RENDER
# =========================================================

def render_privs(privs):

    print(
        f"\n{B}[*]{W} "
        f"DETECTED PRIVILEGES\n"
    )

    for idx, entry in enumerate(privs):

        connector = (
            "└──"
            if idx == len(privs)-1
            else "├──"
        )

        color = (
            G if entry["enabled"]
            else Y
        )

        state = (
            "enabled"
            if entry["enabled"]
            else "disabled"
        )

        print(
            f"  {B}{connector}{W} "
            f"{color}{entry['name']}{W} "
            f"({state})"
        )


def render_paths(privs):

    print(
        f"\n{B}[*]{W} "
        f"POTENTIAL ABUSE PATHS\n"
    )

    for idx, entry in enumerate(privs):

        meta = entry["meta"]

        connector = (
            "└──"
            if idx == len(privs)-1
            else "├──"
        )

        color = (
            G if entry["enabled"]
            else Y
        )

        print(
            f"  {B}{connector}{W} "
            f"{color}{entry['name']}{W}"
        )

        print(
            f"  {B}│{W} "
            f"purpose: "
            f"{meta['description']}"
        )

        # =================================================
        # MODULES
        # =================================================

        modules = meta.get(
            "modules",
            []
        )

        if modules:

            print(
                f"  {B}│{W} "
                f"modules:"
            )

            for module in modules:

                print(
                    f"  {B}│{W} "
                    f"  ├── "
                    f"{C}{module['name']}{W}"
                )

                print(
                    f"  {B}│{W} "
                    f"  │   "
                    f"{module['reason']}"
                )

        # =================================================
        # TECHNIQUES
        # =================================================

        abuses = meta.get(
            "abuse",
            []
        )

        if abuses:

            print(
                f"  {B}│{W} "
                f"techniques:"
            )

            for abuse in abuses:

                print(
                    f"  {B}│{W} "
                    f"  └── "
                    f"{abuse}"
                )

        # =================================================
        # ENABLED / DISABLED
        # =================================================

        if not entry["enabled"]:

            print(
                f"  {B}│{W} "
                f"{Y}note:{W} "
                f"privilege currently disabled"
            )

        print()


def render_enable_hint(privs):

    disabled = [

        p for p in privs
        if not p["enabled"]

    ]

    if not disabled:
        return

    print(
        f"{Y}"
        f"┌── ENABLE TOKEN PRIVILEGES "
        f"────────────────────────────┐{W}"
    )

    print(
        f"{Y}│{W} "
        f"Import-Module "
        f".\\Enable-Privilege.ps1"
    )

    print(
        f"{Y}│{W} "
        f".\\EnableAllTokenPrivs.ps1"
    )

    print(
        f"{Y}"
        f"└──────────────────────────────────────────────────┘{W}"
    )


# =========================================================
# MAIN
# =========================================================

def run(data=None, cred=None, args=None):

    print(
        f"\n{W_BOLD}"
        f"[*] WINDOWS PRIVILEGE ANALYZER{W}"
    )

    # =====================================================
    # INPUT
    # =====================================================

    try:

        text = input(
            f"\n{B}whoami /priv{W}> "
        )

    except (KeyboardInterrupt, EOFError):

        print()

        return data

    if not text.strip():

        print(
            f"\n{R}[!] "
            f"No input provided.{W}"
        )

        return data

    # =====================================================
    # PARSE
    # =====================================================

    found = parse_privileges(text)

    if not found:

        print(
            f"\n{R}[!] "
            f"No supported privileges detected.{W}"
        )

        return data

    # =====================================================
    # OUTPUT
    # =====================================================

    render_privs(found)

    render_paths(found)

    render_enable_hint(found)

    return data