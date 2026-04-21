from pathlib import Path
import importlib.util

BASE_DIR = Path(__file__).resolve().parent.parent
CHAINS_DIR = BASE_DIR / "chains"


def run_chain_script(args):
    # 1. Convert "ad.kerberoast" to "ad/kerberoast" so Linux can find the file
    path_name = args.name.replace(".", "/")
    chain_file = CHAINS_DIR / f"{path_name}.py"

    if not chain_file.exists():

        print(f"[!] Chain not found at: {chain_file}") 
        available = [p.stem for p in CHAINS_DIR.rglob("*.py")] # rglob finds nested files
        print(f"[*] Available chains: {', '.join(available)}")
        return 

    spec = importlib.util.spec_from_file_location(path_name, chain_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.run(args)
