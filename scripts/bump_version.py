#!/usr/bin/env python3
"""Version bumping script."""
import argparse
from pathlib import Path
import subprocess

from va_shared.version import get_version, increment_version, update_version_files


def create_git_tag(version: str) -> None:
    """Create and push git tag."""
    tag = f"v{version}"
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Version {version}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)

def main():
    parser = argparse.ArgumentParser(description="Bump package version")
    parser.add_argument(
        "increment",
        choices=["major", "minor", "patch"],
        help="Version part to increment"
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git commands"
    )

    args = parser.parse_args()

    current_version = get_version()
    new_version = increment_version(current_version, args.increment)

    print(f"Bumping version: {current_version} -> {new_version}")

    update_version_files(new_version)

    if not args.no_git:
        create_git_tag(new_version)

    print("Version bump complete!")

if __name__ == "__main__":
    main()