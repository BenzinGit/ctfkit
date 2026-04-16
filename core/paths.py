from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_artifacts_dir(target_name):
    path = BASE_DIR / "artifacts" / target_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_artifact(target_name, filename):
    return get_artifacts_dir(target_name) / filename