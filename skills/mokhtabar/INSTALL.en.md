# Install Mokhtabar

[العربية](INSTALL.md) · [English](INSTALL.en.md)

Place the complete `mokhtabar` folder in the skill directory supported by your agent. The template, builder, and resources are required; do not copy only SKILL.md.

- Codex: `~/.agents/skills/mokhtabar/`
- Claude Code: `~/.claude/skills/mokhtabar/`
- Other agents: use their documented skill path, or ask the agent to read SKILL.md directly.

Ask: “Use Mokhtabar for my project. Prepare relevant questions, apply alternatives to its actual pages, and include a page map and notes.”

Build the bundled neutral example from this directory:

```bash
python scripts/build.py assets/example-project.json --out lab.html
```

Open lab.html in a modern browser, answer questions, add notes, review, and copy the final brief to your agent. Python 3.10+ is required for building, with no third-party libraries. The resulting HTML embeds its resources and can be used offline.

The display name is مختبر; its technical identifier is `mokhtabar`. SHELL.sha256 detects accidental changes to the fixed shell. MIT for code; SIL OFL for bundled IBM Plex and Noto fonts.
