# Multi-Template System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure the template system so multiple named templates (each with their own HTML layout + CSS) live in subfolders, and `generate.py` prompts interactively to pick one, saving the choice to a `.generate.yaml` sidecar for re-runs.

**Architecture:** Each template is a self-contained folder under `templates/` with `resume.html`, `style.css`, and `meta.yaml`. Shared infrastructure (`base.html`, `base.css`) stays at `templates/` root. `render.py` uses a two-path Jinja2 `FileSystemLoader` so templates can `{% extends "base.html" %}` without path changes. `generate.py` replaces its `--output`/`--theme` flags with an interactive prompt that reads/writes `.generate.yaml` next to `tailored.yaml`.

**Tech Stack:** Python 3.10+, Jinja2, PyYAML, WeasyPrint, pytest. Venv at `~/.venvs/resume-builder`. Run all commands with venv activated: `source ~/.venvs/resume-builder/bin/activate`.

---

### Task 1: Set up pytest

**Files:**
- Create: `pyproject.toml`
- Create: `tests/__init__.py` (empty)

**Step 1: Create pyproject.toml**

```toml
[tool.pytest.ini_options]
pythonpath = ["scripts"]
testpaths = ["tests"]
```

**Step 2: Create the tests directory**

```bash
mkdir tests && touch tests/__init__.py
```

**Step 3: Verify pytest discovers tests**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest --collect-only
```

Expected: `no tests ran` (no test files yet) — confirms config is valid.

**Step 4: Commit**

```bash
git add pyproject.toml tests/__init__.py
git commit -m "chore: add pytest config"
```

---

### Task 2: Reorganize template files

Migrate existing flat files into the new folder structure. No Python code changes yet.

**Files:**
- Create: `templates/modern/meta.yaml`
- Move: `templates/resume.html` → `templates/modern/resume.html`
- Move: `templates/styles/modern.css` → `templates/modern/style.css`
- Move: `templates/styles/base.css` → `templates/base.css`
- Delete: `templates/styles/` directory

**Step 1: Create the modern template folder and meta.yaml**

```bash
mkdir templates/modern
```

```yaml
# templates/modern/meta.yaml
name: Modern
description: Clean single-column with Montserrat headings and blue accents
```

**Step 2: Move files using git mv (preserves history)**

```bash
git mv templates/resume.html templates/modern/resume.html
git mv templates/styles/modern.css templates/modern/style.css
git mv templates/styles/base.css templates/base.css
rmdir templates/styles
```

**Step 3: Verify structure**

```bash
find templates/ -type f | sort
```

Expected output:
```
templates/base.css
templates/base.html
templates/modern/meta.yaml
templates/modern/resume.html
templates/modern/style.css
```

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: reorganize templates into per-template subfolders"
```

---

### Task 3: Update render.py + base.html

**Files:**
- Modify: `scripts/render.py`
- Modify: `templates/base.html`
- Create: `tests/test_render.py`

**Step 1: Write failing tests**

```python
# tests/test_render.py
from pathlib import Path
import pytest
from render import render_html, load_yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_render_html_contains_name():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert data["basics"]["name"] in html


def test_render_html_links_style_css():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert "modern/style.css" in html


def test_render_html_links_base_css():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert "templates/base.css" in html


def test_render_html_unknown_template_raises():
    with pytest.raises(Exception):
        render_html({}, template="nonexistent")
```

**Step 2: Run tests — confirm they fail**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest tests/test_render.py -v
```

Expected: 4 failures (render_html still uses old signature).

**Step 3: Update render.py**

Replace the full file content:

```python
#!/usr/bin/env python3
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


def build_jinja_env(template_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader([str(template_dir), str(TEMPLATES_DIR)]),
        autoescape=False,
    )
    env.filters["format_date"] = format_date
    env.filters["strip_scheme"] = strip_scheme
    return env


