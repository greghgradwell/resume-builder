# Resume Builder

## The Problem

Over your career, you've probably written several resumes — each tailored for a different job, each cutting some experience to make room for other things. No single document has everything, and rebuilding from scratch every time means starting from an incomplete picture. Plus, formatting in a document editor is painful.

## The Solution

A resume builder designed for use with AI CLI tools (Claude Code, Gemini CLI, Cursor, etc.). Feed in your existing resumes, and the AI aggregates them into a single master file — preserving your original wording. When applying for a job, the AI can help you select the most relevant bullets and generates a tailored PDF.

You can't have AI slop if it's all your own words (if you write like a bot, I can't help you).

## How It Works

1. **Import** — feed your existing resumes (PDFs, text, multiple files) to the AI. It extracts everything into a single master YAML file (`data/resume.yaml`) with tagged, prioritized bullets. Your original wording is preserved — the AI structures, it doesn't rewrite.
2. **Add** — when you start a new job, the AI interviews you and helps you shape bullets. It's a copy editor, not a ghostwriter — you provide the words, it helps with structure and consistency.
3. **Tailor** — paste a job description and ask the AI to tailor your resume. It selects the most relevant bullets by ID, orders them, and writes a lightweight reference file.
4. **Generate** — the tool resolves references, renders HTML via Jinja2 templates, and produces a PDF with WeasyPrint.

The boundary is simple: your *content* is sacred — your claims, your phrasing, your voice. The AI handles *organization* — categorizing skills, selecting bullets, ordering sections, formatting output. The result sounds like you because every word is yours.

## Installation

> **For the AI assistant:** follow these steps to set up the project. Ask the user for confirmation before creating a virtual environment or installing system packages.

1. **Python virtual environment** — ask the user if they want a project-local venv (`.venv`) or a shared one elsewhere. Then create and activate it:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```

2. **Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **WeasyPrint system dependencies** — these are required for PDF generation and need root privileges. Ask the user to run the appropriate command in their terminal:
   ```bash
   # Ubuntu/Debian
   sudo apt install libpango1.0-dev libharfbuzz-dev libffi-dev

   # macOS (Homebrew)
   brew install pango libffi

   # Other platforms: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
   ```

4. **Fonts:**
   ```bash
   python scripts/fetch_fonts.py
   ```

## Quick Start

Drop your existing resume PDFs/docs into `docs/resume_source_material/`, then tell your AI assistant:

```
"Import my resumes from docs/resume_source_material/"
```

The AI reads `IMPORT_EXISTING.md` and aggregates everything into `data/resume.yaml`. The more resumes you feed it, the more complete your master file.

Once imported:

```
"Tailor my resume for this Software Engineer role at Acme Corp: <paste JD>"
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
docs/resume_source_material/      # Your existing resumes go here (gitignored)
docs/job_descriptions/            # Job descriptions for tailoring (gitignored)
```

## AI Workflows

This tool is designed to be used with an AI CLI tool. The workflow files are structured prompts that the AI reads and follows:

| Workflow               | Trigger                        | What it does                                              |
| ---------------------- | ------------------------------ | --------------------------------------------------------- |
| `IMPORT_EXISTING.md`   | "Import my resumes"            | Aggregates multiple existing resumes into the master YAML |
| `INSTRUCTIONS.md`      | "Tailor my resume for..."      | Selects bullets for a job description, generates PDF      |
| `ADDING_EXPERIENCE.md` | "Add my new job at..."         | Interactive interview to add a new role to the master     |
| `ANALYZING.md`         | "Analyze my resume against..." | Evaluates a tailored resume's coverage of a JD            |

The AI tool picks up project context automatically via `CLAUDE.md`, `GEMINI.md`, or `.cursorrules`.

## Templates

Templates live in `templates/<name>/` with `resume.html`, `style.css`, and `meta.yaml`. The first time you generate a PDF, you're prompted to pick a template. Add `--reconfigure` to change later.

## Commands

```bash
python scripts/generate.py --data <yaml> [--keep-html] [--reconfigure]  # Generate PDF
python scripts/render.py --data <yaml> --output <path>                    # Render HTML only
python scripts/pdf.py --input <html> --output <path>                     # HTML → PDF
python scripts/fetch_fonts.py                                            # Download fonts
```

With [just](https://github.com/casey/just):

```bash
just regen              # Regenerate the most recently modified tailored.yaml
just generate <path>    # Generate a specific tailored resume
just fonts              # Fetch/update fonts
```

## Requirements

- An AI CLI tool (Claude Code, Gemini CLI, Cursor, or similar)
- Python 3.10+

## License

AGPL-3.0 — see [LICENSE](LICENSE).
