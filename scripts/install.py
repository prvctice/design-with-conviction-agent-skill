#!/usr/bin/env python3
"""Copy the portable skill into an agent's discovery directory. Python 3.9+."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile

SKILL_NAME = "design-with-conviction"
REPOSITORY = Path(__file__).resolve().parents[1]
SOURCE = REPOSITORY / "skills" / SKILL_NAME
AGENT_DIRS = {"codex": ".agents", "claude": ".claude", "gemini": ".gemini"}


def inventory(folder):
    """Compare complete skill contents; reject symlinks rather than following them."""
    result = {}
    for item in sorted(folder.rglob("*")):
        if item.is_symlink():
            raise ValueError("Skill contains a symlink: " + str(item))
        if item.is_file():
            result[item.relative_to(folder).as_posix()] = item.read_bytes()
    return result


def target_parent(agent, project=None, home=None):
    base = Path(project).expanduser().resolve() if project else (home or Path.home())
    return base / AGENT_DIRS[agent] / "skills"


def install(source, parent, dry_run=False):
    source = Path(source).resolve()
    parent = Path(parent).expanduser().resolve()
    target = parent / SKILL_NAME
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source is missing SKILL.md: " + str(source))
    contents = inventory(source)
    if target.is_symlink():
        raise ValueError("Destination is a symlink; inspect it manually: " + str(target))
    if target.exists():
        if target.is_dir() and inventory(target) == contents:
            return "Already installed: " + str(target)
        raise FileExistsError(
            "Destination already exists and differs; back it up and move it aside "
            "before installing: " + str(target)
        )
    if source == target or source in target.parents:
        raise ValueError("Destination cannot be inside the source skill")
    if dry_run:
        return "Would install: " + str(target)
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".dwc-skill-install-", dir=str(parent)) as tmp:
        staged = Path(tmp) / SKILL_NAME
        shutil.copytree(source, staged)
        if target.exists() or target.is_symlink():
            raise FileExistsError("Destination appeared during install: " + str(target))
        staged.rename(target)
    return "Installed: " + str(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agent", choices=sorted(AGENT_DIRS))
    mode.add_argument("--target", type=Path, help="Custom parent directory for skill folders")
    parser.add_argument("--project", type=Path, help="Project directory; otherwise installs for current user")
    parser.add_argument("--dry-run", action="store_true", help="Check and print destination without writes")
    args = parser.parse_args()
    if args.target and args.project:
        parser.error("--project only applies with --agent")
    parent = args.target if args.target else target_parent(args.agent, args.project)
    try:
        print(install(SOURCE, parent, args.dry_run))
    except (OSError, ValueError) as error:
        print("Install failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
