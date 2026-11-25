---
name: ke-bian-ji-tu
description: Create a local browser-based editable image annotation tool for experiment photos, paper figures, screenshots, and diagrams. Use when the user wants to edit labels, arrows, lines, arcs, distance markers, angle markers, callouts, or other figure annotations interactively inside Codex instead of repeatedly asking the agent to redraw a static image.
---

# Editable Image Annotation

Use this skill to turn a static image into a local, draggable annotation editor. The core method is: keep the original image unchanged, render it as a canvas background, place editable annotation objects above it, then export a full-resolution PNG after manual adjustment.

The user-facing Chinese name for this skill is "ke bian ji tu" / "editable image".

## Workflow

1. Identify the source image path and the annotation types the user needs.
2. Generate an editor HTML with:
   - the source image as the immutable background;
   - editable overlay objects such as text, lines, arrows, arcs, rectangles, and circles;
   - a right-side property panel for position, text, color, line width, font size, and arc angles;
   - an export button that renders the original-resolution image plus current overlay.
3. Start a local HTTP server from the output directory before opening the editor. Prefer HTTP over `file://` because browser canvas export can be blocked or tainted when local images are loaded directly.
4. Give the user the localhost URL and explain that they can drag objects directly on the canvas and export PNG when done.

## Quick Start

Run the bundled script:

```powershell
python C:\Users\67423\.codex\skills\ke-bian-ji-tu\scripts\create_editable_image.py `
  --image "C:\path\to\figure.jpg" `
  --output "C:\path\to\editable-figure.html"
```

Then start a server in the output folder:

```powershell
python -m http.server 8767 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8767/editable-figure.html
```

## Annotation Defaults

For paper experiment photos, default to a small set of editable objects instead of overbuilding the UI:

- angle labels: `-5 deg`, `+5 deg` or exact degree symbols if the figure needs them;
- distance labels: `4 m`, `4 m`;
- two arc objects for angle marks;
- optional line/arrow objects only when the image does not already contain them.

If the user says the existing lines are already correct, do not create new line objects. Add only the requested editable text and arcs.

## Implementation Notes

- Use `assets/editor-template.html` through `scripts/create_editable_image.py`.
- Store overlay objects as JSON inside the generated HTML so the user can edit without extra files.
- Keep coordinates in original image pixels. Display scaling should not change export resolution.
- Export by drawing the original image at natural resolution and then drawing overlays at scale `1`.
- Add selected-element outlines only in the editor preview; do not include them in exported PNG.

## Typical User Requests

- "Make this figure editable so I can drag the labels myself."
- "Create an editor where I can adjust the plus/minus 5 degree labels and 4 m labels."
- "Do not redraw the existing lines; only let me drag arcs and text."
- "Create an editable annotation layer for this experiment photo and export a high-resolution PNG."
