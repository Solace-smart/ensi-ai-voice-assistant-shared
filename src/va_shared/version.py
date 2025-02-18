"""Version management for va-shared package."""
from pathlib import Path
import re
from typing import Tuple

VERSION = "0.1.23"

def get_version() -> str:
    """Get the current version."""
    return VERSION

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into tuple of (major, minor, patch)."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, match.groups()))

def increment_version(version: str, increment: str = "patch") -> str:
    """
    Increment the version number.

    Args:
        version: Current version string
        increment: One of 'major', 'minor', or 'patch'

    Returns:
        New version string
    """
    major, minor, patch = parse_version(version)

    if increment == "major":
        return f"{major + 1}.0.0"
    elif increment == "minor":
        return f"{major}.{minor + 1}.0"
    elif increment == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Increment must be 'major', 'minor', or 'patch'")

def update_version_files(new_version: str) -> None:
    """Update version in all necessary files."""
    root_dir = Path(__file__).parent.parent.parent

    # Update version.py - ONLY update the VERSION variable
    version_file = root_dir / "src" / "va_shared" / "version.py"
    with open(version_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith('VERSION = "'):
            lines[i] = f'VERSION = "{new_version}"\n'

    with open(version_file, 'w') as f:
        f.writelines(lines)

    # Update pyproject.toml - Only update version in [project] section
    pyproject_file = root_dir / "pyproject.toml"
    with open(pyproject_file, 'r') as f:
        lines = f.readlines()

    in_project_section = False
    for i, line in enumerate(lines):
        if line.strip() == '[project]':
            in_project_section = True
        elif line.startswith('['):
            in_project_section = False
        elif in_project_section and line.strip().startswith('version = "'):
            lines[i] = f'version = "{new_version}"\n'

    with open(pyproject_file, 'w') as f:
        f.writelines(lines)

    # Update setup.py
    setup_file = root_dir / "setup.py"
    content = setup_file.read_text()
    content = re.sub(
        r'version="[^"]+"',
        f'version="{new_version}"',
        content
    )
    setup_file.write_text(content)