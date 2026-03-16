# Resume Tailoring Instructions

Instructions for Claude Code (or any AI assistant) to tailor a resume for a specific job.

---

## 1. Overview

You are given a master resume (`data/resume.yaml`) containing every piece of professional history, and a job description. Your task is to produce a tailored subset of that data, then render it to PDF.

You select — never invent or modify.

---

## 2. Input Files

- **Master data**: `data/resume.yaml` — read this first, every time
- **Job description**: path provided by the user (or pasted inline)
- **Output directory**: `jobs/<company>/<role>/` — create if it doesn't exist

---

## 3. Analysis Step

Before selecting anything, extract from the job description:

1. **Required skills / technologies** — what must appear on the resume
2. **Preferred skills** — nice to have, include if present in master
3. **Key themes** — e.g. "distributed systems", "people management", "data pipelines"
4. **Seniority signals** — IC vs. management, years of experience expected
5. **Section emphasis** — does the JD weight projects heavily? Publications? Open source?

Write a brief internal analysis (you don't need to show it to the user unless asked).

---

## 4. Selection Rules

### Basics
Always include the full `basics` section unchanged.

### Work experience
- Include all jobs from the master (omitting old jobs entirely looks suspicious)
- For each job, select **3–5 bullets** from `bullets[]` based on:
  1. Relevance to the job's key themes and required skills (primary criterion)
  2. `priority` field — lower number = higher default importance (tiebreaker)
- For roles more than 10 years old, select **1–2 bullets maximum**
- Record selected bullets by their `id` field in `highlight_ids` (ordered list) — do not copy text

### Skills
- Include skill categories that are relevant or adjacent to the role
- Always include core languages (the first `skills` entry)
- Reorder categories so the most relevant appear first
- Within a category, you may drop individual `keywords` that are irrelevant, but keep at least 3 per included category

### Projects
- Include only if directly relevant to the role or if the JD emphasizes open source / side projects
- Select 1–2 bullets per project if included

### Education
- Always include

### Publications
- Include only if the role is research-adjacent, or the publication topic is directly relevant

### Certificates
- Include if they match a required or preferred qualification in the JD

### Awards
- Include only if directly relevant

### Volunteer
- Include if the role emphasizes leadership, community, or teaching

### Section ordering
Default order: Experience → Skills → Projects → Education → Publications → Certifications → Awards → Volunteer

Reorder if the JD clearly emphasizes something else:
- Research role → move Publications up (after Experience)
- New grad role → move Education up (after Experience)
- Engineering manager role → move Volunteer/Leadership signals earlier

---

## 5. Page Fitting

Target: **up to 2 pages** (US Letter).

After first draft:
- **Over 2 pages**: remove bullets from oldest or least relevant roles first, then trim less-relevant sections entirely
- **Under 2 pages**: acceptable — do not pad content just to fill space

Page length cannot be estimated from bullet count alone — it depends on the template and bullet text length. Always render and check the page count printed by `generate.py`.

---

## 6. Output Step

### 6a. Create tailored YAML

Write `jobs/<company>/<role>/tailored.yaml` with this structure:

```yaml
# Tailored for: <Company> — <Role>
source: data/resume.yaml

basics:
  # copy verbatim from master

work:
  - name: Acme Corp
    highlight_ids: [a1b2c3d4, e5f6a7b8]
  - name: Some Corp
    highlight_ids: [c9d0e1f2]
  # If a company appears more than once in master (e.g. promotion), position: is REQUIRED on
  # every entry for that company to disambiguate — omitting it will cause a generation error:
  - name: Nimbus Labs
    position: Software Engineer
    highlight_ids: [91a2d4f7, f6c83b21]

skills:
  # selected and reordered categories

education:
  # copy verbatim

# include other sections only if selected above
# for publications, list by name only — metadata resolved from master:
# publications:
#   - name: "Publication Title"
```

**Key points:**
- `source` field triggers reference resolution at generation time
- `work` entries only need `name` + `highlight_ids`; position/dates/summary are inherited from master
- `highlight_ids` is an ordered list of 8-char hex bullet IDs from `data/resume.yaml`
- Order of `work` entries = order on the rendered resume; order of `highlight_ids` = order of bullets
- Skills, basics, and education are still copied verbatim

### 6b. Generate PDF

```bash
python scripts/generate.py --data jobs/<company>/<role>/tailored.yaml --keep-html
# First run: prompts for template selection and output path, saves to .generate.yaml
# Subsequent runs: uses saved settings automatically
# To change template: add --reconfigure flag
```

### 6c. Verify

After generation:
- Confirm the PDF exists and is non-zero bytes
- Check page count: `generate.py` prints the page count; if `pdfinfo` is available, use `pdfinfo jobs/<company>/<role>/resume.pdf` to confirm 1 or 2 pages
- Offer to analyze coverage: **"Want me to check how well this covers the job description? I can identify gaps and suggest improvements."** If yes, follow `ANALYZING.md`.

---

## 7. Hard Rules — NEVER VIOLATE

1. **Never modify wording** — select bullets by ID; the master text is rendered verbatim
2. **Never invent content** — if a skill, achievement, or project isn't in the master YAML, it cannot appear in the tailored resume
3. **Never remove basics** — name, email, phone, profiles are always included
4. **Never use `highlights` with copied text** in tailored YAML — use `highlight_ids` referencing master bullet IDs
5. **Never skip the analysis step** — reading the JD carefully before selecting is mandatory
6. **Never modify `data/resume.yaml`** — it is the single source of truth; only create new files in `jobs/`

---

## 8. Example Workflow

```
User: "Tailor my resume for this SRE role at Google: <JD>"

You:
1. Read data/resume.yaml
2. Analyze JD: key themes = reliability, SLOs, on-call, Kubernetes, Go/Python
3. Select bullets by ID emphasizing SRE, distributed systems, reliability work
4. Write jobs/google/sre/tailored.yaml (source + highlight_ids, no copied text)
5. Run: python scripts/generate.py --data jobs/google/sre/tailored.yaml --keep-html
6. Confirm: pdfinfo jobs/google/sre/resume.pdf → 1 or 2 pages
```
