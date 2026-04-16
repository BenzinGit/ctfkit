from core import runner
from core.loot import loot_exists

PIPELINES = {
    "asrep": [
        "wordlist.gen-usernames",
        "ad.asreproast",
        "crack.hash"
    ]
}

def run_pipeline(name, data, extra_args=None):
    if name not in PIPELINES:
        print("[!] Pipeline not found")
        return

    for module_name in PIPELINES[name]:
        module = runner.load_module(module_name)

        # skip if already done
        if all(loot_exists(data, p) for p in getattr(module, "PROVIDES", [])):
            print(f"[*] Skipping {module_name}")
            continue

        # check requirements
        missing = [
            r for r in getattr(module, "REQUIRES", [])
            if not loot_exists(data, r)
        ]

        if missing:
            print(f"[!] Missing {missing} for {module_name}")
            continue

        print(f"[*] Running {module_name}")
        runner.run_module_by_name(module_name, extra_args or [], data)