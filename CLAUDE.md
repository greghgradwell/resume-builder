# Resume Builder

## Project Structure
- `data/resume.yaml` — Master resume data (single source of truth)
- `INSTRUCTIONS.md` — AI tailoring instructions (READ THIS for resume generation tasks)
- `scripts/render.py` — HTML rendering
- `scripts/pdf.py` — PDF generation
- `scripts/generate.py` — Combined render + PDF
- `scripts/fetch_fonts.py` — Font downloader
- `templates/` — Jinja2 HTML templates and CSS
- `fonts/` — Self-hosted font files (TTF/WOFF2)
- `jobs/` — Generated resumes organized by company/role

## Resume Tailoring Workflow
When asked to tailor a resume, ALWAYS read INSTRUCTIONS.md first and follow it exactly.

## Adding a New Work Experience
When asked to add a new job or work experience, ALWAYS read ADDING_EXPERIENCE.md first and follow it exactly.

## Commands
- `python scripts/fetch_fonts.py` — Download/update Google Fonts
- `python scripts/generate.py --data <yaml> --output <path>` — Generate PDF from YAML
- `python scripts/render.py --data <yaml> --output <path>` — Render HTML only
- `python scripts/pdf.py --input <html> --output <path>` — Convert HTML to PDF

## Conventions
- Python 3.10+, virtual environment at `~/.venvs/resume-builder`
- No docstrings unless logic is non-obvious
- Functions and arguments should be self-documenting via naming
- No fallback behavior — code works or fails explicitly
