# Analyzing a Tailored Resume

Instructions for Claude Code to evaluate a completed tailored resume against a job description, surface missed opportunities, and flag gaps.

---

## 1. Overview

You are given a tailored resume (`tailored.yaml`), a job description, and access to the master resume (`data/comprehensive_bio.yaml`). Your task is to evaluate how well the tailored resume covers the JD, identify bullets from the master that should have been included, and flag requirements that no existing bullet addresses.

You analyze — never modify, never invent.

---

## 2. Inputs

- **Tailored resume**: `data/jobs/<company>/<role>/tailored.yaml` — the resume to evaluate
- **Job description**: PDF or text from `data/jobs/<company>/<role>/`, or pasted inline by the user
- **Master resume**: `data/comprehensive_bio.yaml` — read this in full to access the complete bullet pool

Read all three before producing any output.

---

## 3. Extract JD Requirements

Parse the job description into these categories:

1. **Required skills / technologies** — explicit must-haves ("C++", "ROS", "AUTOSAR")
2. **Preferred skills** — nice-to-haves, often prefixed with "preferred" or "plus"
3. **Key responsibilities / themes** — recurring themes that signal what the role actually does day-to-day ("write safety-critical code", "collaborate cross-functionally", "own the full stack")
4. **Seniority signals** — years of experience, IC vs. lead, owns vs. contributes
5. **Domain knowledge expectations** — industry-specific background (ADAS, aerospace, finance, etc.)

Write a brief internal summary of these before proceeding to coverage analysis.

---

## 4. Coverage Analysis

For each extracted requirement, determine coverage in the tailored resume:

- **Strong** — one or more bullets directly address this requirement with specific evidence
- **Partial** — the tailored resume touches the theme but doesn't name the technology or doesn't give evidence
- **Weak** — the requirement is implied by a job title or section header but not demonstrated in a bullet
- **Missing** — nothing in the tailored resume addresses this requirement

For each "Missing" or "Partial" result, also check the master resume's `bullets[]` across all roles:

- If a matching bullet exists in the master but wasn't included in the tailored resume, mark it **"available but unused"**
- If no matching bullet exists anywhere in the master, mark it **"gap"**

Use tags and bullet text to determine relevance — a bullet tagged `[cpp, embedded]` is relevant to a C++ embedded systems requirement even if the text doesn't use the exact phrase.

---

## 5. Unused Bullet Suggestions

From the master resume, identify bullets that:

1. Match a JD requirement (by tag, technology name, or theme)
2. Were **not** included in the tailored resume's `highlight_ids`

For each such bullet, recommend:
- Which role it comes from
- Which JD requirement it addresses
- Whether it should **replace** a current highlight (and which one) or **expand** the highlights list (noting the page-length tradeoff)
- The bullet's `id` from the master, so it can be added directly to `highlight_ids`

Limit suggestions to bullets that would meaningfully improve coverage — do not suggest minor additions for requirements already marked Strong.

---

## 6. Gap Analysis

For requirements marked "gap" (no matching bullet exists anywhere in the master):

- Review the work history and roles in `data/comprehensive_bio.yaml`
- Identify companies or roles where this experience **might** plausibly exist but was never written as a bullet
- For each candidate, ask a specific, targeted question:

> "You worked at [Company] as [Role] — did you [specific activity related to the requirement]?"

Do not invent bullets. Do not assume the experience exists. Only ask — the user confirms or denies.

If no plausible candidate exists in the work history, note the requirement as a **true gap** (no relevant experience to draw from).

### After the report

If the user confirms they have experience for any gap, offer to add it immediately: **"Want to add that as a bullet? I'll walk you through it."** Then follow `ADDING_EXPERIENCE.md` Phase 2 (Shape Bullets) for that specific bullet — the interview questions aren't needed since the user just described the experience. Once the new bullet is in the master, offer to update the tailored resume to include it.

---

## 7. Report Format

Produce a structured report in this format:

```
## Resume Analysis: [Company] — [Role]

### Match Score: X/10

[One sentence rationale for the score.]

### Coverage Table
| JD Requirement | Status | Evidence (role + bullet) |
|---|---|---|
| Go development | Strong | Nimbus Labs: "Led migration of monolithic API..." |
| ADAS experience | Missing | — |
| Cross-functional collaboration | Partial | Implied by PM role titles, no explicit bullet |

### Suggested Changes
1. **Add from master**: "[bullet text]" (`id: a1b2c3d4`, from [Role] at [Company]) — matches [requirement]
2. **Swap out**: `id: a1b2c3d4` is less relevant than `id: e5f6a7b8` ("[suggested bullet text]") for this role
3. **Reorder**: Move [Role] highlights to lead with [topic] — closer JD match

### Gaps to Explore
1. **[Requirement]**: You worked at [Company] as [Role] — did you [specific question]?
   → If yes, add via ADDING_EXPERIENCE.md
2. **[Requirement]**: No relevant experience found in your history — true gap.
```

Present the full report at once, then wait. Do not start making changes until the user explicitly asks.

---

## 8. Hard Rules — NEVER VIOLATE

1. **Never invent bullets or skills** — only suggest content that exists verbatim in `data/comprehensive_bio.yaml`
2. **Never modify files during analysis** — present the full report first, then wait for the user to decide what to change
3. **Never skip reading the master** — partial analysis based only on the tailored resume is not acceptable
4. **Never assume experience** — gap questions are questions, not assertions; the user confirms what they actually did
5. **Always present the full report before acting** — wait for the user to decide which suggestions to implement
