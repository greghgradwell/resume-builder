# Importing Existing Resumes

Instructions for an AI assistant to aggregate one or more existing resumes into `data/comprehensive_bio.yaml`.

---

## 1. Overview

The user has existing resumes — likely several, each tailored for a different job over the course of their career. No single document has everything. Your task is to read all of them and produce a single, comprehensive master file that captures every unique bullet, skill, and credential across all sources.

You extract and structure — never embellish or invent. The user's original wording is the raw material.

**The boundary:** the user's *content* is sacred — their claims, their phrasing, their voice. But *organization* is yours. Categorize skills, group bullets by theme, choose tag taxonomies, assign priorities, reorder sections — use your judgment freely. The input comes from the user; the structure comes from you.

---

## 2. Input

The user provides one or more of:
- PDF or docx files (e.g. `hand_crafted_resumes/*.pdf`)
- Text pasted inline
- A LinkedIn export or similar structured data

Read **all** provided files before starting conversion. If the directory is empty or no files are provided, ask the user to supply their resumes before proceeding.

Different resumes will contain different subsets of the user's experience — the goal is the union of all of them.

---

## 3. Read the Example

Before writing anything, read `data/comprehensive_bio.yaml` — this ships with example data demonstrating the expected structure, field names, and formatting conventions. Your output will replace it and must match this structure precisely.

---

## 4. Aggregation Rules

### Deduplication

The same job will appear on multiple resumes, often with different bullets selected. For each job:
- Merge bullets across all sources — keep every unique accomplishment
- If two resumes describe the same accomplishment with different wording, keep the more specific version (the one with technology names, numbers, or outcomes)
- Do not create duplicate bullets for the same work

### Basics

Extract and map to:

```yaml
basics:
  name: Full Name
  label: Professional Title
  email: email@example.com
  phone: "555.123.4567"
  location:
    city: City
    region: State/Province
    countryCode: US
  profiles:
    - network: GitHub
      username: handle
      url: https://github.com/handle
```

- Use the most recent resume as the authority for contact info and title
- If a field isn't present in any source, omit it entirely
- `profiles` is a list — include GitHub, LinkedIn, or any other professional profiles found

### Work Experience

For each position, create a work entry with bullets:

```yaml
work:
  - name: Company Name
    position: Job Title
    startDate: "YYYY-MM"
    endDate: "YYYY-MM"        # omit entirely for current role
    summary: One-sentence description of the company or role focus.
    bullets:
      - id: a1b2c3d4
        text: "Verb-led bullet preserving the user's original wording"
        tags: [tag1, tag2]
        priority: 1
```

- Order: most recent first
- Generate a unique 8-char hex ID for every bullet (run once per bullet — each must be unique): `python -c "import uuid; print(uuid.uuid4().hex[:8])"`
- Dates: use `YYYY-MM` format. Omit `endDate` entirely for current roles (empty string fails validation)

### Bullet Style

The user's original wording is the raw material. You may make **minimal adjustments** for consistency:
- Restructure to be **verb-led** if needed (e.g. "Was responsible for developing..." → "Developed...")
- Remove filler words ("responsible for", "leveraged", "spearheaded")
- Normalize tense to past tense

You may **not**:
- Rewrite bullets in different words than the user used
- Add outcomes, metrics, or claims not present in the source
- Embellish or upgrade language
- Merge two distinct accomplishments into one bullet

When in doubt, keep the user's original phrasing. Flag any bullet you had to significantly rephrase during the review step so the user can verify it still sounds like them.

### Tags

Assign lowercase, hyphen-separated tags to each bullet. Draw from common categories:
- Domain: `software`, `hardware`, `web`, `data`, `embedded`, `cloud`, `devops`
- Technology: `python`, `go`, `javascript`, `react`, `kubernetes`, `postgresql`, etc.
- Functional: `api`, `testing`, `ci-cd`, `security`, `performance`, `tooling`, `leadership`

Use 2–5 tags per bullet. Be specific enough to be useful for filtering.

### Priority

Assign based on significance:
- `1` — core accomplishment, most likely to appear on any tailored resume
- `2` — solid supporting bullet, appears on most tailored resumes
- `3` — contextual detail, appears when the role is especially relevant
- `4` — edge case, included only for highly specific matches

When uncertain, default to `2`. The user can adjust later.

### Skills

Group into categories:

```yaml
skills:
  - name: Category Name
    level: Advanced    # Advanced, Intermediate, or Beginner
    keywords: [Skill1, Skill2, Skill3]
```

- Extract all skills mentioned across all resumes
- Group logically (Languages, Cloud, Web, Data, Practices, etc.)
- Match the category style in the example data

### Education

```yaml
education:
  - institution: University Name
    area: Field of Study
    studyType: B.S.    # B.S., M.S., Ph.D., etc.
    endDate: "YYYY-06"
```

### Publications

Only if present in any source:

```yaml
publications:
  - name: "Paper Title"
    publisher: "Conference or Journal"
    releaseDate: "YYYY-MM-DD"    # must be full date
    url: https://doi.org/...
    summary: One-sentence description.
```

Note: `releaseDate` requires `YYYY-MM-DD` format (not just `YYYY-MM`).

---

## 5. Review with User

After drafting the full YAML, present a summary to the user:

1. **Job count**: "I found N positions across your resumes."
2. **Bullet count**: "I extracted N unique bullets total (N merged duplicates)."
3. **Gaps**: "These roles appeared on only one resume — did I capture everything for them?"
4. **Wording check**: "I've rephrased some bullets for style consistency. Review any that seem off — your wording is what matters."
5. **Missing experience**: "Is there anything from your career that didn't appear on any of these resumes?"

Revise until the user approves.

---

## 6. Write and Validate

Once approved:

1. Write to `data/comprehensive_bio.yaml`
2. Validate:

```bash
python -c "import yaml; yaml.safe_load(open('data/comprehensive_bio.yaml'))"
```

No output = valid. Fix any errors before finishing.

3. Clean up example files — the import replaces `data/comprehensive_bio.yaml`, and the example input files are no longer needed:
   - Delete PDFs in `hand_crafted_resumes/` with `(example)` in the name
   - Delete `data/jobs/example/` directory

---

## 7. Hard Rules

1. **Never invent content** — only include what the source resumes actually say
2. **Never rewrite** — minimal style adjustments only; the user's words are the product
3. **Never exaggerate** — preserve the original scope and claims exactly
4. **Never skip validation** — always run the YAML check after writing
5. **Generate unique IDs** — every bullet must have a fresh 8-char hex ID
6. **Omit missing fields** — don't add placeholder data for fields not in any source
7. **Keep every unique bullet** — the master file should be comprehensive; tailoring happens later
8. **Flag significant rephrasing** — if you had to restructure a bullet beyond verb-leading, call it out during review
