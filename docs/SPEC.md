# Resume Builder — Product Specification

## Problem Statement

A senior engineer with 15+ years of experience needs to maintain a comprehensive
record of all professional accomplishments and tailor two-page resumes for specific
job applications. The current single-page format is insufficient to represent the
breadth of experience. Manual resume tailoring for each application is
time-consuming and error-prone.

## Users

**Primary user**: The resume owner — a senior software engineer who:
- Has extensive work history across multiple organizations
- Applies to roles requiring tailored emphasis on different skills/experiences
- Wants full control over wording (AI must never rewrite content)
- Is comfortable using CLI tools and editing YAML files
- Uses Linux as their primary development environment

**Secondary user**: Any AI assistant (Claude Code or similar) that:
- Reads a structured instruction set to perform resume tailoring
- Selects relevant bullets from a master list based on a job description
- Generates formatted output without altering the user's original wording

## Core Requirements

### R1: Master Resume Data (YAML)
- Single YAML file containing ALL professional data
- Sections: basics, work experience, skills, education, publications,
  certifications, projects, awards, volunteer work
- Each work experience entry contains ALL bullet points (the complete list)
- Skills organized by category with keyword lists
- Must be the single source of truth — all generated resumes derive from this

### R2: AI Tailoring via Claude Code
- A detailed `INSTRUCTIONS.md` file that any AI can follow
- Instructions specify:
  - How to read and parse the master YAML
  - How to analyze a job description for relevant keywords/themes
  - How to select which bullet points to include (relevance scoring)
  - How to select which skills to highlight
  - How to order sections for maximum impact
  - Formatting rules (two pages max, font sizes, margins)
- **Hard constraint**: AI must NEVER modify the wording of any bullet point,
  skill, publication, or other content. Selection only.
- AI generates the tailored HTML file and triggers PDF generation

### R3: PDF Output
- Final deliverable is a PDF file
- US Letter size (8.5" x 11")
- Exactly two pages (preferred) — never more than two
- Professional fonts (Google Fonts: Inter, Lato, Montserrat, etc.)
- ATS-friendly (parseable text, no images for text content)
- Clean modern style: single-column, sans-serif, subtle section dividers

### R4: Directory Structure for Job Applications
- Each job application gets a directory: `jobs/<company>/<role>/`
- Contains: job description file, generated HTML, generated PDF
- Provides an organized history of all tailored resumes

### R5: Local Preview Server
- Localhost web server to preview the HTML resume in a browser
- Hot-reload on file changes for rapid iteration
- Controls for adjusting font family, font size, spacing, margins
- Changes reflected immediately without regenerating from scratch

### R6: Font Management
- Self-hosted Google Fonts (not dependent on CDN at PDF generation time)
- Curated set of professional resume fonts downloaded locally
- Easy to add new fonts
- Fonts embedded in PDF output

## Non-Requirements (Explicitly Out of Scope for MVP)

- No web-hosted deployment (localhost only)
- No user authentication or multi-user support
- No database — all data in flat files (YAML, HTML, CSS)
- No automatic job description fetching/scraping
- No cover letter generation
- No ATS score checking
- No version control UI (git handles this)

## Success Criteria

1. Can generate a tailored two-page PDF resume in under 2 minutes
2. Generated PDF is ATS-parseable (text selectable, no image-based content)
3. Master YAML file is the single source of truth for all content
4. AI tailoring follows instructions without rewriting any user content
5. Font rendering in PDF matches the browser preview
6. Directory structure keeps all job applications organized and browsable

## File Organization

```
resume-builder/
├── docs/                       # Project documentation
│   ├── SPEC.md                 # This file
│   ├── DESIGN.md               # Technical architecture
│   └── PLAN.md                 # Implementation roadmap
├── data/
│   └── resume.yaml             # Master resume data (single source of truth)
├── templates/
│   ├── resume.html             # Jinja2 HTML template
│   └── styles/
│       ├── modern.css          # Clean modern theme
│       └── base.css            # Shared base styles
├── fonts/                      # Self-hosted Google Fonts (.woff2)
│   ├── inter/
│   ├── lato/
│   └── montserrat/
├── scripts/
│   ├── preview.py              # Local preview server (Flask/FastAPI)
│   ├── render.py               # HTML rendering from YAML + template
│   └── pdf.py                  # PDF generation (WeasyPrint)
├── jobs/                       # Job applications (one dir per application)
│   ├── google/
│   │   └── sre/
│   │       ├── description.txt # Job description (saved by user)
│   │       ├── resume.html     # Tailored HTML output
│   │       └── resume.pdf      # Final PDF output
│   └── meta/
│       └── backend/
│           ├── description.txt
│           ├── resume.html
│           └── resume.pdf
├── INSTRUCTIONS.md             # AI tailoring instructions
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies (if using JSON Resume themes)
└── README.md                   # Setup and usage guide
```
