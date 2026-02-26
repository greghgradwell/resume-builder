# Multi-Template System Design

## Problem

The resume builder has a single hardcoded layout. Different job applications may call for different visual presentations, and there's no way to switch between them.

## Design

### Template Structure

Each template is a self-contained subfolder under `templates/`. Shared infrastructure lives at the `templates/` root.

```
templates/
  base.html           ← shared HTML skeleton (Jinja2 base, renamed from current base.html)
  base.css            ← shared structural CSS (moved up from styles/)
  modern/
    resume.html       ← extends base.html, migrated from templates/resume.html
    style.css         ← migrated from templates/styles/modern.css
    meta.yaml         ← template name and description
```

`meta.yaml` format:
```yaml
name: Modern
description: Clean single-column with Montserrat headings and blue accents
```

Adding a new template = drop a new folder in `templates/`. No registry to update.

### Jinja2 Loader

`render.py` will configure `FileSystemLoader` with two search paths: the template subfolder first, then the `templates/` root. This lets `resume.html` find `base.html` via `{% extends "base.html" %}` without any path changes in the templates themselves.

```python
FileSystemLoader([str(TEMPLATES_DIR / template_name), str(TEMPLATES_DIR)])
```

### Interactive CLI

On first run (no sidecar found), `generate.py` prompts interactively:

```
Available templates:

  1. modern    — Clean single-column with Montserrat headings and blue accents
  2. minimal   — Single-column, plain black & white, ATS-optimized

Select template [1]: _
Output path [jobs/audi/adas/resume.pdf]: _

Saving settings to jobs/audi/adas/.generate.yaml
```

On subsequent runs, the sidecar is read and the prompt is skipped:

```
Using saved settings (.generate.yaml):
  template: modern
  output:   jobs/audi/adas/resume.pdf
```

`--reconfigure` flag forces the prompt to re-appear even when a sidecar exists.

### Sidecar File

`.generate.yaml` lives next to `tailored.yaml` in the job directory:

```yaml
template: modern
output: resume.pdf   # relative to the tailored.yaml directory
```

### Removed

- `--theme` and `--template` CLI flags on `generate.py` (replaced by interactive flow)
- `templates/styles/` directory (base.css moves up, modern.css moves into `templates/modern/`)
