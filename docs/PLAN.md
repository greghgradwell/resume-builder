# Resume Builder — Implementation Plan

## Phase 1: Foundation (Core MVP)

The minimum needed to generate a tailored PDF resume from YAML data.

### 1.1 Project Setup
- [ ] Initialize Python project with `requirements.txt`
- [ ] Set up directory structure (`data/`, `templates/`, `fonts/`, `scripts/`, `jobs/`)
- [ ] Create `.gitignore` (exclude `__pycache__`, `.venv`, `node_modules`)
- [ ] Add `CLAUDE.md` with project conventions and instructions for Claude Code

### 1.2 Font Management
- [ ] Write font download script (`scripts/fetch_fonts.py`)
  - Fetches `.woff2` files from Google Fonts API for the curated font set
  - Stores in `fonts/<family>/` directories
  - Generates `fonts/fonts.css` with `@font-face` declarations
- [ ] Download initial font set: Inter, Lato, Montserrat, Source Sans 3,
      Raleway, Merriweather, Source Serif 4

### 1.3 Master Resume Data
- [ ] Create `data/resume.yaml` with the full schema
  - Placeholder/example data for all sections
  - Comments documenting each field
  - Tag and priority fields on work highlights
- [ ] Write YAML schema documentation (inline comments in the YAML itself)

### 1.4 HTML Template
- [ ] Create `templates/base.html` (document structure, font loading, CSS)
- [ ] Create `templates/resume.html` (resume layout sections)
- [ ] Create `templates/styles/base.css` (reset, typography, print rules)
- [ ] Create `templates/styles/modern.css` (clean modern theme)
- [ ] Implement CSS custom properties for all adjustable values
- [ ] Implement `@page` rules for US Letter, two-page max

### 1.5 Rendering Pipeline
- [ ] Write `scripts/render.py`
  - Loads YAML data (master or tailored)
  - Renders Jinja2 template to HTML string
  - Writes HTML file to specified output path
  - CLI: `python scripts/render.py --data data/resume.yaml --output output.html`
- [ ] Write `scripts/pdf.py`
  - Takes HTML file path as input
  - Uses WeasyPrint to generate PDF with embedded fonts
  - CLI: `python scripts/pdf.py --input output.html --output resume.pdf`

### 1.6 AI Tailoring Instructions
- [ ] Write `INSTRUCTIONS.md`
  - Step-by-step guide for Claude Code to tailor a resume
  - Rules for bullet selection (relevance, quantity per role)
  - Rules for skill selection
  - Formatting constraints (two-page max, section ordering)
  - Examples of good vs. bad selections
  - Hard rule: never modify wording

**Go/No-Go**: Can generate a complete two-page PDF from YAML data with proper
fonts. Claude Code can follow INSTRUCTIONS.md to produce a tailored resume.

---

## Phase 2: Preview & Iteration

Interactive tools for rapid visual iteration.

### 2.1 Preview Server
- [ ] Write `scripts/preview.py` (Flask app)
  - Serves rendered HTML at `http://localhost:5000`
  - Auto-reloads when YAML, template, or CSS files change
  - Watchdog-based file monitoring
- [ ] Add control panel (separate route or overlay)
  - Font family dropdown
  - Font size sliders (name, heading, body)
  - Margin adjustment
  - Line height / spacing controls
  - All changes applied via CSS custom property updates
  - "Generate PDF" button

### 2.2 Developer Experience
- [ ] Add `Makefile` or shell script for common operations:
  - `make preview` — start the preview server
  - `make pdf` — render and generate PDF for current data
  - `make fonts` — download/update fonts
  - `make setup` — install all dependencies
- [ ] Write `README.md` with setup and usage instructions

**Go/No-Go**: Can preview resume in browser, adjust styling in real time,
and generate PDF with one click.

---

## Phase 3: Polish & Extras (Full Vision)

Nice-to-have improvements after core is solid.

### 3.1 Additional Templates
- [ ] Two-column layout option
- [ ] Classic/traditional theme
- [ ] Template switching in preview server

### 3.2 Enhanced AI Features
- [ ] Tag-based bullet categorization in YAML
- [ ] Priority-aware selection (prefer high-priority bullets)
- [ ] Professional summary generation guidance (AI drafts, user approves)
- [ ] Skills gap analysis (what the job wants vs. what's in master data)

### 3.3 Quality of Life
- [ ] JSON Resume import/export (`scripts/convert.py`)
- [ ] YAML validation script (checks required fields, formatting)
- [ ] Batch generation (multiple roles from a single command)
- [ ] PDF comparison tool (diff two generated resumes)
- [ ] Font preview page in the preview server

---

## Suggested First Step

After this specification is approved:

```
/cadre:plan Implement Phase 1: Foundation
```

This will create a detailed, file-level implementation plan for the core MVP.
