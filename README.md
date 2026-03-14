# Resume Builder

A YAML-based resume builder with AI-assisted tailoring. Maintain a single master resume with tagged, prioritized bullets — then use any AI CLI tool (Claude Code, Gemini CLI, Cursor, etc.) to select the best bullets for each job application and generate a polished PDF.

## How It Works

1. **Master resume** (`data/resume.yaml`) — all your experience, skills, education, and publications in one file. Each bullet has a unique ID, tags, and a priority level.
2. **Tailoring** — an AI assistant reads a job description, selects relevant bullets by ID, and writes a lightweight `tailored.yaml` that references the master.
3. **PDF generation** — `generate.py` resolves the references, renders HTML via Jinja2 templates, and converts to PDF with WeasyPrint.

You never edit bullet text in tailored files. The master is the single source of truth.

## Quick Start

```bash
# Clone and set up
git clone <repo-url> && cd resume-builder
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Install WeasyPrint system dependencies (Ubuntu/Debian)
sudo apt install libpango1.0-dev libharfbuzz-dev libffi-dev

# Download fonts
python scripts/fetch_fonts.py

# Populate your resume
# Edit data/resume.yaml with your real information (see the example data for structure)

# Generate a PDF from the example
python scripts/generate.py --data jobs/example/software-engineer/tailored.yaml --keep-html
```

## Project Structure

```
data/resume.yaml                  # Master resume (single source of truth)
jobs/<company>/<role>/
  tailored.yaml                   # AI-generated subset referencing master bullet IDs
  .generate.yaml                  # Saved template + output settings
  resume.pdf                      # Generated output (gitignored)
scripts/
  generate.py                     # Main entrypoint: resolve references → HTML → PDF
  render.py                       # Jinja2 HTML rendering
  pdf.py                          # WeasyPrint PDF conversion
  fetch_fonts.py                  # Google Fonts downloader
templates/
  base.html / base.css            # Shared template infrastructure
  modern/                         # "Modern" template (resume.html + style.css + meta.yaml)
fonts/                            # Self-hosted font files (TTF/WOFF2)
INSTRUCTIONS.md                   # AI tailoring workflow
ADDING_EXPERIENCE.md              # AI interview workflow for new bullets
ANALYZING.md                      # AI resume analysis workflow
```

## AI-Assisted Tailoring

The `INSTRUCTIONS.md`, `ADDING_EXPERIENCE.md`, and `ANALYZING.md` files are structured prompts designed for AI CLI tools. They work with any tool that can read files and execute commands:

- **Tailoring** — give your AI assistant a job description and ask it to tailor your resume. It reads `INSTRUCTIONS.md`, selects bullets by ID, and generates a PDF.
- **Adding experience** — ask your AI to help add a new job. It reads `ADDING_EXPERIENCE.md` and runs an interactive interview to draft bullets.
- **Analyzing** — ask your AI to evaluate a tailored resume against a job description. It reads `ANALYZING.md` and produces a coverage report.

Example: `"Tailor my resume for this Software Engineer role at Acme Corp: <paste JD>"`

## Templates

Templates live in `templates/<name>/` with `resume.html`, `style.css`, and `meta.yaml`. The first time you run `generate.py`, it prompts you to pick a template and saves the choice to `.generate.yaml`. Add `--reconfigure` to change templates later.

## Commands

```bash
python scripts/generate.py --data <yaml> [--keep-html] [--reconfigure]  # Generate PDF
python scripts/render.py --data <yaml> --output <path> --template modern # Render HTML only
python scripts/pdf.py --input <html> --output <path>                     # HTML → PDF
python scripts/fetch_fonts.py                                            # Download fonts
```

If you have [just](https://github.com/casey/just) installed:

```bash
just regen      # Regenerate the most recently modified tailored.yaml
just generate <path>  # Generate a specific tailored resume
just fonts      # Fetch/update fonts
```

## Requirements

- Python 3.10+
- WeasyPrint system dependencies ([installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html))
- Packages: `weasyprint`, `jinja2`, `pyyaml` (see `requirements.txt`)

## License

AGPL-3.0 — see [LICENSE](LICENSE).
