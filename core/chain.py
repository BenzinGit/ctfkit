from pathlib import Path
import importlib.util

BASE_DIR = Path(__file__).resolve().parent.parent
CHAINS_DIR = BASE_DIR / "chains"


def run_chain_script(args):
    chain_file = CHAINS_DIR / f"{args.name}.py"

    if not chain_file.exists():
        available = [p.stem for p in CHAINS_DIR.glob("*.py")]

        print(f"[!] Chain not found: {args.name}")
        print(f"[*] Available chains: {', '.join(available)}")

    spec = importlib.util.spec_from_file_location(args.name, chain_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.run(args)