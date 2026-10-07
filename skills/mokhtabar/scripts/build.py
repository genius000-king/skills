#!/usr/bin/env python3
"""Validate project data and embed it in the immutable offline lab template."""
import base64
import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        is_slot = any(name == "data-slot" for name, _ in attrs)
        if is_slot and any(has_slot for _, has_slot in self.stack):
            raise ValueError("Slots cannot be nested: use independent sibling slots")
        if tag.lower() in {"script", "iframe", "object", "embed", "link", "base", "meta", "style", "form", "set", "animate", "animatemotion", "animatetransform", "foreignobject"}:
            raise ValueError(f"Forbidden HTML tag: {tag}")
        for name, value in attrs:
            if name.lower().startswith("on") or name.lower() == "srcdoc":
                raise ValueError(f"Forbidden HTML attribute: {name}")
            if name.lower() in {"src", "href", "action", "xlink:href", "srcset"} and value:
                if not value.startswith("#") and not (name.lower()=="src" and tag.lower()=="img" and raster_data(value)):
                    raise ValueError("External/executable resource URLs are not supported")
            if name == "data-slot":
                if not value or not SLUG.fullmatch(value):
                    raise ValueError("Invalid data-slot identifier")
                self.slots.append(value)
        if tag.lower() not in {"area", "br", "col", "hr", "img", "input", "param", "source", "track", "wbr"}:
            self.stack.append((tag.lower(), is_slot))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag.lower():
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def text_field(obj, key, where, allow_empty=False):
    value = obj.get(key)
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{where}.{key} must be {'a string' if allow_empty else 'a nonempty string'}")
    if len(value) > (12_000_000 if key in {"html", "css"} else 200_000):
        raise ValueError(f"{where}.{key} is too large")
    return value


def raster_data(value):
    match = re.fullmatch(r"data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=]+)", value)
    if not match or len(value) > 6_000_000:
        return False
    try:
        raw = base64.b64decode(match[2], validate=True)
        return ((match[1] == "png" and raw.startswith(b"\x89PNG\r\n\x1a\n")) or
                (match[1] == "jpeg" and raw.startswith(b"\xff\xd8\xff")) or
                (match[1] == "gif" and raw.startswith((b"GIF87a", b"GIF89a"))) or
                (match[1] == "webp" and raw.startswith(b"RIFF") and raw[8:12] == b"WEBP"))
    except ValueError:
        return False


def css_check(value, where):
    if not isinstance(value, str):
        raise ValueError(f"{where} must be CSS text")
    def image_url(match):
        if not raster_data(match[2]):
            raise ValueError(f"{where}: invalid embedded raster image")
        return "embedded-image"
    checked = re.sub(r"url\(\s*(['\"]?)(data:image/[^)'\"]+)\1\s*\)", image_url, value, flags=re.I)
    checked = re.sub(r"url\(\s*['\"]?#[a-zA-Z0-9_-]+['\"]?\s*\)", "local-svg-reference", checked)
    if re.search(r"<|@import|url\s*\(|expression\s*\(|javascript\s*:", checked, re.I):
        raise ValueError(f"{where}: remote or executable CSS is unsupported")


def html_check(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where} requires nonempty HTML")
    parser = Markup()
    parser.feed(value)
    if len(parser.slots) != len(set(parser.slots)):
        raise ValueError(f"{where}: duplicate data-slot")
    return set(parser.slots)


