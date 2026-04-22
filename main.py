#!/usr/bin/env python3

import argparse
import sys

from core import target
from core import runner
from core.aliases import ALIASES
from core import doctor
from core.chain import run_chain_script
from core.chain import run_chain_script, CHAINS_DIR

# ---------------------- ALIAS RESOLVER ----------------------

def resolve_alias():
    if len(sys.argv) < 2:
        return None

    cmd1 = sys.argv[1]
    cmd2 = sys.argv[2] if len(sys.argv) > 2 else None

    # -------------------------
    # 1. dot syntax (ad.enum)
    # -------------------------
    if "." in cmd1:
        module, action = cmd1.split(".", 1)
    else:
        module = cmd1
        action = cmd2

    # -------------------------
    # 2. normal alias resolution
    # -------------------------
    for mod_name, mod_data in ALIASES.items():
        if module in mod_data["aliases"]:
            if not action:
                return None

            for action_name, action_aliases in mod_data["actions"].items():
                if action in action_aliases:
                    return mod_name, action_name

       # 🔥 FLAT COMMAND SUPPORT
    for mod_name, mod_data in ALIASES.items():
        for action_name, action_aliases in mod_data["actions"].items():
            if cmd1 in action_aliases:
                return mod_name, action_name

    return None


# ---------------------- MAIN ----------------------





def main():

    # ---------------------- PREPROCESS ----------------------

    def route_command(target_name, extra_args):
        # -------------------------
        # SHELL SPECIAL CASE
        # -------------------------
        if target_name == "shell":
            if not extra_args:
                extra_args = ["bash"]

            return [sys.argv[0], "run", "shell.generate"] + extra_args

        # -------------------------
        # NORMAL ROUTING
        # -------------------------
        path_name = target_name.replace(".", "/")
        chain_path = CHAINS_DIR / f"{path_name}.py"

        if chain_path.exists():
            print(f"\033[94m[*] Using Chain: {target_name}\033[0m")
            return [sys.argv[0], "chain", target_name] + extra_args
        else:
            return [sys.argv[0], "run", target_name] + extra_args


    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        # -------------------------
        # 0. SHELL DIRECT COMMAND
        # -------------------------
        if cmd == "shell":
            extra = sys.argv[2:]
            sys.argv = route_command("shell", extra)

        # -------------------------
        # 1. FORCE MODULE (:ad.xxx)
        # -------------------------
        elif cmd.startswith(":"):
            target_name = cmd[1:]
            print(f"\033[93m[*] Forced Module Mode: {target_name}\033[0m")
            sys.argv = [sys.argv[0], "run", target_name] + sys.argv[2:]

        else:
            resolved = resolve_alias()

            # -------------------------
            # 2. ALIASES
            # -------------------------
            if resolved:
                module, action = resolved

                if module == "target":
                    cmd = sys.argv[1]

                    # FULL FORM: ctf target create ...
                    if cmd == "target":
                        extra = sys.argv[3:]
                    else:
                        extra = sys.argv[2:]

                    sys.argv = [sys.argv[0], "target", action] + extra

                else:
                    target_name = f"{module}.{action}"
                    extra = sys.argv[2:]
                    sys.argv = route_command(target_name, extra)

            # -------------------------
            # 3. DOT SYNTAX (ad.xxx)
            # -------------------------
            elif "." in cmd:
                target_name = cmd
                extra = sys.argv[2:]
                sys.argv = route_command(target_name, extra)

    

    # ---------------------- CLI ----------------------

    parser = argparse.ArgumentParser(prog="ctf")
    subparsers = parser.add_subparsers(dest="command")

    # ---------------------- TARGET ----------------------
    target_parser = subparsers.add_parser("target")
    target_sub = target_parser.add_subparsers(dest="subcommand")

    create = target_sub.add_parser("create")
    create.add_argument("name")
    create.add_argument("--ip", required=True)
    create.add_argument("--domain", default=None)
    create.add_argument("--dc", default=None)
    create.set_defaults(func=target.target_create)

    use = target_sub.add_parser("use")
    use.add_argument("name")
    use.set_defaults(func=target.target_use)

    lst = target_sub.add_parser("list")
    lst.set_defaults(func=target.target_list)

    show = target_sub.add_parser("show")
    show.set_defaults(func=target.target_show)

    addcred = target_sub.add_parser("add-cred")
    addcred.add_argument("user")

    # password (default)
    addcred.add_argument("password", nargs="?")

    # alternative auth types
    addcred.add_argument("--hash")
    addcred.add_argument("--aes")
    addcred.add_argument("--ccache")

    addcred.set_defaults(func=target.target_add_cred)

    delete_parser = target_sub.add_parser("delete", help="Delete a target")
    delete_parser.add_argument("name", nargs="?", help="Target name (optional, defaults to current)")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=target.target_delete)

    creds = target_sub.add_parser("creds")
    creds.add_argument("--local", action="store_true")
    creds.add_argument("--domain", action="store_true")
    creds.set_defaults(func=target.target_creds)

    setcred = target_sub.add_parser("set-cred")
    setcred.add_argument("identifier")
    setcred.set_defaults(func=target.target_set_cred)



    # ---------------------- DOCTOR ----------------------

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--install", action="store_true")
    doctor_parser.set_defaults(func=doctor.doctor_run)

    # ---------------------- CHAIN ----------------------
    chain_parser = subparsers.add_parser("chain")
    chain_parser.add_argument("name")
    chain_parser.add_argument("extra", nargs="*")
    chain_parser.add_argument("--all", action="store_true") 
    chain_parser.add_argument("--full", action="store_true") 

    chain_parser.add_argument("--user")
    chain_parser.add_argument("--auto", action="store_true")
    chain_parser.add_argument("--quiet", action="store_true")
    
    chain_parser.set_defaults(func=lambda args: run_chain_script(args))
    
    




    # ---------------------- WHOAMI ----------------------
    whoami_parser = subparsers.add_parser("whoami")
    whoami_parser.add_argument("--short", action="store_true")
    whoami_parser.add_argument("--table", action="store_true")
    whoami_parser.set_defaults(func=target.target_whoami)


    # ---------------------- RUN ----------------------
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("module")
    run_parser.add_argument("--cred")
    run_parser.add_argument("--no-auth", action="store_true")
    run_parser.add_argument("extra", nargs="*")
    run_parser.add_argument("--users")
    run_parser.add_argument("--user")
    run_parser.add_argument("--out", "-o")
    run_parser.add_argument("--cmd")
    run_parser.add_argument("--run", action="store_true")
    run_parser.add_argument("--file", "-f", "--in")
    run_parser.add_argument("--format")
    run_parser.add_argument("--mode")
    run_parser.add_argument("--share")

    run_parser.add_argument("--method")
    run_parser.add_argument("--all", action="store_true")
    run_parser.add_argument("--save", action="store_true")

    run_parser.add_argument("--lhost")
    run_parser.add_argument("--lport")

    run_parser.set_defaults(func=runner.run_module)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
