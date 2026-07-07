def run(
    data,
    cred,
    args
):

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'

    from core.paths import get_tools_dir
    from modules.upload.windows import stage_windows_files

    domain = (
        data.get("domain")
        or "<DOMAIN>"
    )

    print(
        f"\n{B}┌── {BOLD}SNAFFLER{W}{B} ──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W}  {B}Domain:{W} "
        f"{C}{domain:<28}{W}"
        f"{B}│{W}"
    )

    print(
        f"{B}└───────────────────────────────────────────┘{W}\n"
    )

    print(
        f"{B}[?]{W} Transfer Snaffler?\n"
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

        Snaffler = (
            windows_tools /
            "Snaffler.exe"
        )

        stage_windows_files([
            Snaffler
        ])

    print(
        f"\n{G}[+] {W}Broad Share Scan\n"
    )

    print(
        f"{Y}.\\Snaffler.exe "
        f"-s "
        f"-d {domain.upper()} "
        f"-o snaffler.log "
        f"-v data{W}"
    )

    print()

    print(
        f"{G}[+] {W}Notes\n"
    )

    print(
        f"  {B}├──{W} Searches accessible shares"
    )

    print(
        f"  {B}├──{W} Looks for passwords, configs, keys"
    )

    print(
        f"  {B}├──{W} Writes findings to {C}snaffler.log{W}"
    )

    print(
        f"  {B}└──{W} Review findings manually"
    )

    print()

    return data