def validate(data):
    if not isinstance(data, dict) or data.get("version") not in (1, 2, 3):
        raise ValueError("Expected project object with version: 1, 2, or 3")
    v2 = data["version"] >= 2
    v3 = data["version"] == 3
    phases = set()
    if v2:
        if data.get("domain") not in {"interface", "motion", "video", "planning", "explanation", "mixed"}:
            raise ValueError("Specify a supported domain")
        if not isinstance(data.get("phases"), list) or not 1 <= len(data["phases"]) <= 20:
            raise ValueError("Provide 1–20 meaningful phases")
        for phase in data["phases"]:
            if not isinstance(phase, dict):
                raise ValueError("Each phase must be an object")
            for key in ("id", "title", "description"):
                text_field(phase, key, "phase")
            if not SLUG.fullmatch(phase["id"]) or phase["id"] in phases:
                raise ValueError("Phase IDs must be unique slugs")
            phases.add(phase["id"])
        if not isinstance(data.get("deliverables"), list) or not data["deliverables"] or not all(isinstance(x, str) and x.strip() for x in data["deliverables"]):
            raise ValueError("Specify concrete deliverables")
    if "viewports" in data:
        if not isinstance(data["viewports"], list) or not 1 <= len(data["viewports"]) <= 6:
            raise ValueError("Provide 1–6 viewport formats")
        vids = set()
        for view in data["viewports"]:
            if not isinstance(view, dict):
                raise ValueError("Viewport must be an object")
            for key in ("id", "title"):
                text_field(view, key, "viewport")
            if not SLUG.fullmatch(view["id"]) or view["id"] in vids:
                raise ValueError("Viewport IDs must be unique slugs")
            vids.add(view["id"])
            if any(type(view.get(k)) is not int or not 160 <= view[k] <= 4096 for k in ("width", "height")):
                raise ValueError("Viewport dimensions must be integers from 160 to 4096")
    if "motionDuration" in data and (type(data["motionDuration"]) is not int or not 1600 <= data["motionDuration"] <= 30000):
        raise ValueError("motionDuration must be 1600–30000ms")
    for key in ("id", "title", "brief", "responsive", "css"):
        text_field(data, key, "project")
    if not SLUG.fullmatch(data["id"]):
        raise ValueError("project.id must be a lowercase ASCII slug")
    if "visualStyle" in data:
        text_field(data, "visualStyle", "project")
    for key in ("requirements", "assumptions"):
        if not isinstance(data.get(key), list) or not all(isinstance(v, str) and v.strip() for v in data[key]):
            raise ValueError(f"project.{key} must be an array of nonempty strings")
    if not data["requirements"]:
        raise ValueError("Specify at least one requirement")
    css_check(data["css"], "project.css")
    if not isinstance(data.get("screens"), list) or not 1 <= len(data["screens"]) <= 64:
        raise ValueError("Provide 1–64 scenes, boards, or screens")
    slots = {}
    for screen in data["screens"]:
        if not isinstance(screen, dict):
            raise ValueError("Each screen must be an object")
        for key in ("id", "title", "html"):
            text_field(screen, key, "screen")
        if not SLUG.fullmatch(screen["id"]) or screen["id"] in slots:
            raise ValueError("Screen IDs must be unique slugs")
        slots[screen["id"]] = html_check(screen["html"], "screen.html")
    if not isinstance(data.get("questions"), list) or not (8 if v2 else 3) <= len(data["questions"]) <= 200:
        raise ValueError("Provide 8–200 meaningful questions for v2 (3+ for legacy v1)")
    ids, owners = set(), {}
    for q in data["questions"]:
        if not isinstance(q, dict):
            raise ValueError("Each question must be an object")
        for key in ("id", "title", "hint", "screen", "default"):
            text_field(q, key, "question")
        if not SLUG.fullmatch(q["id"]) or q["id"] in ids:
            raise ValueError("Question IDs must be unique slugs")
        ids.add(q["id"])
        if v2:
            for key in ("phase", "recommendation", "impact"):
                text_field(q, key, "question")
            if q["phase"] not in phases:
                raise ValueError(f"{q['id']}: unknown phase")
            if q.get("presentation") not in {"cards", "gallery", "comparison", "storyboard", "timeline", "diagram"}:
                raise ValueError(f"{q['id']}: choose a presentation suited to the decision")
        if q["screen"] not in slots:
            raise ValueError(f"{q['id']}: unknown question.screen")
        if not isinstance(q.get("options"), list) or not 3 <= len(q["options"]) <= 8:
            raise ValueError(f"{q['id']}: provide 3–8 options")
        option_ids, concepts, signatures = set(), set(), set()
        expected_pairs = None
        for o in q["options"]:
            if not isinstance(o, dict):
                raise ValueError("Each option must be an object")
            where = f"{q['id']}.{o.get('id', '?')}"
            for key in ("id", "title", "concept", "description", "tradeoff", "implementation"):
                text_field(o, key, where)
            if not SLUG.fullmatch(o["id"]) or o["id"] in option_ids:
                raise ValueError(f"{where}: option IDs must be unique slugs")
            option_ids.add(o["id"])
            concept = o["concept"].strip().casefold()
            if concept in concepts:
                raise ValueError(f"{where}: duplicate idea/concept")
            concepts.add(concept)
            if v2 and (not isinstance(o.get("axes"), list) or not all(isinstance(x, str) and x.strip() for x in o["axes"]) or len(set(o["axes"])) < 2):
                raise ValueError(f"{where}: specify at least two axes of meaningful difference")
            if "visual" in o:
                if not isinstance(o["visual"], dict):
                    raise ValueError(f"{where}: visual must be an object")
                html_check(o["visual"].get("html"), where + ".visual.html")
                css_check(o["visual"].get("css", ""), where + ".visual.css")
            css_check(o.get("css", ""), where + ".css")
            patches = o.get("patches")
            if not isinstance(patches, dict) or not patches:
                raise ValueError(f"{where}: supply real screen patches, not CSS-only variations")
            if q["screen"] not in patches:
                raise ValueError(f"{where}: patch the question's visible screen")
            pairs = set()
            for sid, changes in patches.items():
                if sid not in slots or not isinstance(changes, dict) or not changes:
                    raise ValueError(f"{where}: invalid patched screen")
                for slot, markup in changes.items():
                    if slot not in slots[sid]:
                        raise ValueError(f"{where}: nonexistent slot {sid}/{slot}")
                    if html_check(markup, where + ".patch"):
                        raise ValueError(f"{where}: patches cannot create nested slots")
                    pairs.add((sid, slot))
                    if (sid, slot) in owners and owners[(sid, slot)] != q["id"]:
                        raise ValueError(f"{where}: slot already owned by another question")
            if expected_pairs is None:
                expected_pairs = pairs
            elif pairs != expected_pairs:
                raise ValueError(f"{where}: options must patch identical slot sets")
            for pair in pairs:
                owners[pair] = q["id"]
            sig = json.dumps({"patches": patches, "css": o.get("css", "")} if v3 and q.get("kind") in {"palette", "typography"} else patches, ensure_ascii=False, sort_keys=True)
            if sig in signatures:
                raise ValueError(f"{where}: duplicate visual structure")
            signatures.add(sig)
            preview = o.get("preview")
            if not isinstance(preview, dict):
                raise ValueError(f"{where}: isolated preview required")
            html_check(preview.get("html"), where + ".preview.html")
            if not any(preview["html"].strip() in markup for markup in patches[q["screen"]].values()):
                raise ValueError(f"{where}: isolated preview must reuse a component from the visible screen patch")
            css_check(preview.get("css", ""), where + ".preview.css")
            motion_css = data["css"] + o.get("css", "")
            if re.search(r"(?:animation|transition)\s*:", motion_css) and "prefers-reduced-motion" not in motion_css:
                raise ValueError(f"{where}: motion requires a reduced-motion override")
        if q["default"] not in option_ids:
            raise ValueError(f"{q['id']}: default does not match an option")
    if v2:
        if phases != {q["phase"] for q in data["questions"]}:
            raise ValueError("Every phase needs meaningful questions")
        previous = {}
        for q in data["questions"]:
            when = q.get("when", {})
            if not isinstance(when, dict):
                raise ValueError("when must be a condition object")
            for dependency, values in when.items():
                if dependency not in previous or not isinstance(values, list) or not values or not all(v in previous[dependency] for v in values):
                    raise ValueError(f"{q['id']}: when must reference valid options from earlier questions")
            previous[q["id"]] = {o["id"] for o in q["options"]}
        items = data.get("workItems")
        if not isinstance(items, list) or not items:
            raise ValueError("Provide actionable workItems, not only design choices")
        items = list(items)
        for q in data["questions"]:
            for o in q["options"]:
                if "workItems" in o:
                    if not isinstance(o["workItems"], list):
                        raise ValueError("option.workItems must be a list")
                    items.extend(o["workItems"])
        graph = {}
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("workItem must be an object")
            for key in ("id", "title", "phase", "description", "acceptance"):
                text_field(item, key, "workItem")
            if not SLUG.fullmatch(item["id"]) or item["id"] in graph or item["phase"] not in phases:
                raise ValueError("Work items require unique IDs and existing phases")
            if not isinstance(item.get("dependsOn"), list) or not all(isinstance(x, str) for x in item["dependsOn"]):
                raise ValueError("workItem.dependsOn must be a list of IDs")
            graph[item["id"]] = item["dependsOn"]
            when = item.get("when", {})
            if not isinstance(when, dict):
                raise ValueError("workItem.when must be a condition object")
            for dependency, values in when.items():
                if dependency not in previous or not isinstance(values, list) or not values or not all(v in previous[dependency] for v in values):
                    raise ValueError("workItem.when references unknown choices")
        visiting, visited = set(), set()
        def visit(node):
            if node not in graph:
                raise ValueError("Unknown work-item dependency")
            if node in visiting:
                raise ValueError("Circular work-item dependencies")
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph[node]:
                visit(dependency)
            visiting.remove(node)
            visited.add(node)
        for node in graph:
            visit(node)
    if v3:
        validate_v3(data)
    return data


