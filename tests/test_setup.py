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
