from pathlib import Path
import yaml
import pytest
from generate import load_sidecar, save_sidecar, list_templates


def test_load_sidecar_returns_none_when_missing(tmp_path):
    assert load_sidecar(tmp_path / "tailored.yaml") is None


def test_load_sidecar_returns_dict_when_present(tmp_path):
    (tmp_path / ".generate.yaml").write_text("template: modern\noutput: resume.pdf\n")
    result = load_sidecar(tmp_path / "tailored.yaml")
    assert result == {"template": "modern", "output": "resume.pdf"}


def test_save_sidecar_writes_correct_yaml(tmp_path):
    save_sidecar(tmp_path / "tailored.yaml", "modern", "resume.pdf")
    content = yaml.safe_load((tmp_path / ".generate.yaml").read_text())
    assert content == {"template": "modern", "output": "resume.pdf"}


def test_list_templates_includes_modern():
    templates = list_templates()
    names = [t["name"] for t in templates]
    assert "modern" in names


def test_list_templates_have_description():
    for t in list_templates():
        assert "description" in t and t["description"]
