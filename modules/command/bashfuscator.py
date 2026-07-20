import subprocess

from core.paths import get_tools_dir, get_venvs_dir


NAME = "command.bashfuscator"
DESCRIPTION = "Obfuscate Linux commands using Bashfuscator."

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"



def get_payload(args):

    if getattr(args, "extra", None):
        return " ".join(args.extra)

    return input(f"{Y}Payload>{W} ").strip()

def run(data, cred, args):

    payload = get_payload(args)

    if not payload:
        return

    bashfuscator = (
        get_tools_dir()
        / "Bashfuscator"
        / "bashfuscator"
        / "bin"
        / "bashfuscator"
    )

    python = (
        get_venvs_dir()
        / "bashfuscator"
        / "bin"
        / "python"
    )

    if not bashfuscator.exists():
        print(f"{R}[-]{W} Bashfuscator not found.")
        return

    if not python.exists():
        print(f"{R}[-]{W} Bashfuscator venv not found.")
        return

    try:

        result = subprocess.run(
            [
                str(python),
                str(bashfuscator),
                "-q",
                "-c",
                payload,
                "-s",
                "2",
                "-t",
                "2",
                "--layers",
                "1",
                "--no-mangling",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print()
        print(f"\n{G}[+] Obfuscated Payload{W}")
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:

        print(f"{R}[-]{W} Bashfuscator failed.")
        print(e.stderr)
