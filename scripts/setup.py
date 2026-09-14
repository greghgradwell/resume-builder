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
