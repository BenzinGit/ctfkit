from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOOT_DIR = BASE_DIR / "loot"

def get_loot_dir(data):
    path = LOOT_DIR / data["name"]
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_loot_path(data, name):
    target = data.get("name")

    target_dir = LOOT_DIR / target
    target_dir.mkdir(parents=True, exist_ok=True)

    return target_dir / f"{name}.txt"


def loot_exists(data, name):
    return get_loot_path(data, name).exists()


def resolve_input(data, args, arg_name, loot_name):

    # CLI
    value = getattr(args, arg_name, None)
    if value:
        return value

    # Loot fallback
    path = get_loot_path(data, loot_name)
    if path.exists():
        return path

    return None

from pathlib import Path

def require_input(data, args, arg_name, loot_name, desc):
    value = getattr(args, arg_name, None)

    if value:
        path = Path(value).expanduser().resolve()

        if path.exists():
            return path

        print(f"[!] File not found: {value} ({path})")
        return None

    # fallback to loot
    path = get_loot_path(data, loot_name)

    if path.exists():
        return path

    print(f"[!] Missing {desc}")
    print(f"[*] Use --{arg_name} OR put file in loot/<target>/{loot_name}.txt")
    return None
