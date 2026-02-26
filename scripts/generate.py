#!/usr/bin/env python3
"""Generate a PDF resume from a YAML data file in one step."""

import argparse
import tempfile
from pathlib import Path

from pdf import generate_pdf
from render import load_yaml, render_html


def main():
    parser = argparse.ArgumentParser(description="Generate PDF resume from YAML")
    parser.add_argument("--data", required=True, help="Path to resume YAML file")
    parser.add_argument("--output", required=True, help="Output PDF file path")
    parser.add_argument("--theme", default="modern", help="Theme CSS name (without .css)")
    parser.add_argument("--keep-html", action="store_true", help="Also save the HTML alongside the PDF")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_yaml(args.data)
    html = render_html(data, theme=args.theme)

    if args.keep_html:
        html_path = output_path.with_suffix(".html")
        html_path.write_text(html)
        print(f"Rendered:  {html_path}")
        generate_pdf(str(html_path), str(output_path))
    else:
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as tmp:
            tmp.write(html)
            tmp_path = tmp.name
        try:
            generate_pdf(tmp_path, str(output_path))
        finally:
            Path(tmp_path).unlink()

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
