# Installation and compatibility

The skill is a self-contained folder using the open
[Agent Skills format](https://agentskills.io/specification). It requires no specific
model API, provider credentials, MCP server, or design application. Python 3.9+
is needed only for the installer and package checks.

## Install manually

```sh
git clone https://github.com/prvctice/design-with-conviction-agent-skill.git
cd design-with-conviction-agent-skill
```

Choose the command for your agent:

```sh
python3 scripts/install.py --agent codex
python3 scripts/install.py --agent claude
python3 scripts/install.py --agent gemini
```

On Windows, use `py -3` or `python` if `python3` is unavailable.

For one project or a custom skills directory:

```sh
python3 scripts/install.py --agent claude --project /path/to/project
python3 scripts/install.py --target /path/to/agent/skills
```

Add `--dry-run` to preview the destination without writing. You can also copy the
complete `skills/design-with-conviction/` folder, including its
license, into your agent's skills directory.

| Agent | Default installation location | Documentation |
| --- | --- | --- |
| Codex | `~/.agents/skills/` | [Codex skills](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `~/.claude/skills/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Gemini CLI | `~/.gemini/skills/` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |
| Muse and other agents | Load `SKILL.md` and its linked references explicitly | Native integration not verified |

Older or custom installations can use `--target` with their configured skills
location. Avoid duplicate copies under the same name across discovery paths.

## Claude app

In the Claude app, save the contents of `skills/design-with-conviction/SKILL.md` as a
skill, or ask Claude to propose it as a skill for you to save.

## Updates and removal

The installer copies only the skill folder. It does not change agent settings,
install dependencies, or call the network. Reinstalling an identical copy does
nothing. If an existing copy differs, for example because you filled in House
principles, installation stops so your changes are kept.

To update, copy your House principles somewhere safe, move the existing skill
folder aside, install again, and paste your principles back. To uninstall, remove
only the installed skill folder.

## Contributing

Run the package checks with:

```sh
python3 -m unittest discover -s tests -v
```

Tests check the package and installer. They can't judge design quality. For that,
run the prompts in [`evals/evals.json`](../evals/evals.json) with and without the
skill and compare the results side by side.

Changes should keep the skill provider-neutral (no tool names from any one agent)
and self-contained in `SKILL.md`. Proposed principles should come with the
manifesto or practice they draw on.

Developed by Tim Moore with AI-assisted authoring, drawing on the collection at
[designmanifestos.org](https://designmanifestos.org/). Released under the
[MIT license](../LICENSE). No affiliation with the manifesto authors or any agent
provider is implied.
