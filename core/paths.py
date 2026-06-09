from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_artifacts_dir(target_name):
    path = BASE_DIR / "artifacts" / target_name
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_domains_dir():
    return BASE_DIR / "domains"

def get_artifact(target_name, filename):
    return get_artifacts_dir(target_name) / filename

def get_chain_artifacts_dir(target_name, chain_name):
    base = get_artifacts_dir(target_name)
    path = base / chain_name
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_tools_dir():
    return BASE_DIR / "tools"

def get_tool_path(filename):
    return get_tools_dir() / filename

def get_windows_tools_dir():

    path = (
        get_tools_dir()
        / "windows"
    )

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return path