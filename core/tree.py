from pathlib import Path

# ---------------- COLORS ----------------
G = '\033[92m'
C = '\033[96m'
B = '\033[94m'
Y = '\033[93m'
W = '\033[0m'
R = '\033[91m'
BOLD = '\033[1m'

# =========================================================
# TREE BUILDING
# =========================================================

def build_tree(paths, base_dir):
    tree = {}

    for path in paths:
        parts = path.relative_to(base_dir).with_suffix("").parts

        current = tree
        for p in parts:
            current = current.setdefault(p, {})

    return tree


def print_tree(tree, prefix=""):
    items = sorted(tree.items())

    for i, (key, subtree) in enumerate(items):

        is_last = i == len(items) - 1

        connector = "└── " if is_last else "├── "

        label = f"{C}{key}{W}" if subtree else f"{W}{BOLD}{key}{W}"

        print(f"  {B}{prefix}{connector}{W}{label}")

        if subtree:
            extension = "    " if is_last else "│   "
            print_tree(subtree, prefix + extension)


# =========================================================
# GENERIC RESOURCE LISTING
# =========================================================

def list_resources(base_dir, extension, title, ignore=None):

    ignore = ignore or []

    print(f"\n{W}{BOLD}[*] {title.upper()}{W}")

    paths = []

    for p in base_dir.rglob(f"*{extension}"):

        if any(x in str(p) for x in ignore):
            continue

        if p.name.startswith("__"):
            continue

        paths.append(p)

    if not paths:
        print(f"  {R}└── No resources found.{W}")
        return

    print(f"  {B}└──{W} Source: {C}{base_dir}{W}\n")

    tree = build_tree(paths, base_dir)

    print_tree(tree)

    print()
