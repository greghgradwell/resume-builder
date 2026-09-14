import io
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest
import yaml
from setup import unpack_example, install_hooks

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
