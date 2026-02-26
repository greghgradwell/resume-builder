# Resume Builder — Technical Design

## Architecture Overview

The system has three layers:

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                     │
│  Claude Code (AI tailoring)  │  Preview Server (web) │
└──────────────┬───────────────┴──────────┬────────────┘
               │                          │
┌──────────────▼──────────────────────────▼────────────┐
│                  Rendering Engine                      │
│  YAML parser → Jinja2 templates → HTML generation     │
└──────────────────────────┬───────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────┐
│                   PDF Generation                      │
│  WeasyPrint (HTML + CSS + Fonts → PDF)                │
└──────────────────────────────────────────────────────┘
```

## Technology Choices

### Content Layer: YAML + JSON Resume Schema

**Choice**: YAML file following the JSON Resume schema structure.

**Rationale**:
- YAML is easier to read and edit than JSON, supports comments
- JSON Resume schema is a well-established standard with clear field definitions
- We follow the schema structure but store as YAML (trivial to convert)
- PyYAML (Python) handles parsing

**Schema extensions beyond JSON Resume**:
- `highlights` in each work entry serves as the master bullet list
- Each highlight can optionally have `tags` for categorization (e.g., "leadership",
  "architecture", "performance") to aid AI in selection
- A `priority` field (1-5) on highlights to indicate the user's preference for
  inclusion when space is tight

### Templating Layer: Jinja2 (Python)

**Choice**: Jinja2 HTML templates rendered in Python.

**Rationale**:
- Jinja2 is the standard Python templating engine
- Full control over HTML output
- Template inheritance for multiple themes
- Filters and macros for formatting dates, lists, etc.
- No Node.js dependency for the core rendering pipeline

**Template approach**:
- `base.html` — document structure, CSS links, font loading
- `resume.html` — extends base, defines resume sections
- CSS files control visual styling independently from template structure
- Template receives a "tailored" data dict (subset of master YAML selected by AI)

### PDF Generation: WeasyPrint

**Choice**: WeasyPrint (Python library, no browser dependency).

**Rationale**:
- Actively maintained (v68+, Feb 2026)
- Excellent CSS support: Flexbox, `@page`, `@font-face`, `break-before/after`
- Embeds and subsets fonts automatically in PDF
- No Chromium/browser dependency (lighter than Puppeteer/Playwright)
- Native Python API — trivial to integrate with the rendering pipeline
- Excellent multi-page pagination (core design goal of the library)

**If WeasyPrint rendering is insufficient**: Fall back to Playwright (Python bindings)
for pixel-perfect browser rendering. This is a contingency, not the default.

### Preview Server: Flask

**Choice**: Flask with live reload.

**Rationale**:
- Lightweight, minimal dependencies
- Serves the rendered HTML directly
- Watchdog-based file watcher triggers re-render on YAML/template/CSS changes
- Simple enough to not need a frontend build step
- API endpoints for font/style adjustments from a control panel

**Preview features**:
- Renders the current resume HTML at `http://localhost:5000`
- Control panel sidebar (or separate route) for:
  - Font family selection (dropdown of available fonts)
  - Font size adjustment (body text, headings)
  - Margin adjustment
  - Line spacing
  - Live CSS variable updates via simple JS
- "Generate PDF" button that triggers WeasyPrint and opens/downloads result

### Font Strategy

**Approach**: Self-hosted Google Fonts with a download script.

**Initial font set** (curated for professional resumes):

| Font | Style | Use Case |
|------|-------|----------|
| Inter | Sans-serif | Body text (default) |
| Lato | Sans-serif | Body text (alternative) |
| Source Sans 3 | Sans-serif | Body text (alternative) |
| Montserrat | Sans-serif | Headings |
| Raleway | Sans-serif | Headings (alternative) |
| Merriweather | Serif | Traditional/executive feel |
| Source Serif 4 | Serif | Pairs with Source Sans |

**Download method**:
- Script fetches `.woff2` files from Google Fonts API
- Stores in `fonts/<family>/` directory
- Generates `@font-face` CSS declarations automatically
- Fonts referenced via local paths in CSS (no CDN dependency at render time)

### AI Tailoring Architecture

The AI (Claude Code) operates through a structured instruction file.

**Flow**:
```
1. User saves job description to jobs/<company>/<role>/description.txt
2. User asks Claude Code: "Tailor my resume for jobs/google/sre/description.txt"
3. Claude Code reads INSTRUCTIONS.md
4. Claude Code reads data/resume.yaml (full master data)
5. Claude Code reads the job description
6. Claude Code analyzes the job description for:
   - Required skills and technologies
   - Experience level expectations
   - Domain/industry focus
   - Key responsibilities and themes
7. Claude Code selects from master data:
   - Which work experience bullets to include (based on relevance)
   - Which skills to list (matching job requirements)
   - Which publications/projects to feature
   - Section ordering for maximum impact
8. Claude Code generates a "tailored" YAML (subset of master)
   stored as jobs/<company>/<role>/tailored.yaml
9. Claude Code renders HTML via the render script
10. Claude Code generates PDF via the pdf script
```

**Key design principle**: The tailored YAML is an intermediate artifact. It contains
only selected data from the master, with NO modifications to wording. This makes it
auditable — the user can diff `tailored.yaml` against `data/resume.yaml` to verify
nothing was changed.

### Directory Convention

```
jobs/
└── <company-slug>/          # lowercase, hyphenated (e.g., "google", "meta")
    └── <role-slug>/         # lowercase, hyphenated (e.g., "sre", "staff-backend")
        ├── description.txt  # Original job description (saved by user)
        ├── tailored.yaml    # AI-selected subset of master data
        ├── resume.html      # Rendered HTML
        └── resume.pdf       # Final PDF output
```

## CSS Architecture

### Design Tokens (CSS Custom Properties)

```css
:root {
  /* Typography */
  --font-heading: 'Montserrat', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-size-name: 22px;
  --font-size-heading: 11px;
  --font-size-body: 10.5px;
  --font-size-small: 9px;

  /* Spacing */
  --margin-page: 0.5in;
  --spacing-section: 12px;
  --spacing-item: 6px;
  --line-height: 1.35;

  /* Colors */
  --color-text: #1a1a1a;
  --color-heading: #333333;
  --color-accent: #555555;
  --color-divider: #cccccc;
}
```

These tokens are adjustable from the preview server's control panel via JavaScript
that updates CSS custom properties in real time.

### Print Styles

```css
@page {
  size: letter;
  margin: var(--margin-page);
}

@media print {
  /* Ensure exactly two pages */
  /* Page break controls */
  /* Hide preview UI elements */
}
```

## Dependencies

### Python (primary)
- `pyyaml` — YAML parsing
- `jinja2` — HTML templating
- `weasyprint` — PDF generation
- `flask` — Preview server
- `watchdog` — File watching for live reload

### Node.js (optional, for JSON Resume ecosystem)
- `resumed` — JSON Resume renderer (if using existing themes)
- `jsonresume-theme-*` — Pre-built themes (reference/fallback)

### System
- Python 3.10+
- Node.js 18+ (optional)
- Linux (primary target)
