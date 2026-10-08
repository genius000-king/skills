# Mokhtabar — مختبر

[العربية](README.md) · [English](README.en.md)

One question, its alternatives, and one preview. The agent prepares questions for your project; you answer and press Next. The laboratory shell has a fixed dark theme. The project inside it keeps its own visual identity.

![Desktop decision workspace](assets/images/mokhtabar-desktop.png)

## Workflow

1. Start answering immediately, without selecting question categories or phases.
2. Compare real alternatives applied to the project's content; add notes when needed.
3. Continue through the relevant questions and conditional branches.
4. Review decisions and copy the implementation brief. Download JSON, HTML, or text when needed.

On phones, questions and options appear first and Next stays at the bottom. Page tools and details are available in the ⋯ menu.

## Page-flow canvas

Actual page thumbnails connect through arrows labeled with navigation actions. Move nodes, zoom, and open a page separately to see its design, specifications, and notes. Previews use the selected phone or desktop viewport dimensions.

![Connected pages](assets/images/mokhtabar-flow.png)

[Phone interface](assets/images/mokhtabar-mobile.png) · [Phone-sized pages on the canvas](assets/images/mokhtabar-flow-phone-pages.png) · [Page specifications and notes](assets/images/mokhtabar-page-detail-desktop.png)

## Installation and building

Copy this entire folder into your agent's skill directory. Read [INSTALL.en.md](INSTALL.en.md) and [SKILL.md](SKILL.md). Ask: “Use Mokhtabar for my project and prepare the relevant questions automatically.”

```bash
python scripts/build.py project.json --out lab.html
python scripts/build.py project.json --selection choices.json --out lab.html
```

Release 4.0.0. Python 3.10+ and a modern browser; no additional libraries. Data contract version 3 retains support for versions 1 and 2.

## What the agent prepares

- Existing projects: source-based previews that preserve colors, typography, and content.
- Missing visual identity: colors, typography, and direction first, then structure and interaction decisions.
- Websites/apps: composition, navigation, components, and motion applied to actual pages.
- Motion/video, plans, and explanations: relevant decisions, content, and domain-specific previews; no unrelated questions.

## Changes in 4.0.0

Phase selectors and question-index buttons were removed from the answering journey. One preview remains, with optional notes and tools. Selecting an option keeps the question in view. Conditional branches, local saving, alternative/page notes, and exports remain available.

## Practical limits

The agent prepares questions and branches before building. The HTML does not run an AI model or generate new questions at runtime. Written ideas are passed back to the agent; they are not redrawn automatically. Saving is local. Send the brief or JSON to your agent to implement your decisions. The example login only demonstrates navigation; the HTML does not authenticate users, implement backend services, or render video files.

The example and screenshots use neutral content to show the skill, not client projects or test reports. Documentation is bilingual; the fixed interface remains Arabic and RTL.

See the [data contract](references/v3-contract.md) and [quality checks](references/quality.md). [MIT](LICENSE), with bundled font licenses.
