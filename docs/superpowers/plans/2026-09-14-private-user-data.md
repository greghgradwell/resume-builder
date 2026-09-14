# Private User Data + Unpackable Example Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every user-data location gitignored by default, ship the fictional Robin Codewright example as one tracked archive that a first-time setup script unpacks, and block commits of personal data with a pre-commit hook.

**Architecture:** The example files currently tracked in place (`data/comprehensive_bio.yaml`, `data/jobs/example/`, `hand_crafted_resumes/*(example).pdf`) move into `examples/example-materials.tar.gz`, whose member paths equal their repo-relative destinations. `scripts/setup.py` extracts it (only when no master bio exists) and points `core.hooksPath` at a tracked `hooks/` directory whose `pre-commit` rejects staged personal-data paths. Tests stop reading user data and use a tracked fixture.

**Tech Stack:** Python 3.12 stdlib (`tarfile` with `filter="data"`, `subprocess`), POSIX sh hook, pytest, just.

**Spec:** Approved design (in-session plan `~/.claude/plans/first-of-all-i-cozy-lagoon.md`); this document is self-contained.

## Global Constraints

- Python **3.12+** (the tarfile `data` filter is relied on). Venv: `~/.venvs/resume-builder`; activate with `source ~/.venvs/resume-builder/bin/activate` before any `python`/`pytest`.
- No fallbacks: code works or fails explicitly. No try/except around expected operations.
- No docstrings; self-documenting names. Comments only for non-obvious *why*.
- Do not use `sys.path.insert` in tests (pytest `pythonpath = ["scripts"]` already handles imports). Do not wrap tests in classes.
- Never commit anything under `data/comprehensive_bio.yaml`, `data/jobs/`, or `hand_crafted_resumes/` other than `hand_crafted_resumes/.gitkeep`, and deletions of the currently tracked example files.
- Work only inside this worktree: `/home/ubuntu/Documents/Github/resume-builder/.claude/worktrees/private-user-data` (branch `worktree-private-user-data`). Never touch the main checkout at `/home/ubuntu/Documents/Github/resume-builder` (it holds the owner's real resume data).
- Do **not** push and do **not** open a PR.
- Commit messages end with:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```

## File Map

| Path | Action | Responsibility |
| --- | --- | --- |
| `examples/example-materials.tar.gz` | Create | The fictional example, packed with repo-relative member paths |
| `scripts/setup.py` | Create | First-run: unpack example if no bio exists; install hooks path |
| `hooks/pre-commit` | Create (executable) | Reject staged added/modified personal-data paths |
| `tests/test_setup.py` | Create | Tests for `setup.py`, the shipped archive, and the hook |
| `tests/fixtures/sample_bio.yaml` | Create | Tracked copy of the example bio for render tests |
| `tests/test_render.py` | Modify line 11 | Load fixture instead of `data/comprehensive_bio.yaml` |
| `.gitignore` | Modify | Ignore all user-data paths; drop example negations |
| `justfile` | Modify | Add `setup` and `pack-examples` recipes |
| `README.md`, `IMPORT_EXISTING.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules` | Modify | Document setup, privacy, Python 3.12 |
| 7 example files | `git rm --cached` → then delete from worktree | No longer tracked in place |

---

### Task 0: Rebuild the venv on Python 3.12

The existing venv is broken (`~/.venvs/resume-builder/pyvenv.cfg` has `home = /home/ubuntu/.platformio/penv/bin`, `version = 3.10.12`; `pip` and `yaml` fail to import).

**Files:** none in the repo.

- [ ] **Step 1: Set the broken venv aside (do not delete)**

```bash
mv ~/.venvs/resume-builder ~/.venvs/resume-builder.broken-20260914
```

- [ ] **Step 2: Create the new venv from system Python 3.12 and install deps**

```bash
/usr/bin/python3.12 -m venv ~/.venvs/resume-builder
source ~/.venvs/resume-builder/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 3: Verify**

```bash
source ~/.venvs/resume-builder/bin/activate
python --version
python -c "import yaml, jinja2, weasyprint, requests; print('ok')"
pytest -q
```
Expected: `Python 3.12.x`, `ok`, and all existing tests PASS (they still read the tracked example bio at this point).

If `weasyprint` import fails for missing system libraries, stop and report — do not attempt `sudo`.

No commit (nothing in the repo changed).

---

### Task 1: Decouple render tests from user data

**Files:**
- Create: `tests/fixtures/sample_bio.yaml`
- Modify: `tests/test_render.py:9-11`

**Interfaces:**
- Produces: `tests/fixtures/sample_bio.yaml` — a valid master bio (same schema as `data/comprehensive_bio.yaml`, `basics.name` = `Robin Codewright`).

- [ ] **Step 1: Create the fixture as an exact copy of the tracked example bio**

```bash
mkdir -p tests/fixtures
cp data/comprehensive_bio.yaml tests/fixtures/sample_bio.yaml
```

Then remove the first line `# EXAMPLE — replace with your own data via the import workflow` from `tests/fixtures/sample_bio.yaml` (it's a test fixture, not a user-facing example).

- [ ] **Step 2: Point the fixture at it**

In `tests/test_render.py` replace:

```python
@pytest.fixture
def resume_data():
    return load_yaml(str(PROJECT_ROOT / "data" / "comprehensive_bio.yaml"))
```

with:

```python
@pytest.fixture
def resume_data():
    return load_yaml(str(PROJECT_ROOT / "tests" / "fixtures" / "sample_bio.yaml"))
```

- [ ] **Step 3: Prove tests no longer depend on the data file**

```bash
source ~/.venvs/resume-builder/bin/activate
mv data/comprehensive_bio.yaml /home/ubuntu/.claude/jobs/977278ef/tmp/example-bio.bak
pytest -q
mv /home/ubuntu/.claude/jobs/977278ef/tmp/example-bio.bak data/comprehensive_bio.yaml
```
Expected: all tests PASS while the data file is absent. (Restore it — Task 2 needs it.)

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/sample_bio.yaml tests/test_render.py
git commit -m "$(cat <<'EOF'
test: render tests use a tracked fixture instead of the master bio

The master bio is about to become gitignored user data, so tests must
not depend on it existing.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Pack the example archive and verify its contents

**Files:**
- Create: `examples/example-materials.tar.gz`
- Create: `tests/test_setup.py`
- Modify: `justfile`

**Interfaces:**
- Produces: `examples/example-materials.tar.gz` with exactly these members (paths relative to repo root):
  - `data/comprehensive_bio.yaml`
  - `data/jobs/example/senior-cloud-platform-engineer/.generate.yaml`
  - `data/jobs/example/senior-cloud-platform-engineer/Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf`
  - `data/jobs/example/senior-cloud-platform-engineer/resume.pdf`
  - `data/jobs/example/senior-cloud-platform-engineer/tailored.yaml`
  - `hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf`
  - `hand_crafted_resumes/Robin Codewright - Full Stack Developer (example).pdf`

- [ ] **Step 1: Write the failing test**

Create `tests/test_setup.py`:

```python
import tarfile
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_ARCHIVE = PROJECT_ROOT / "examples" / "example-materials.tar.gz"

EXPECTED_EXAMPLE_FILES = {
    "data/comprehensive_bio.yaml",
    "data/jobs/example/senior-cloud-platform-engineer/.generate.yaml",
    "data/jobs/example/senior-cloud-platform-engineer/Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf",
    "data/jobs/example/senior-cloud-platform-engineer/resume.pdf",
    "data/jobs/example/senior-cloud-platform-engineer/tailored.yaml",
    "hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf",
    "hand_crafted_resumes/Robin Codewright - Full Stack Developer (example).pdf",
}


def test_example_archive_contains_exactly_the_example_files():
    with tarfile.open(EXAMPLE_ARCHIVE) as archive:
        file_names = {member.name for member in archive.getmembers() if member.isfile()}
    assert file_names == EXPECTED_EXAMPLE_FILES


def test_example_archive_bio_is_the_fictional_example():
    with tarfile.open(EXAMPLE_ARCHIVE) as archive:
        bio = yaml.safe_load(archive.extractfile("data/comprehensive_bio.yaml"))
    assert bio["basics"]["name"] == "Robin Codewright"
```

- [ ] **Step 2: Run to verify it fails**

```bash
source ~/.venvs/resume-builder/bin/activate
pytest tests/test_setup.py -v
```
Expected: FAIL with `FileNotFoundError` for `examples/example-materials.tar.gz`.

- [ ] **Step 3: Add the `pack-examples` recipe to `justfile`**

Append after the existing `examples` recipe:

```just
# Pack the example files into the tracked archive (run after `just examples` or editing the example)
pack-examples:
    tar czf examples/example-materials.tar.gz \
        data/comprehensive_bio.yaml \
        data/jobs/example/senior-cloud-platform-engineer/.generate.yaml \
        "data/jobs/example/senior-cloud-platform-engineer/Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf" \
        data/jobs/example/senior-cloud-platform-engineer/resume.pdf \
        data/jobs/example/senior-cloud-platform-engineer/tailored.yaml \
        "hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf" \
        "hand_crafted_resumes/Robin Codewright - Full Stack Developer (example).pdf"
```

- [ ] **Step 4: Build the archive**

```bash
mkdir -p examples
just pack-examples
```
If `just` is not installed, run the identical `tar czf ...` command from the recipe directly.

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_setup.py -v
```
Expected: both tests PASS.

- [ ] **Step 6: Commit**

```bash
git add examples/example-materials.tar.gz tests/test_setup.py justfile
git commit -m "$(cat <<'EOF'
feat: pack the fictional example into a tracked archive

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Pre-commit hook that blocks personal data

**Files:**
- Create: `hooks/pre-commit` (mode 755)
- Modify: `tests/test_setup.py`

**Interfaces:**
- Produces: `hooks/pre-commit` — exits 1 and lists offending paths when any staged **added/copied/modified/renamed** path matches `data/comprehensive_bio.yaml`, `data/jobs/…`, or `hand_crafted_resumes/…` (except `hand_crafted_resumes/.gitkeep`); exits 0 otherwise. Deletions are allowed.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_setup.py`:

```python
import shutil
import subprocess

import pytest

HOOK_SOURCE = PROJECT_ROOT / "hooks" / "pre-commit"


def run_git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


@pytest.fixture
def repo_with_hook(tmp_path):
    run_git(tmp_path, "init", "-q")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    run_git(tmp_path, "config", "user.name", "Test")
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    shutil.copy2(HOOK_SOURCE, hooks_dir / "pre-commit")
    run_git(tmp_path, "config", "core.hooksPath", "hooks")
    return tmp_path


def stage_file(repo, relative_path):
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("content\n")
    run_git(repo, "add", "-f", relative_path)


@pytest.mark.parametrize(
    "personal_path",
    [
        "data/comprehensive_bio.yaml",
        "data/jobs/acme/engineer/tailored.yaml",
        "hand_crafted_resumes/my resume.pdf",
    ],
)
def test_hook_blocks_personal_data(repo_with_hook, personal_path):
    stage_file(repo_with_hook, personal_path)
    result = run_git(repo_with_hook, "commit", "-q", "-m", "leak")
    assert result.returncode != 0
    assert personal_path in result.stderr


@pytest.mark.parametrize(
    "safe_path",
    ["scripts/tool.py", "hand_crafted_resumes/.gitkeep", "docs/data/jobs/notes.md"],
)
def test_hook_allows_non_personal_paths(repo_with_hook, safe_path):
    stage_file(repo_with_hook, safe_path)
    result = run_git(repo_with_hook, "commit", "-q", "-m", "ok")
    assert result.returncode == 0, result.stderr


def test_hook_allows_deleting_previously_tracked_personal_path(repo_with_hook):
    run_git(repo_with_hook, "config", "core.hooksPath", "/dev/null")
    stage_file(repo_with_hook, "data/comprehensive_bio.yaml")
    run_git(repo_with_hook, "commit", "-q", "-m", "seed")
    run_git(repo_with_hook, "config", "core.hooksPath", "hooks")
    run_git(repo_with_hook, "rm", "-q", "--cached", "data/comprehensive_bio.yaml")
    result = run_git(repo_with_hook, "commit", "-q", "-m", "untrack")
    assert result.returncode == 0, result.stderr
```

Move the new `import shutil`, `import subprocess`, and `import pytest` lines up into the import block at the top of the file.

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/test_setup.py -v -k hook
```
Expected: FAIL — `FileNotFoundError` copying `hooks/pre-commit`.

- [ ] **Step 3: Write the hook**

Create `hooks/pre-commit`:

```sh
#!/bin/sh
# Personal resume data lives in these paths; .gitignore keeps it out, this catches `git add -f`.
blocked=$(git diff --cached --name-only --diff-filter=ACMR \
    | grep -E '^(data/comprehensive_bio\.yaml$|data/jobs/|hand_crafted_resumes/)' \
    | grep -v '^hand_crafted_resumes/\.gitkeep$')

if [ -n "$blocked" ]; then
    echo "Commit blocked: these paths hold personal resume data and must not be committed:" >&2
    echo "$blocked" | sed 's/^/  /' >&2
    echo "Unstage them with: git restore --staged <path>" >&2
    exit 1
fi
```

```bash
chmod 755 hooks/pre-commit
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_setup.py -v -k hook
```
Expected: all 7 hook tests PASS.

- [ ] **Step 5: Commit**

```bash
git add hooks/pre-commit tests/test_setup.py
git update-index --chmod=+x hooks/pre-commit
git commit -m "$(cat <<'EOF'
feat: pre-commit hook blocks committing personal resume data

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: `scripts/setup.py` — unpack example and install hooks

**Files:**
- Create: `scripts/setup.py`
- Modify: `tests/test_setup.py`

**Interfaces:**
- Consumes: `examples/example-materials.tar.gz` (Task 2), `hooks/` (Task 3).
- Produces:
  - `unpack_example(archive_path: Path, project_root: Path) -> bool` — if `project_root / "data" / "comprehensive_bio.yaml"` exists, returns `False` and writes nothing; otherwise extracts the archive into `project_root` with `filter="data"` and returns `True`.
  - `install_hooks(project_root: Path) -> None` — runs `git -C <project_root> config core.hooksPath hooks`, `check=True`.
  - `main()` — calls both for `PROJECT_ROOT`, prints outcome and next steps.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_setup.py` (put `import io` and `from setup import unpack_example, install_hooks` in the top import block):

```python
def build_archive(archive_path, members):
    with tarfile.open(archive_path, "w:gz") as archive:
        for name, content in members.items():
            data = content.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


def test_unpack_example_places_files_when_no_bio_exists(tmp_path):
    archive_path = tmp_path / "example.tar.gz"
    build_archive(
        archive_path,
        {
            "data/comprehensive_bio.yaml": "basics: {name: Example}\n",
            "hand_crafted_resumes/example.pdf": "pdf",
        },
    )
    project_root = tmp_path / "project"
    project_root.mkdir()

    assert unpack_example(archive_path, project_root) is True
    assert (project_root / "data" / "comprehensive_bio.yaml").read_text() == "basics: {name: Example}\n"
    assert (project_root / "hand_crafted_resumes" / "example.pdf").read_text() == "pdf"


def test_unpack_example_never_overwrites_existing_bio(tmp_path):
    archive_path = tmp_path / "example.tar.gz"
    build_archive(
        archive_path,
        {
            "data/comprehensive_bio.yaml": "basics: {name: Example}\n",
            "data/jobs/example/tailored.yaml": "work: []\n",
        },
    )
    project_root = tmp_path / "project"
    bio = project_root / "data" / "comprehensive_bio.yaml"
    bio.parent.mkdir(parents=True)
    bio.write_text("basics: {name: Real Person}\n")

    assert unpack_example(archive_path, project_root) is False
    assert bio.read_text() == "basics: {name: Real Person}\n"
    assert not (project_root / "data" / "jobs").exists()


def test_unpack_example_rejects_paths_outside_project(tmp_path):
    archive_path = tmp_path / "evil.tar.gz"
    build_archive(archive_path, {"../escaped.txt": "nope"})
    project_root = tmp_path / "project"
    project_root.mkdir()

    with pytest.raises(tarfile.FilterError):
        unpack_example(archive_path, project_root)
    assert not (tmp_path / "escaped.txt").exists()


def test_install_hooks_sets_hooks_path(tmp_path):
    run_git(tmp_path, "init", "-q")
    install_hooks(tmp_path)
    assert run_git(tmp_path, "config", "core.hooksPath").stdout.strip() == "hooks"


def test_real_example_archive_unpacks_into_fresh_project(tmp_path):
    assert unpack_example(EXAMPLE_ARCHIVE, tmp_path) is True
    unpacked = {
        str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*") if path.is_file()
    }
    assert unpacked == EXPECTED_EXAMPLE_FILES
```

- [ ] **Step 2: Run to verify they fail**

```bash
pytest tests/test_setup.py -v
```
Expected: collection error — `ModuleNotFoundError: No module named 'setup'`.

- [ ] **Step 3: Write `scripts/setup.py`**

```python
#!/usr/bin/env python3
import subprocess
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_ARCHIVE = PROJECT_ROOT / "examples" / "example-materials.tar.gz"
EXAMPLE_TAILORED = "data/jobs/example/senior-cloud-platform-engineer/tailored.yaml"


def unpack_example(archive_path: Path, project_root: Path) -> bool:
    # The example tailored.yaml references example bullet IDs, so the example is useless next to a real bio.
    if (project_root / "data" / "comprehensive_bio.yaml").exists():
        return False
    with tarfile.open(archive_path) as archive:
        archive.extractall(project_root, filter="data")
    return True


def install_hooks(project_root: Path) -> None:
    subprocess.run(["git", "-C", str(project_root), "config", "core.hooksPath", "hooks"], check=True)


def main():
    if unpack_example(EXAMPLE_ARCHIVE, PROJECT_ROOT):
        print("Unpacked the Robin Codewright example:")
        print("  data/comprehensive_bio.yaml       master bio built from the source resumes")
        print("  hand_crafted_resumes/*(example)*  the source resumes it was imported from")
        print("  data/jobs/example/                a tailored resume for an example job")
        print()
        print("Try the pipeline:")
        print(f"  python scripts/generate.py --data {EXAMPLE_TAILORED}")
    else:
        print("data/comprehensive_bio.yaml already exists; example not unpacked.")

    install_hooks(PROJECT_ROOT)
    print()
    print("Installed git hooks: commits containing personal resume data will be blocked.")
    print("When ready, drop your own resumes into hand_crafted_resumes/ and ask your AI assistant")
    print('to "Import my resumes from hand_crafted_resumes/".')


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest -q
```
Expected: entire suite PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/setup.py tests/test_setup.py
git commit -m "$(cat <<'EOF'
feat: setup script unpacks the example and installs git hooks

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Untrack the example files and make user data private by default

**Files:**
- Modify: `.gitignore`
- Modify: `justfile` (add `setup` recipe)
- Untrack: the 7 files listed in Task 2

- [ ] **Step 1: Replace `.gitignore` with**

```gitignore
__pycache__/
*.pyc
.venv/
venv/
node_modules/
*.pdf
.env
instance/
.vscode/

# Personal resume data — never committed. `python scripts/setup.py` unpacks the
# fictional example into these paths; your own data replaces it.
data/comprehensive_bio.yaml
data/jobs/*
hand_crafted_resumes/*
!hand_crafted_resumes/.gitkeep
```

(`*.pdf` stays so generated PDFs elsewhere remain ignored; `data/jobs/**/*.html` is subsumed by `data/jobs/*`. The archive in `examples/` is `.tar.gz`, so it is not affected.)

- [ ] **Step 2: Untrack the example files**

```bash
git rm -q --cached \
  data/comprehensive_bio.yaml \
  data/jobs/example/senior-cloud-platform-engineer/.generate.yaml \
  "data/jobs/example/senior-cloud-platform-engineer/Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf" \
  data/jobs/example/senior-cloud-platform-engineer/resume.pdf \
  data/jobs/example/senior-cloud-platform-engineer/tailored.yaml \
  "hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf" \
  "hand_crafted_resumes/Robin Codewright - Full Stack Developer (example).pdf"
```

- [ ] **Step 3: Add a `setup` recipe to `justfile`** (after `fonts`)

```just
# First-time setup: unpack the example and install git hooks
setup:
    {{python}} scripts/setup.py
```

- [ ] **Step 4: Verify tracking and ignore state**

```bash
git ls-files data hand_crafted_resumes
git status --short
git check-ignore -v data/comprehensive_bio.yaml data/jobs/example/senior-cloud-platform-engineer/tailored.yaml "hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf"
```
Expected: `git ls-files` prints only `hand_crafted_resumes/.gitkeep`; status shows the 7 deletions staged plus `.gitignore`/`justfile` modified and nothing untracked under `data/` or `hand_crafted_resumes/`; `check-ignore` reports a matching rule for all three paths.

- [ ] **Step 5: Run tests**

```bash
pytest -q
```
Expected: PASS.

- [ ] **Step 6: Commit (activate the hook first to prove deletions pass through it)**

```bash
git config core.hooksPath hooks
git add .gitignore justfile
git commit -m "$(cat <<'EOF'
feat: keep user resume data private by default

Stop tracking the example in place; it now ships in
examples/example-materials.tar.gz and is unpacked by scripts/setup.py.
All user-data paths are gitignored.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```
Expected: commit succeeds (hook allows deletions). Note: worktrees share `.git/config`, so this also sets `core.hooksPath` for the main checkout — intended; it has no `hooks/` dir until this branch merges, so nothing changes there yet.

---

### Task 6: Documentation and Python 3.12

**Files:**
- Modify: `README.md`, `IMPORT_EXISTING.md:32`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`

`CLAUDE.md` and `GEMINI.md` are byte-identical today; keep them identical. `.cursorrules` carries the same Project Structure/Conventions lines — apply the same edits there where the lines exist.

- [ ] **Step 1: `README.md`**

1. Installation step 1 code block → `python3.12 -m venv .venv && source .venv/bin/activate`
2. After step 4 (Fonts), add:
   ````markdown
   5. **Example + git hooks:**
      ```bash
      python scripts/setup.py
      ```
      Unpacks a complete fictional example (Robin Codewright) and installs a pre-commit hook that blocks committing personal resume data.
   ````
3. Replace the Quick Start intro paragraph (line 56) with:
   ```markdown
   `python scripts/setup.py` unpacks an end-to-end example: Robin Codewright's source resumes in `hand_crafted_resumes/`, the master file imported from them at `data/comprehensive_bio.yaml`, and a tailored resume in `data/jobs/example/`. Run `python scripts/generate.py --data data/jobs/example/senior-cloud-platform-engineer/tailored.yaml` to see the pipeline produce a PDF, then replace the example with your own data.
   ```
4. After the Quick Start list paragraph ("The more resumes you feed…"), add:
   ```markdown
   ### Your data stays private

   Everything personal — `data/comprehensive_bio.yaml`, `data/jobs/`, and `hand_crafted_resumes/` — is gitignored, so you can keep your resume data in your clone of this repo without it reaching a public remote. The pre-commit hook installed by `setup.py` also rejects those paths if they are force-added.
   ```
5. Project Structure block: mark `comprehensive_bio.yaml` as `# Master resume (single source of truth, gitignored)`, change `hand_crafted_resumes/` comment to `# Your existing resumes go here (gitignored)`, change `.generate.yaml` comment to `# Saved template + output settings`, and add lines:
   ```
   examples/
     example-materials.tar.gz        # Fictional example, unpacked by scripts/setup.py
   hooks/
     pre-commit                      # Blocks committing personal data
   ```
   plus under `scripts/`: `  setup.py                        # First-time setup: example + git hooks`
6. Commands block: add `python scripts/setup.py                                                  # Unpack example + install hooks`; just block: add `just setup              # Unpack example + install hooks` and `just pack-examples      # Rebuild examples/example-materials.tar.gz`.
7. Requirements: `Python 3.10+` → `Python 3.12+`.

- [ ] **Step 2: `IMPORT_EXISTING.md:32`**

Replace:
```markdown
Before writing anything, read `data/comprehensive_bio.yaml` — this ships with example data demonstrating the expected structure, field names, and formatting conventions. Your output will replace it and must match this structure precisely.
```
with:
```markdown
Before writing anything, read `data/comprehensive_bio.yaml` — `python scripts/setup.py` unpacks example data there demonstrating the expected structure, field names, and formatting conventions. If it doesn't exist, run that script first. Your output will replace it and must match this structure precisely.
```

- [ ] **Step 3: `CLAUDE.md`, `GEMINI.md`, `.cursorrules`**

- `data/comprehensive_bio.yaml` line → `` - `data/comprehensive_bio.yaml` — Master resume data (single source of truth; gitignored personal data) ``
- `.generate.yaml` line → `` - `data/jobs/<company>/<role>/.generate.yaml` — Sidecar: saved template + output path ``  (drop "(commit this)" — `data/jobs/` is gitignored)
- Add after `scripts/fetch_fonts.py` line: `` - `scripts/setup.py` — First-time setup: unpacks `examples/example-materials.tar.gz`, installs git hooks ``
- Add: `` - `hooks/pre-commit` — Blocks commits of personal data (`data/comprehensive_bio.yaml`, `data/jobs/`, `hand_crafted_resumes/`) ``
- Commands: add `` - `python scripts/setup.py` — Unpack example (only if no master bio exists) + install git hooks ``
- Conventions: `Python 3.10+` → `Python 3.12+`
- Add a Conventions bullet: `- Never commit personal resume data; never bypass the pre-commit hook`

Verify identical: `diff CLAUDE.md GEMINI.md` prints nothing.

- [ ] **Step 4: Check for stale references**

```bash
grep -rn "3\.10\|ships with example\|examples tracked\|commit this" --include="*.md" --include=".cursorrules" . | grep -v docs/superpowers
```
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add README.md IMPORT_EXISTING.md CLAUDE.md GEMINI.md .cursorrules
git commit -m "$(cat <<'EOF'
docs: document setup script, private user data, and Python 3.12

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: End-to-end verification in a fresh clone

**Files:** none (verification only; nothing committed).

- [ ] **Step 1: Clone the branch fresh**

```bash
rm -rf /home/ubuntu/.claude/jobs/977278ef/tmp/fresh
git clone -q --branch worktree-private-user-data \
  /home/ubuntu/Documents/Github/resume-builder/.claude/worktrees/private-user-data \
  /home/ubuntu/.claude/jobs/977278ef/tmp/fresh
cd /home/ubuntu/.claude/jobs/977278ef/tmp/fresh
ls data hand_crafted_resumes -a
```
Expected: `data` does not exist; `hand_crafted_resumes` contains only `.gitkeep`.

- [ ] **Step 2: Run setup and the pipeline**

```bash
source ~/.venvs/resume-builder/bin/activate
python scripts/setup.py
git status --short
git config core.hooksPath
python scripts/generate.py --data data/jobs/example/senior-cloud-platform-engineer/tailored.yaml
```
Expected: setup prints the "Unpacked" message; `git status --short` prints nothing; hooksPath is `hooks`; generate uses the existing `.generate.yaml` sidecar (no prompt) and writes `data/jobs/example/senior-cloud-platform-engineer/resume.pdf`.

- [ ] **Step 3: Re-run setup is safe**

```bash
echo "# sentinel" >> data/comprehensive_bio.yaml
python scripts/setup.py
tail -1 data/comprehensive_bio.yaml
```
Expected: "already exists; example not unpacked"; last line is still `# sentinel`.

- [ ] **Step 4: Hook blocks a forced add**

```bash
git add -f data/comprehensive_bio.yaml
git commit -m "should be blocked"; echo "exit=$?"
git restore --staged data/comprehensive_bio.yaml
```
Expected: `Commit blocked: …data/comprehensive_bio.yaml`, `exit=1`.

- [ ] **Step 5: Full test suite in the fresh clone and clean up**

```bash
pytest -q
cd /home/ubuntu/Documents/Github/resume-builder/.claude/worktrees/private-user-data
rm -rf /home/ubuntu/.claude/jobs/977278ef/tmp/fresh
```
Expected: PASS.

- [ ] **Step 6: Report**

Report: commits made (`git log --oneline main..HEAD`), test results, and the outcome of each Task 7 step. Do not push.
