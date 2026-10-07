# Common HTML/CSS contract (v2 extends this in v2-contract.md)

Create UTF-8 JSON. No dependencies, network resources, JS or event handlers in project data.
Read `assets/example-project.json` for a complete neutral example. Keep the shell unchanged.

This snippet illustrates shared fields; a full v2 file adds domain/phases/workItems and question metadata from v2-contract.md.

```json
{
  "version": 1,
  "id": "unique-project-slug",
  "title": "اسم المشروع",
  "brief": "هدف المشروع والجمهور والمهمة الأساسية",
  "assumptions": ["افتراض واضح"],
  "requirements": ["متطلب قابل للتنفيذ"],
  "responsive": "كيف تتغير البنية عند 760px، وكيف تعمل اللمسات ولوحة المفاتيح",
  "visualStyle": "اختياري: وصف هوية المشروع وألوانه الدقيقة إذا طلب المستخدم تنويع الهوية",
  "css": "CSS common to all screens, scoped to the iframe document",
  "screens": [{"id": "home", "title": "الرئيسية", "html": "<main><div data-slot='hero'>Default content</div></main>"}],
  "questions": [{
    "id": "hero", "title": "كيف يبدأ الزائر؟", "hint": "اختر فكرة واضحة",
    "screen": "home", "default": "story",
    "options": [{
      "id": "story", "title": "قصة المشكلة", "concept": "بدء الصفحة بقصة قصيرة",
      "description": "الفكرة وكيف تختلف", "tradeoff": "ما تكسبه وما تتنازل عنه",
      "implementation": "تفاصيل تنفيذ محددة، وليس عنوانًا فقط",
      "css": ".story{display:grid}",
      "patches": {"home": {"hero": "<section class='story'>...</section>"}},
      "preview": {"html": "<section class='story'>...</section>", "css": ""}
    }]
  }]
}
```

For v2 use 3–8 alternatives per question and depth appropriate to the work; see v2-contract.md. Cover information
architecture, navigation, main content, primary action, and animation when relevant.
Each option must provide `preview` with a real isolated component. `preview.css`
is only for positioning in isolation; behavioral CSS belongs to `option.css` so
it is identical in isolation and the assembled site. Include the SAME component
markup/classes in patches and preview. For animations use `data-demo` on the
component; the runtime toggles `data-playing="true"` on `<html>` for 1600ms on
replay and on component click. Also support hover/focus-visible and touch active.
Use CSS selectors such as `html[data-playing='true'] .action`.
Animation definitions MUST include a `prefers-reduced-motion: reduce` override.
The isolated preview inherits `project.css` and the selected `option.css`, then
adds `preview.css`. Use a prefix like `.q-navigation` or `.q-action`; the prefix
need not exactly match the question ID, but must be unique to that question.
Put `data-demo` on the actual interactive button or summary, not only a wrapper.

Each question owns its slots exclusively; separate questions may not overwrite the
same `(screen, slot)` pair. Every option in a question must patch the same slot set
and must materially differ in structure, task flow, or interaction. Use explicit,
different `concept` values. Duplicate concepts, CSS-only alternatives, duplicate
patches, nonexistent slots, or more than one question owning a slot are rejected.
Question CSS selectors must be prefixed by a question-specific class to avoid
changing unrelated components. Dependencies: use `var(--a-bg)`, `--a-fg`,
`--a-muted`, `--a-line`, `--a-card`, `--a-btn`, `--a-btnfg`, `--a-ok`, `--a-warn`,
`--a-bad`; project previews are also dark by default. Do not load assets remotely.
When the user explicitly requests different project colors, redefine `--a-*`
tokens in `project.css` and describe them in `visualStyle`. Those overrides only
affect the sandboxed project; the dark lab shell remains unchanged. Keep IBM Plex
Sans Arabic and verify contrast for every foreground/background pair.

Choose viewports suited to the domain. Interfaces use mobile/desktop responsive layouts; video uses aspect ratios and storyboards; plans/explanations use readable boards and diagrams. Frames render at actual configured dimensions and scale to fit their shell box. Review unscaled views too.

No `<script>`, iframe, external CSS, form submission, executable SVG, or event
attributes. Render honest UI prototypes; project-specific actions are specified
in export, not connected to real backends. Navigation between screen previews is
via the shell screen selector. Dynamic CSS-only details/disclosure are allowed.
Escape arbitrary user text as text. JSON strings containing closing script tags
must be embedded by the build script, never pasted into the template by hand.