def validate_v3(data):
    source = data.get("source")
    if not isinstance(source, dict) or source.get("mode") not in {"existing", "new"} or source.get("identityStatus") not in {"defined", "undefined"}:
        raise ValueError("v3 requires source.mode and identityStatus")
    text_field(source, "reference", "source")
    if "allowIdentityChange" in source and type(source["allowIdentityChange"]) is not bool:
        raise ValueError("allowIdentityChange must be boolean")
    if source["mode"] == "existing":
        if source.get("fidelity") not in {"source", "reconstructed"}:
            raise ValueError("Existing projects need source/reconstructed fidelity")
        if source["identityStatus"] == "defined":
            identity = source.get("identity", {})
            for key in ("colors", "fonts"):
                if not isinstance(identity.get(key), list) or not identity[key] or not all(isinstance(x,str) and x.strip() for x in identity[key]):
                    raise ValueError("Describe existing colors/fonts in source.identity")
            if not source.get("allowIdentityChange", False) and any(q.get("kind") in {"palette", "typography"} for q in data["questions"]):
                raise ValueError("Preserve defined identity; explicit identity-change authorization required")
    if source["identityStatus"] == "undefined" and data["domain"] in {"interface", "mixed", "motion", "video"}:
        if [q.get("kind") for q in data["questions"][:3]] != ["palette", "typography", "direction"]:
            raise ValueError("Start undefined visual identity with palette, typography and direction")
    options = {q["id"]:{o["id"] for o in q["options"]} for q in data["questions"]}
    def conditions(obj, where):
        when = obj.get("when", {})
        if not isinstance(when, dict):
            raise ValueError(where + ": when must be an object")
        for qid, values in when.items():
            if qid not in options or not isinstance(values,list) or not values or not all(isinstance(v,str) and v in options[qid] for v in values):
                raise ValueError(where + ": invalid choice condition")
    screens = {s["id"] for s in data["screens"]}
    for screen in data["screens"]:
        for key in ("purpose", "route"):
            text_field(screen, key, "screen")
        for key in ("sections", "actions"):
            if not isinstance(screen.get(key),list) or not all(isinstance(x,str) and x.strip() for x in screen[key]):
                raise ValueError("screen.sections/actions must list specifications")
        conditions(screen, "screen")
        if "position" in screen:
            if not isinstance(screen["position"],dict) or any(type(screen["position"].get(k)) not in (int,float) or not 0 <= screen["position"][k] <= 20000 for k in ("x","y")):
                raise ValueError("screen.position must contain nonnegative bounded x/y")
    flow = data.get("flow")
    if data["domain"] in {"interface", "mixed"} and not isinstance(flow,dict):
        raise ValueError("Interface work needs a page flow")
    if flow is not None:
        if not isinstance(flow,dict) or flow.get("entry") not in screens or not isinstance(flow.get("edges"),list):
            raise ValueError("flow needs an existing entry page and edges")
        edge_ids = set()
        for edge in flow["edges"]:
            for key in ("id","from","to","trigger"):
                text_field(edge,key,"flow.edge")
            if not SLUG.fullmatch(edge["id"]) or edge["id"] in edge_ids or edge["from"] not in screens or edge["to"] not in screens:
                raise ValueError("Edges require unique IDs and existing endpoints")
            edge_ids.add(edge["id"]);conditions(edge,"edge")
    for q in data["questions"]:
        if "helper" in q and (not isinstance(q["helper"],str) or len(q["helper"])>120):
            raise ValueError("helper must be brief (120 characters maximum)")
        for o in q["options"]:
            if "caption" in o and (not isinstance(o["caption"],str) or len(o["caption"])>80):
                raise ValueError("caption must be brief (80 characters maximum)")
            if "scope" in o.get("visual",{}) and o["visual"]["scope"] not in {"page","component"}:
                raise ValueError("visual.scope must be page/component")
    if not isinstance(data.get("fonts",[]),list):
        raise ValueError("fonts must be a list")
    for font in data.get("fonts",[]):
        if not isinstance(font,dict) or not isinstance(font.get("family"),str) or not re.fullmatch(r"[A-Za-z0-9 \-\u0600-\u06ff]{1,80}",font["family"]):
            raise ValueError("Font family must be a safe name")
        if font.get("format") not in {"woff2","woff","truetype","opentype"} or not isinstance(font.get("data"),str) or len(font["data"]) > 4_000_000:
            raise ValueError("Provide a local base64 font up to 3MB")
        try:
            raw = base64.b64decode(font["data"], validate=True)
        except ValueError:
            raise ValueError("Invalid font base64")
        signatures={"woff2":b"wOF2","woff":b"wOFF","truetype":b"\x00\x01\x00\x00","opentype":b"OTTO"}
        if not raw.startswith(signatures[font["format"]]):
            raise ValueError("Font format does not match binary")
        if font.get("weight","400") not in {"400","500","600","700","100 900"}:
            raise ValueError("Unsupported font weight")


