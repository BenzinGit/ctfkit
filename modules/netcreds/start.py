import shutil
import subprocess

from core.paths import get_tools_dir
from core.attacker import get_current_interface


G, C, B, Y, W, R = (
        '\033[92m',
        '\033[96m',
        '\033[94m',
        '\033[93m',
        '\033[0m',
        '\033[91m',
)

BOLD = '\033[1m'

#
# Stable tool path convention (see docs/CTFKIT_STANDARDS.md #14) - the repo
# clone keeps its upstream name, the script inside it keeps its own name.
# Not present yet - see the README/TODO for where to put it.
#
TOOL_PATH = get_tools_dir() / "net-creds" / "net-creds.py"


def _find_interpreter():

    #
    # net-creds' own README documents it as Python 2.7 (scapy/pcapy/pypcap/
    # libdnet, all classic py2-era packages). Prefer an actual py2 if one's
    # on the box; python3 is offered as a last-resort fallback since modern
    # scapy does support it, but pcapy/libdnet compatibility isn't
    # guaranteed - flagged clearly rather than silently assumed to work.
    #
    for candidate in ("python2", "python2.7"):

        path = shutil.which(candidate)

        if path:
            return path, True

    path = shutil.which("python3")

    return path, False


def run(data, cred, args):

    #
    # REFERENCE MODE
    #

    if getattr(args, "reference", False):

        print()
        print(f"{Y}sudo python2 {TOOL_PATH} -i <INTERFACE>{W}")
        print()
        print(f"{Y}python2 {TOOL_PATH} -p <PCAP_FILE>{W}")
        print()

        return data

    if not TOOL_PATH.is_file():

        print(f"\n{R}[!]{W} {TOOL_PATH} not found.")
        print(f"{Y}    git clone https://github.com/DanMcInerney/net-creds {TOOL_PATH.parent}{W}\n")

        return data

    #
    # MODE: pcap file (positional arg) vs live interface (default - "let
    # this tool run in the background during an assessment" is the
    # material's own framing of the primary use case)
    #

    pcap = None

    if hasattr(args, "extra") and args.extra:
        pcap = args.extra[0]

    interface = None

    if not pcap:

        try:
            interface = get_current_interface()
        except Exception:
            pass

        if not interface:
            interface = input(f"\n{B}[?]{W} Interface > ").strip()

        if not interface:
            print(f"\n{R}[!]{W} No interface selected\n")
            return data

    #
    # INTERPRETER
    #

    interpreter, is_py2 = _find_interpreter()

    if not interpreter:

        print(f"\n{R}[!]{W} No Python 2 or Python 3 interpreter found on PATH.\n")
        return data

    if not is_py2:
        print(f"\n{Y}[!]{W} No python2/python2.7 found - falling back to {interpreter}.")
        print(f"    net-creds is documented against Python 2.7 - pcapy/libdnet under py3 aren't guaranteed to work.")

    #
    # COMMAND
    #

    if pcap:
        cmd = [interpreter, str(TOOL_PATH), "-p", pcap]
    else:
        cmd = ["sudo", interpreter, str(TOOL_PATH), "-i", interface]

    #
    # HEADER
    #
    # Box stays constant-width - the mode line (pcap path or interface
    # name) is arbitrary-length free text, printed below rather than
    # fixed-width-embedded in the border (that broke alignment in
    # breakout/citrix.py for the same reason).
    #

    print(f"\n{B}┌── {BOLD}MODULE: NET-CREDS{W}{B} " + "─" * 20 + f"┐{W}")
    print(f"{B}└" + "─" * 38 + f"┘{W}")

    if pcap:
        print(f"{B}Mode:{W} {C}pcap file — {pcap}{W}")
    else:
        print(f"{B}Mode:{W} {C}live capture — {interface}{W}")

    print(f"\n{B}[*]{W} Starting net-creds\n")
    print(f"{Y}{' '.join(cmd)}{W}\n")

    subprocess.run(cmd)

    return data
