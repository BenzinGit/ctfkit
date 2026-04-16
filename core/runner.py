import importlib.util
from pathlib import Path

from core.target import load_current_profile, get_active_cred, save_profile

BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"


# ---------------------- Module Loader ----------------------



def load_module(module_name):
    import importlib

    try:
        return importlib.import_module(f"modules.{module_name}")
    except Exception as e:
        print(f"[!] Failed to load module {module_name}: {e}")
        return None

# ---------------------- Runner ----------------------

def run_module(args):
    try:
        data, path = load_current_profile()
    except Exception as e:
        print(f"[!] {e}")
        return

    # credential handling
    if args.no_auth:
        cred = None
    else:
        try:
            cred = get_active_cred(data, args.cred)
        except Exception:
            cred = None

    # load module
    try:
        module = load_module(args.module)
    except Exception as e:
        print(f"[!] {e}")
        return

    # execute
    result = module.run(data, cred, args)

    # save if modified
    if result:
        save_profile(result, path)

def run_module_by_name(module_name, extra_args, data=None):
    import argparse

    module = load_module(module_name)

    if not module:
        print(f"[!] Module not found: {module_name}")
        return

    args = argparse.Namespace()
    args.extra = extra_args
    args.no_auth = False
    args.cred = None

    i = 0
    while i < len(extra_args):
        if extra_args[i].startswith("--"):
            key = extra_args[i][2:]

            if i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
                value = extra_args[i + 1]
                i += 2
            else:
                value = True
                i += 1

            setattr(args, key, value)
        else:
            i += 1

    # load data + cred
    from core import target
    try:
        if not data:
            data, _ = target.load_current_profile()
        cred = target.get_active_cred(data)
    except:
        cred = None

    return module.run(data, cred, args)