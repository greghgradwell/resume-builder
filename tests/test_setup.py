import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_ARCHIVE = PROJECT_ROOT / "examples" / "example-materials.tar.gz"
HOOK_SOURCE = PROJECT_ROOT / "hooks" / "pre-commit"

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
