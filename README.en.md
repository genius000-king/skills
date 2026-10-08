# Skills

[العربية](README.md) · [English](README.en.md)

A skill library for AI agents that support `SKILL.md` and can read and write files.

## Available skills

| Category | Skill | Description | Files |
| --- | --- | --- | --- |
| Design and planning | Mokhtabar — مختبر | Guided questions, visual alternatives, and a page-flow canvas | [Guide](skills/mokhtabar/README.en.md) · [SKILL.md](skills/mokhtabar/SKILL.md) · [ZIP](packages/mokhtabar-v4.0.0.zip) |

## Mokhtabar

The agent builds an HTML decision workspace: one question, its alternatives, and one preview. Answer and press Next. The agent prepares the question order and relevant branches from the project; follow-ups depend on your answers. Notes and additional tools open when needed.

The laboratory shell keeps its fixed dark theme and Arabic RTL interface. Existing projects retain their visual identity inside the preview. Projects without an identity begin with colors, typography, and direction. Alternatives change the actual page composition or interaction, using the project's content.

![Mokhtabar on desktop](skills/mokhtabar/assets/images/mokhtabar-desktop.png)

### Page-flow canvas

See actual page thumbnails connected by labeled arrows. Move nodes, zoom, open a page separately, inspect its specifications, and leave a note for the agent. Switching between phone and desktop changes the page viewport dimensions.

![Page-flow canvas with labeled arrows](skills/mokhtabar/assets/images/mokhtabar-flow.png)

[All screenshots with Arabic and English captions](docs/SCREENSHOTS.md) · [Image gallery](docs/GALLERY.html) · [Interactive HTML example](docs/preview.html)

## Installation and use

Download the [Mokhtabar ZIP](packages/mokhtabar-v4.0.0.zip). Extract the complete `mokhtabar` folder into your agent's skill directory:

| Agent | Common directory |
| --- | --- |
| Codex | `~/.agents/skills/mokhtabar/` |
| Claude Code | `~/.claude/skills/mokhtabar/` |
| Other agents | Use the directory documented by the tool |

```text
Use Mokhtabar for [my project or idea].
Prepare the relevant questions automatically and apply alternatives to the project's actual content.
Include the page-flow canvas, my notes, and a copyable implementation brief.
```

Building requires Python 3.10+ with no additional libraries. Open the resulting HTML in a modern browser. Its resources are embedded for offline use.

```bash
git clone https://github.com/genius000-king/skills.git
cd skills
python skills/mokhtabar/scripts/build.py skills/mokhtabar/assets/example-project.json --out lab.html
```

See the [skill guide](skills/mokhtabar/README.en.md) and [installation instructions](skills/mokhtabar/INSTALL.en.md).

## Repository structure

- `skills/`: skill instructions, templates, and resources.
- `packages/`: standalone ZIPs and SHA256 checksums.
- `docs/`: laboratory screenshots and a neutral example.
- [catalog.json](catalog.json): skill catalog.
- [CONTRIBUTING.en.md](CONTRIBUTING.en.md): adding or updating a skill.

## Preview limits

The agent prepares questions and conditional branches before building the HTML; there is no live AI model inside it. Previews demonstrate design and navigation. The example login simulates navigation, not authentication. Motion/video workflows show simulations and production specifications, not rendered video files. Screenshots use neutral content and contain no client projects or test reports. English documentation describes the Arabic interface; an English UI is not included.

## License

[MIT](LICENSE) for code and instructions. Bundled IBM Plex and Noto fonts use SIL OFL; their licenses are included.
