# Adding a New Work Experience

Instructions for Claude Code to run an interactive interview, draft bullets, and insert a new work entry into `data/resume.yaml`.

---

## Overview

Greg has a master resume in `data/resume.yaml` with a consistent bullet style. When adding a new role, this workflow extracts raw experience through conversation, then translates it into bullets that match that style — without embellishment.

---

## Phase 1: Interview

Ask questions **one or two at a time**. Do not present a wall of questions. Use follow-up questions to dig into vague answers before moving on.

### 1. Role basics
Ask:
- Company name, job title
- Start date and end date (or "present")

### 2. Company context
Ask:
> "What did the company do? What was the product or service?"

Use the answer to write the `summary` field on the work entry.

### 3. Day-to-day responsibilities
Ask:
> "What was your role day-to-day? What were you primarily responsible for?"

### 4. Things built or created
Ask:
> "What did you build, create, or ship? What technologies did you use?"

Follow up if the answer is vague: "Can you name the specific language, framework, or tool?"

### 5. Accomplishments
Ask:
> "What's something you're proud of from this role? A problem you solved, or something that made a real difference?"

Follow up: "Do you remember any rough numbers — time saved, scale, or scope?"

### 6. Additional contributions
Ask:
> "Anything else worth capturing — side projects, process improvements, tools you built, things you learned on the job?"

### 7. New skills
Ask:
> "Did you use or learn any skills or technologies in this role that aren't already on your resume?"

---

## Phase 2: Draft Bullets

Before drafting, **read `data/resume.yaml`** to absorb the existing bullet voice and style.

### Style rules (from existing bullets)
- **Verb-led**: start with a past-tense action verb ("Developed", "Built", "Designed", "Implemented", "Adapted", "Created") — use past tense even for current roles
- **Technology-specific**: name the exact language, protocol, tool, or framework ("Elixir-based autopilot", "UAVCAN driver", "ROS on embedded Jetson TX2")
- **Outcome when available**: include results if the user provided them ("reducing turnaround by several days", "to improve maintainability")
- **No fluff**: no "responsible for", no "leveraged", no "spearheaded", no self-praise adjectives
- **Length**: 10–20 words; occasionally two lines for complex bullets
- **Scope signals**: mention vehicle type, system name, team context naturally when relevant

### Drafting rules
1. Draft 4–8 bullets from the interview answers
2. Only include what the user actually said — do not invent or infer
3. If the user described an outcome, include it; if they didn't, do not add one
4. Present all drafts to the user at once

### Iteration
- Show drafts and ask: "Does this sound right? Anything to change or add?"
- Revise until the user approves

---

## Phase 3: Write to YAML

Once bullets are approved:

### 1. Insert work entry
- Add to the `work:` list in **chronological order** (most recent first)
- Match the structure of existing entries:

```yaml
- name: Company Name
  position: Job Title
  startDate: "YYYY-MM"
  endDate: "YYYY-MM"          # omit entirely if current role
  summary: One-sentence description of the company or role focus.
  bullets:
    - text: "Verb-led bullet text matching existing style"
      tags: [tag1, tag2, tag3]
      priority: 1
    - text: "Another bullet"
      tags: [tag1]
      priority: 2
```

### 2. Assign tags
Tags should be lowercase, hyphen-separated, and drawn from or consistent with existing tags:
- Domain: `software`, `hardware`, `flight-test`, `embedded`, `uav`, `aerospace`
- Technology: `cpp`, `python`, `elixir`, `ros`, `matlab`, `arduino`, `pixhawk`, `ai`, `llm`
- Functional: `autopilot`, `simulation`, `testing`, `computer-vision`, `autonomous-systems`, `tooling`, `data-analysis`, `prototyping`, `pcb-design`

### 3. Assign priority
- `1` — core accomplishment, most likely to appear on any tailored resume
- `2` — solid supporting bullet, appears on most tailored resumes
- `3` — contextual detail, appears when the role is especially relevant
- `4` — edge case, included only for highly specific matches
- `5` — archive only, rarely or never selected

### 4. Add new skills
If the user identified new skills in Phase 1 Step 7, add them to the appropriate category in `skills:`. Add a new category if no existing one fits.

### 5. Validate YAML
```bash
python -c "import yaml; yaml.safe_load(open('data/resume.yaml'))"
```

No output = valid. Fix any errors before finishing.

---

## Hard Rules

1. **Never invent content** — bullets must reflect what the user actually described
2. **Never modify existing entries** — only add new content
3. **Never skip validation** — always run the YAML check after writing
4. **Omit `endDate` entirely for current roles** — an empty string fails schema validation
