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
- Copy selected bullet `text` values verbatim into `highlights` in the tailored YAML

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

Target: **exactly 2 pages** (US Letter).

After first draft:
- **Over 2 pages**: remove bullets from oldest or least relevant roles first, then trim less-relevant sections entirely
- **Under 1.5 pages**: add more bullets from the most relevant roles (still within the `bullets[]` pool), or add an omitted section if it has relevant content
- **Between 1.5–2 pages**: acceptable, leave as-is

You cannot know page length without rendering — use judgment based on bullet count:
- A typical 2-page resume fits ~18–24 bullets across all jobs
- Each section header + entry header takes approximately 2 lines

---

## 6. Output Step

### 6a. Create tailored YAML

Write `jobs/<company>/<role>/tailored.yaml` with this structure:

```yaml
# Tailored for: <Company> — <Role>
# Source: data/resume.yaml

basics:
  # copy verbatim from master

work:
  - name: Acme Corp
    position: Senior Software Engineer
    startDate: "2021-03"
    summary: ...
    highlights:
      - "Exact bullet text copied from master bullets[].text"
      - "Another bullet"
  # ... other jobs

skills:
  # selected and reordered categories

education:
  # copy verbatim

# include other sections only if selected above
```

**Schema note**: `tailored.yaml` uses standard JSON Resume `highlights: string[]` (plain strings). The `bullets` / `tags` / `priority` extension fields from the master are not needed here.

### 6b. Generate PDF

```bash
python scripts/generate.py \
  --data jobs/<company>/<role>/tailored.yaml \
  --output jobs/<company>/<role>/resume.pdf \
  --keep-html
```

### 6c. Verify

After generation:
- Confirm the PDF exists and is non-zero bytes
- Check `pdfinfo jobs/<company>/<role>/resume.pdf` shows 2 pages

---

## 7. Hard Rules — NEVER VIOLATE

1. **Never modify wording** — bullet text must be copied character-for-character from `bullets[].text` in the master
2. **Never invent content** — if a skill, achievement, or project isn't in the master YAML, it cannot appear in the tailored resume
3. **Never remove basics** — name, email, phone, profiles are always included
4. **Never use the `bullets` field** in tailored YAML — use `highlights` with plain strings
5. **Never skip the analysis step** — reading the JD carefully before selecting is mandatory
6. **Never modify `data/resume.yaml`** — it is the single source of truth; only create new files in `jobs/`

---

## 8. Example Workflow

```
User: "Tailor my resume for this SRE role at Google: <JD>"

You:
1. Read data/resume.yaml
2. Analyze JD: key themes = reliability, SLOs, on-call, Kubernetes, Go/Python
3. Select bullets emphasizing SRE, distributed systems, reliability work
4. Write jobs/google/sre/tailored.yaml
5. Run: python scripts/generate.py --data jobs/google/sre/tailored.yaml --output jobs/google/sre/resume.pdf --keep-html
6. Confirm: pdfinfo jobs/google/sre/resume.pdf → 2 pages
```
