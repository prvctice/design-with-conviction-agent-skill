"""Portable package and installer checks; no design tools or agent accounts needed."""
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts" / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class PackageTests(unittest.TestCase):
    def test_frontmatter_and_self_contained_references(self):
        source = installer.SOURCE
        skill = (source / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: " + re.escape(source.name) + r"$")
        self.assertRegex(frontmatter, r"(?m)^description: .+")
        self.assertIn("license: MIT", frontmatter)
        self.assertTrue((source / "LICENSE").is_file())
        for file in source.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
                if re.match(r"https?://", link):
                    continue
                target = (file.parent / link.split("#")[0]).resolve()
                self.assertIn(source.resolve(), target.parents, str(file) + ": " + link)
                self.assertTrue(target.is_file(), str(target))

    def test_no_local_paths_or_host_tool_dependencies(self):
        for file in installer.SOURCE.rglob("*.md"):
            text = file.read_text(encoding="utf-8")
            for marker in ("/Users/", "/Volumes/", "mcp__", "functions.exec", "CLAUDE_SKILL_DIR"):
                self.assertNotIn(marker, text, str(file))

    def test_skill_keeps_its_core_sections(self):
        skill = (installer.SOURCE / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(skill.splitlines()), 500)
        for heading in ("## The manifesto", "## How to work", "## Stances",
                        "## What we don't do", "## House principles"):
            self.assertIn(heading, skill)
        for n in range(1, 11):
            self.assertRegex(skill, r"(?m)^" + str(n) + r"\. \*\*")

    def test_agent_destinations(self):
        base = Path("/example")
        for agent, directory in installer.AGENT_DIRS.items():
            self.assertEqual(installer.target_parent(agent, home=base), base / directory / "skills")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name) / "agent skills"
        self.target = self.parent / installer.SKILL_NAME

    def test_install_complete_and_repeat_is_noop(self):
        installer.install(installer.SOURCE, self.parent)
        self.assertEqual(installer.inventory(self.target), installer.inventory(installer.SOURCE))
        timestamp = (self.target / "SKILL.md").stat().st_mtime_ns
        self.assertTrue(installer.install(installer.SOURCE, self.parent).startswith("Already installed"))
        self.assertEqual(timestamp, (self.target / "SKILL.md").stat().st_mtime_ns)

    def test_dry_run_does_not_write(self):
        self.assertTrue(installer.install(installer.SOURCE, self.parent, True).startswith("Would install"))
        self.assertFalse(self.parent.exists())

    def test_conflicting_install_preserves_existing_content(self):
        self.target.mkdir(parents=True)
        keeper = self.target / "SKILL.md"
        keeper.write_text("local customizations", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            installer.install(installer.SOURCE, self.parent)
        self.assertEqual(keeper.read_text(encoding="utf-8"), "local customizations")
        self.assertEqual(list(self.target.iterdir()), [keeper])

    def test_symlink_destination_is_not_modified(self):
        elsewhere = Path(self.tmp.name) / "keeper"
        elsewhere.mkdir()
        self.parent.mkdir()
        try:
            self.target.symlink_to(elsewhere, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not permit symlink creation")
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE, self.parent)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_invalid_source_does_not_create_destination(self):
        with self.assertRaises(ValueError):
            installer.install(Path(self.tmp.name) / "missing", self.parent)
        self.assertFalse(self.parent.exists())


if __name__ == "__main__":
    unittest.main()
