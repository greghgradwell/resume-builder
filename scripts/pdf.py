#!/usr/bin/env python3
"""Convert a rendered HTML resume to PDF using WeasyPrint."""

import argparse
from pathlib import Path

from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONTS_CSS = PROJECT_ROOT / "fonts" / "fonts.css"


def generate_pdf(html_path: str | Path, output_path: str | Path) -> int:
    font_config = FontConfiguration()
    font_css = CSS(
        filename=str(FONTS_CSS),
        font_config=font_config,
        base_url=str(PROJECT_ROOT),
    )
    rendered = HTML(filename=html_path, base_url=str(PROJECT_ROOT)).render(
        stylesheets=[font_css],
        font_config=font_config,
    )
    rendered.write_pdf(output_path)
    return len(rendered.pages)


def main():
    parser = argparse.ArgumentParser(description="Convert HTML resume to PDF")
    parser.add_argument("--input", required=True, help="Input HTML file path")
    parser.add_argument("--output", required=True, help="Output PDF file path")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pages = generate_pdf(args.input, str(output_path))
    print(f"Generated: {output_path} ({pages} page{'s' if pages != 1 else ''})")


if __name__ == "__main__":
    main()