def render_html(data: dict, template: str = "modern") -> str:
    template_dir = TEMPLATES_DIR / template
    env = build_jinja_env(template_dir)
    tmpl = env.get_template("resume.html")
    return tmpl.render(
        data=data,
        fonts_css_path=str(FONTS_CSS),
        base_css_path=str(TEMPLATES_DIR / "base.css"),
        style_css_path=str(template_dir / "style.css"),
    )


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Render resume YAML to HTML")
    parser.add_argument("--data", required=True, help="Path to resume YAML file")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--template", default="modern", help="Template name (folder in templates/)")
    args = parser.parse_args()

    data = load_yaml(args.data)
    html = render_html(data, template=args.template)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"Rendered: {output_path}")


if __name__ == "__main__":
    main()
```

**Step 4: Update base.html — rename theme_css_path → style_css_path**

In `templates/base.html`, change:
```html
  <link rel="stylesheet" href="{{ theme_css_path }}">
```
to:
```html
  <link rel="stylesheet" href="{{ style_css_path }}">
```

**Step 5: Run tests — confirm they pass**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest tests/test_render.py -v
```

Expected: 4 PASSED.

**Step 6: Commit**

```bash
git add scripts/render.py templates/base.html tests/test_render.py
git commit -m "feat: update render.py for per-template subfolder layout"
```

---

### Task 4: Update generate.py

**Files:**
- Modify: `scripts/generate.py`
- Create: `tests/test_generate.py`

**Step 1: Write failing tests for the helper functions**

```python
# tests/test_generate.py
from pathlib import Path
import yaml
import pytest
from generate import load_sidecar, save_sidecar, list_templates


def test_load_sidecar_returns_none_when_missing(tmp_path):
    assert load_sidecar(tmp_path / "tailored.yaml") is None


def test_load_sidecar_returns_dict_when_present(tmp_path):
    (tmp_path / ".generate.yaml").write_text("template: modern\noutput: resume.pdf\n")
    result = load_sidecar(tmp_path / "tailored.yaml")
    assert result == {"template": "modern", "output": "resume.pdf"}


def test_save_sidecar_writes_correct_yaml(tmp_path):
    save_sidecar(tmp_path / "tailored.yaml", "modern", "resume.pdf")
    content = yaml.safe_load((tmp_path / ".generate.yaml").read_text())
    assert content == {"template": "modern", "output": "resume.pdf"}


def test_list_templates_includes_modern():
    templates = list_templates()
    names = [t["name"] for t in templates]
    assert "modern" in names


def test_list_templates_have_description():
    for t in list_templates():
        assert "description" in t and t["description"]
```

**Step 2: Run tests — confirm they fail**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest tests/test_generate.py -v
```

Expected: 5 failures (helpers don't exist yet).

**Step 3: Replace generate.py**

```python
#!/usr/bin/env python3
import argparse
import tempfile
from pathlib import Path

import yaml

from pdf import generate_pdf
from render import load_yaml, render_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SIDECAR_NAME = ".generate.yaml"


def list_templates() -> list[dict]:
    templates = []
    for d in sorted(TEMPLATES_DIR.iterdir()):
        meta_file = d / "meta.yaml"
        if d.is_dir() and meta_file.exists():
            meta = yaml.safe_load(meta_file.read_text())
            templates.append({"name": d.name, **meta})
    return templates


def load_sidecar(data_path: Path) -> dict | None:
    sidecar = data_path.parent / SIDECAR_NAME
    if sidecar.exists():
        return yaml.safe_load(sidecar.read_text())
    return None


def save_sidecar(data_path: Path, template: str, output: str) -> None:
    sidecar = data_path.parent / SIDECAR_NAME
    sidecar.write_text(yaml.dump({"output": output, "template": template}))


