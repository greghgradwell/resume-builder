# Resume Builder

## Project Structure
- `data/comprehensive_bio.yaml` — Master resume data (single source of truth)
- `INSTRUCTIONS.md` — AI tailoring instructions (READ THIS for resume generation tasks)
- `scripts/render.py` — HTML rendering
- `scripts/pdf.py` — PDF generation
- `scripts/generate.py` — Combined render + PDF
- `scripts/fetch_fonts.py` — Font downloader
- `templates/` — Jinja2 HTML templates and CSS
- `fonts/` — Self-hosted font files (TTF/WOFF2)
- `data/jobs/` — Generated resumes organized by company/role
- `data/jobs/<company>/<role>/.generate.yaml` — Sidecar: saved template + output path (commit this)

## Resume Tailoring Workflow
When asked to tailor a resume, ALWAYS read INSTRUCTIONS.md first and follow it exactly.

## Adding a New Work Experience
When asked to add a new job or work experience, ALWAYS read ADDING_EXPERIENCE.md first and follow it exactly.

## Analyzing a Tailored Resume
When asked to analyze or evaluate a resume against a job description, ALWAYS read ANALYZING.md first and follow it exactly.

## Importing an Existing Resume
When asked to import, convert, or populate a resume from a PDF, text, or LinkedIn export, ALWAYS read IMPORT_EXISTING.md first and follow it exactly.

## Commands
- `python scripts/fetch_fonts.py` — Download/update Google Fonts
- `python scripts/generate.py --data <yaml> [--keep-html] [--reconfigure]` — Generate PDF (interactive on first run)
- `python scripts/render.py --data <yaml> --output <path>` — Render HTML only
- `python scripts/pdf.py --input <html> --output <path>` — Convert HTML to PDF

## Conventions
- Python 3.10+, virtual environment (location chosen during installation)
- No docstrings unless logic is non-obvious
- Functions and arguments should be self-documenting via naming
- No fallback behavior — code works or fails explicitly
