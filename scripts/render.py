#!/usr/bin/env python3
"""Render a resume YAML data file to HTML using Jinja2 templates."""

import argparse
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
FONTS_CSS = PROJECT_ROOT / "fonts" / "fonts.css"


def format_date(value: str) -> str:
    if not value:
        return ""
    for fmt, out in [
        ("%Y-%m-%d", "%b %Y"),
        ("%Y-%m", "%b %Y"),
        ("%Y", "%Y"),
    ]:
        try:
            return datetime.strptime(value, fmt).strftime(out)
        except ValueError:
            continue
    return value


def strip_scheme(url: str) -> str:
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            return url[len(prefix):]
    return url


def build_jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    env.filters["format_date"] = format_date
    env.filters["strip_scheme"] = strip_scheme
    return env


def render_html(
    data: dict,
    template_name: str = "resume.html",
    theme: str = "modern",
) -> str:
    env = build_jinja_env()
    template = env.get_template(template_name)
    return template.render(
        data=data,
        fonts_css_path=str(FONTS_CSS),
        base_css_path=str(TEMPLATES_DIR / "styles" / "base.css"),
        theme_css_path=str(TEMPLATES_DIR / "styles" / f"{theme}.css"),
    )


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Render resume YAML to HTML")
    parser.add_argument("--data", required=True, help="Path to resume YAML file")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--template", default="resume.html", help="Template file name")
    parser.add_argument("--theme", default="modern", help="Theme CSS name (without .css)")
    args = parser.parse_args()

    data = load_yaml(args.data)
    html = render_html(data, template_name=args.template, theme=args.theme)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"Rendered: {output_path}")


if __name__ == "__main__":
    main()