def prompt_settings(data_path: Path) -> tuple[str, Path]:
    templates = list_templates()
    print("\nAvailable templates:\n")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t['name']:<12} — {t['description']}")

    while True:
        raw = input("\nSelect template [1]: ").strip() or "1"
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(templates):
                chosen = templates[idx]["name"]
                break
        except ValueError:
            pass
        print(f"  Enter a number between 1 and {len(templates)}.")

    default_output = data_path.parent / "resume.pdf"
    raw_output = input(f"Output path [{default_output}]: ").strip()
    output_path = Path(raw_output) if raw_output else default_output

    return chosen, output_path


def main():
    parser = argparse.ArgumentParser(description="Generate PDF resume from YAML")
    parser.add_argument("--data", required=True, help="Path to resume YAML file")
    parser.add_argument("--reconfigure", action="store_true", help="Re-prompt even if .generate.yaml exists")
    parser.add_argument("--keep-html", action="store_true", help="Also save the HTML alongside the PDF")
    args = parser.parse_args()

    data_path = Path(args.data).resolve()
    sidecar = None if args.reconfigure else load_sidecar(data_path)

    if sidecar:
        template = sidecar["template"]
        output_path = data_path.parent / sidecar["output"]
        print(f"\nUsing saved settings ({SIDECAR_NAME}):")
        print(f"  template: {template}")
        print(f"  output:   {output_path}\n")
    else:
        template, output_path = prompt_settings(data_path)
        save_sidecar(data_path, template, output_path.name)
        print(f"\nSaved settings to {data_path.parent / SIDECAR_NAME}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_yaml(str(data_path))
    html = render_html(data, template=template)

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
```

**Step 4: Run tests — confirm they pass**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest tests/test_generate.py -v
```

Expected: 5 PASSED.

**Step 5: Run the full test suite**

```bash
source ~/.venvs/resume-builder/bin/activate && pytest -v
```

Expected: 9 PASSED, 0 failed.

**Step 6: Commit**

```bash
git add scripts/generate.py tests/test_generate.py
git commit -m "feat: add interactive template selection and .generate.yaml sidecar"
```

---

### Task 5: Smoke test + update docs

**Step 1: Delete any existing .generate.yaml for example job (to test first-run prompt)**

```bash
rm -f jobs/example/software-engineer/.generate.yaml
```

**Step 2: Run generate.py interactively**

```bash
source ~/.venvs/resume-builder/bin/activate && python scripts/generate.py --data jobs/example/software-engineer/tailored.yaml --keep-html
```

Expected prompt:
```
Available templates:

  1. modern       — Clean single-column with Montserrat headings and blue accents

Select template [1]:
Output path [.../resume.pdf]:
```

Enter `1` and accept the default output path.

**Step 3: Verify PDF was generated**

```bash
pdfinfo jobs/example/software-engineer/resume.pdf
```

Expected: `Pages: 1` or `Pages: 2`.

**Step 4: Run generate.py again (sidecar re-run)**

```bash
source ~/.venvs/resume-builder/bin/activate && python scripts/generate.py --data jobs/example/software-engineer/tailored.yaml
```

Expected: skips prompt, prints `Using saved settings (.generate.yaml)`.

**Step 5: Update INSTRUCTIONS.md — replace generate command**

In `INSTRUCTIONS.md` section 6b, replace:
```bash
python scripts/generate.py \
  --data jobs/<company>/<role>/tailored.yaml \
  --output jobs/<company>/<role>/resume.pdf \
  --keep-html
```
with:
```bash
python scripts/generate.py --data jobs/<company>/<role>/tailored.yaml --keep-html
# First run: prompts for template selection and output path, saves to .generate.yaml
# Subsequent runs: uses saved settings automatically
# To change template: add --reconfigure flag
```

**Step 6: Update CLAUDE.md — fix generate command**

In `CLAUDE.md` under `## Commands`, replace the generate line with:
```
- `python scripts/generate.py --data <yaml> [--keep-html] [--reconfigure]` — Generate PDF (interactive on first run)
```

**Step 7: Commit**

```bash
git add INSTRUCTIONS.md CLAUDE.md jobs/example/software-engineer/.generate.yaml
git commit -m "docs: update generate command docs for interactive template selection"
```