def build(data):
    validate(data)
    template_bytes = (ROOT / "assets/lab.html").read_bytes()
    expected = (ROOT / "assets/SHELL.sha256").read_text().split()[0]
    if hashlib.sha256(template_bytes).hexdigest() != expected:
        raise ValueError("Canonical lab template changed: restore assets/lab.html; do not redesign the shell")
    template = template_bytes.decode("utf-8")
    if template.count("__PROJECT_JSON__") != 1:
        raise ValueError("Template marker is missing or duplicated")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for char in "<>&":
        encoded = encoded.replace(char, f"\\u{ord(char):04x}")
    return template.replace("__PROJECT_JSON__", encoded)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selection", type=Path, help="Carry compatible choices/notes/ideas into a new round")
    args = ap.parse_args()
    try:
        data = json.loads(args.project.read_text(encoding="utf-8"))
        if args.selection:
            selection = json.loads(args.selection.read_text(encoding="utf-8"))
            if not isinstance(selection, dict) or selection.get("projectId") != data.get("id"):
                raise ValueError("Selection belongs to a different projectId")
            for field in ("choices", "notes", "ideas", "pageNotes", "canvasPositions"):
                if field in selection and not isinstance(selection[field], dict):
                    raise ValueError(f"Selection.{field} must be an object")
            data["initialSelection"] = selection
        validate(data)
        if args.check:
            print(f"Valid: {data['id']} ({len(data['questions'])} questions)")
            return
        if not args.out:
            ap.error("--out is required unless --check is used")
        result = build(data)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result, encoding="utf-8")
        digest = hashlib.sha256((ROOT / "assets/lab.html").read_bytes()).hexdigest()
        print(f"Built {args.out} | canonical shell SHA256: {digest}")
    except (ValueError, OSError, TypeError, KeyError) as err:
        print(f"Build failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
