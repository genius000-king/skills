# Contributing skills

[العربية](CONTRIBUTING.md) · [English](CONTRIBUTING.en.md)

Add a skill to the catalog only after its files are complete. Follow the [Agent Skills specification](https://agentskills.io/specification).

```text
skills/<skill-id>/
  SKILL.md
  README.md
  README.en.md
  LICENSE
  scripts/
  assets/
  references/
```

Use a lowercase Latin identifier with digits and hyphens. Match the folder name to the frontmatter `name`. A localized display name can be stored in `metadata.display-name`.

1. Choose or add an appropriate category in catalog.json.
2. Include all required resources; avoid references to your local machine.
3. Document purpose, installation, invocation, requirements, practical limits, and licenses.
4. Use neutral screenshots of the skill. Do not publish client data or secrets.
5. Add a standalone skill ZIP to packages/ and update SHA256SUMS.
6. Update the catalog and README links while preserving other skills.
7. Open a Pull Request describing the change and relevant verification.

## Updating Mokhtabar

Project data varies; the laboratory shell stays fixed. Do not rewrite the shell or its colors for each project. An intentional change to the skill source requires a release version, updated documentation, screenshots, package, and checksum. Do not change a checksum to conceal an unintended edit.

Public material should contain neutral examples and screenshots of the feature, without client test projects or development-session reports.
