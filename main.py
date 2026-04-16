#!/usr/bin/env python3

import argparse
import sys

from core import target
from core import runner
from core.aliases import ALIASES
from core import doctor
from core import pipeline
# ---------------------- ALIAS RESOLVER ----------------------

def resolve_alias():
    if len(sys.argv) < 2:
        return None

    cmd = sys.argv[1]

    if "." in cmd:
        module, action = cmd.split(".", 1)
    else:
        if len(sys.argv) < 3:
            return None
        module = sys.argv[1]
        action = sys.argv[2]

    for mod_name, mod_data in ALIASES.items():
        if module in mod_data["aliases"]:

            # normalize module
            module = mod_name

            for action_name, action_aliases in mod_data["actions"].items():
                if action in action_aliases:
                    return module, action_name

    return None


# ---------------------- MAIN ----------------------

def main():
    # ---------------------- PREPROCESS ----------------------

    # 1. Resolve aliases FIRST
    resolved = resolve_alias()

    if resolved:
        module, action = resolved

        if module != "target":
            extra = sys.argv[2:] if "." in sys.argv[1] else sys.argv[3:]
            sys.argv = ["ctf", "run", f"{module}.{action}"] + extra

        else:
            sys.argv[1] = "target"
            if len(sys.argv) > 2:
                sys.argv[2] = action

    # 2. THEN handle module shorthand
    elif len(sys.argv) > 1 and "." in sys.argv[1]:
        module = sys.argv[1]
        extra = sys.argv[2:]
        sys.argv = ["ctf", "run", module] + extra

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




    creds = target_sub.add_parser("creds")
    creds.add_argument("--local", action="store_true")
    creds.add_argument("--domain", action="store_true")
    creds.set_defaults(func=target.target_creds)

    setcred = target_sub.add_parser("set-cred")
    setcred.add_argument("identifier")
    setcred.set_defaults(func=target.target_set_cred)

    add_domain = target_sub.add_parser("add-domain")
    add_domain.add_argument("--domain", required=True)
    add_domain.set_defaults(func=target.target_add_domain)


    # ---------------------- DOCTOR ----------------------

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--install", action="store_true")
    doctor_parser.set_defaults(func=doctor.doctor_run)


    # ---------------------- Pipeline ----------------------

    pipe = subparsers.add_parser("pipeline")
    pipe.add_argument("name")
    pipe.set_defaults(func=lambda args: pipeline.run_pipeline(
    args.name,
    target.load_current_profile()[0],
    args.extra   
))
    
    



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
    run_parser.add_argument("--out")

    run_parser.add_argument("--names")
    run_parser.add_argument("--format")
    run_parser.set_defaults(func=runner.run_module)

    args, unknown = parser.parse_known_args()

    args.extra = unknown
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
