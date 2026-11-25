#!/usr/bin/env python3
"""Generate a local browser image-annotation editor from a template."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


DEFAULT_ITEMS = [
    {
        "id": "leftArc",
        "name": "left angle arc",
        "type": "arc",
        "x": 1684,
        "y": 2220,
        "radius": 240,
        "start": 234,
        "sweep": 36,
        "color": "#f6e812",
        "width": 7,
    },
    {
        "id": "rightArc",
        "name": "right angle arc",
        "type": "arc",
        "x": 1684,
        "y": 2220,
        "radius": 240,
        "start": 270,
        "sweep": 38,
        "color": "#f6e812",
        "width": 7,
    },
    {
        "id": "leftAngle",
        "name": "-5 degree label",
        "type": "text",
        "text": "-5°",
        "x": 1460,
        "y": 2112,
        "fontSize": 54,
        "color": "#ffffff",
        "width": 8,
    },
    {
        "id": "rightAngle",
        "name": "+5 degree label",
        "type": "text",
        "text": "+5°",
        "x": 1778,
        "y": 2112,
        "fontSize": 54,
        "color": "#ffffff",
        "width": 8,
    },
    {
        "id": "leftDistance",
        "name": "left 4 m",
        "type": "text",
        "text": "4 m",
        "x": 1352,
        "y": 2102,
        "fontSize": 50,
        "color": "#ffffff",
        "width": 8,
    },
    {
        "id": "rightDistance",
        "name": "right 4 m",
        "type": "text",
        "text": "4 m",
        "x": 1962,
        "y": 2102,
        "fontSize": 50,
        "color": "#ffffff",
        "width": 8,
    },
]


def rel_url(path: Path, base_dir: Path) -> str:
    rel = os.path.relpath(path, base_dir)
    return rel.replace(os.sep, "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draggable image annotation editor HTML.")
    parser.add_argument("--image", required=True, help="Source image path.")
    parser.add_argument("--output", required=True, help="Output HTML path.")
    parser.add_argument("--items-json", help="Optional JSON file containing overlay items.")
    parser.add_argument("--title", default="图片标注编辑器", help="Editor page title.")
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    skill_dir = Path(__file__).resolve().parents[1]
    template_path = skill_dir / "assets" / "editor-template.html"
    template = template_path.read_text(encoding="utf-8")

    if args.items_json:
        items = json.loads(Path(args.items_json).read_text(encoding="utf-8"))
    else:
        items = DEFAULT_ITEMS

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_url = rel_url(image_path, output_path.parent)
    html = (
        template.replace("__TITLE__", args.title)
        .replace("__IMAGE_SRC__", image_url)
        .replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False, indent=2))
    )
    output_path.write_text(html, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
