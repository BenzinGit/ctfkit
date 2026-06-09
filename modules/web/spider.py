#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from core.paths import get_artifacts_dir, get_tool_path
from core.target import get_current_url
from core.target import load_current_profile, get_current_url

PROVIDES = []
REQUIRES = []

MAX_DISPLAY = 50

CATEGORIES = {
    "1": ("emails", "EMAILS"),
    "2": ("links", "LINKS"),
    "3": ("external_files", "EXTERNAL FILES"),
    "4": ("js_files", "JAVASCRIPT FILES"),
    "5": ("form_fields", "FORM FIELDS"),
    "6": ("images", "IMAGES"),
    "7": ("comments", "COMMENTS"),
}


def print_summary(results):
    B = "\033[94m"
    C = "\033[96m"
    W = "\033[0m"

    print(f"\n{B}┌── WEB SPIDER RESULTS ────────────────────────┐{W}")
    print(f"{B}│{W} Emails:         {C}{len(results.get('emails', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} Links:          {C}{len(results.get('links', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} External Files: {C}{len(results.get('external_files', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} JS Files:       {C}{len(results.get('js_files', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} Form Fields:     {C}{len(results.get('form_fields', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} Images:          {C}{len(results.get('images', [])):<10}{W}{B}│{W}")
    print(f"{B}│{W} Comments:        {C}{len(results.get('comments', [])):<10}{W}{B}│{W}")
    print(f"{B}└───────────────────────────────────────────────┘{W}")


def save_categories(results, artifact_dir):
    mapping = {
        "emails": "emails.txt",
        "links": "links.txt",
        "external_files": "external_files.txt",
        "js_files": "js_files.txt",
        "form_fields": "form_fields.txt",
        "images": "images.txt",
        "comments": "comments.txt",
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)

    for key, filename in mapping.items():
        values = results.get(key, [])
        output = artifact_dir / filename

        with open(output, "w", encoding="utf-8") as f:
            for item in values:
                f.write(str(item) + "\n")


def show_entries(title, entries):
    G = "\033[92m"
    B = "\033[94m"
    W = "\033[0m"

    print(f"\n{B}[{W}{G}*{W}{B}]{W} {title}\n")

    if not entries:
        print("No entries.")
        return

    for item in entries[:MAX_DISPLAY]:
        print(item)

    if len(entries) > MAX_DISPLAY:
        print()
        print(f"... showing {MAX_DISPLAY} of {len(entries)} entries")

    print()


def menu(results):
    while True:
        print(
            "\n"
            "1) Emails\n"
            "2) Links\n"
            "3) External Files\n"
            "4) JavaScript Files\n"
            "5) Form Fields\n"
            "6) Images\n"
            "7) Comments\n"
            "8) Everything\n"
            "0) Exit\n"
        )

        choice = input("Select: ").strip()

        if choice == "0":
            return

        if choice == "8":
            for key, title in CATEGORIES.values():
                show_entries(title, results.get(key, []))
            continue

        if choice not in CATEGORIES:
            continue

        key, title = CATEGORIES[choice]
        show_entries(title, results.get(key, []))


def run_spider(url):
    spider = get_tool_path("web/ReconSpider.py")

    cmd = [sys.executable, str(spider), str(url)]
    subprocess.run(cmd, check=True)


def move_results_json(artifact_dir):
    source = Path("results.json")
    destination = artifact_dir / "results.json"

    if source.exists():
        shutil.move(str(source), str(destination))
        return destination

    if destination.exists():
        return destination

    return None


def load_results(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Run ReconSpider and display/save results.")
    parser.add_argument(
        "url",
        nargs="?",
        help="Target URL. If omitted, the current target URL is used.",
    )
    parser.add_argument(
        "extra",
        nargs="*",
        help="Optional extra argument(s); if provided, the first one is treated as a JSON file path.",
    )
    return parser.parse_args()

from urllib.parse import urlparse


def run(data, cred, args):

    profile, _ = load_current_profile()

    url = get_current_url(profile)

    if not url:
        raise SystemExit("No URL configured for current target.")

    target_name = profile["name"]
    artifact_dir = get_artifacts_dir(target_name)

    run_spider(url)

    moved = move_results_json(artifact_dir)

    if getattr(args, "extra", None):
        json_file = Path(args.extra[0])
    else:
        json_file = moved if moved else (artifact_dir / "results.json")

    if not json_file.exists():
        raise SystemExit(f"Results file not found: {json_file}")

    results = load_results(json_file)

    save_categories(results, artifact_dir)
    print_summary(results)
    menu(results)