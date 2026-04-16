import importlib.util
from pathlib import Path

from core.target import load_current_profile, get_active_cred, save_profile

BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"


# ---------------------- Module Loader ----------------------

def load_module(module_name):
    path = MODULES_DIR / Path(module_name.replace('.', '/')).with_suffix('.py')

    if not path.exists():
        raise Exception(f"Module not found: {module_name}")

    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    return mod


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