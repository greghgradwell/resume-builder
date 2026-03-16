import pytest
import yaml
from generate import load_sidecar, save_sidecar, list_templates, prompt_settings, resolve_tailored


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


FAKE_TEMPLATES = [
    {"name": "alpha", "description": "First template"},
    {"name": "beta", "description": "Second template"},
]


def test_prompt_settings_selects_template_by_number(tmp_path, monkeypatch):
    monkeypatch.setattr("generate.list_templates", lambda: FAKE_TEMPLATES)
    inputs = iter(["1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    chosen, output_path = prompt_settings(tmp_path / "tailored.yaml")
    assert chosen == "alpha"
    assert output_path == tmp_path / "resume.pdf"


def test_prompt_settings_defaults_to_first_on_empty_input(tmp_path, monkeypatch):
    monkeypatch.setattr("generate.list_templates", lambda: FAKE_TEMPLATES)
    inputs = iter(["", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    chosen, _ = prompt_settings(tmp_path / "tailored.yaml")
    assert chosen == "alpha"


def test_prompt_settings_raises_when_no_templates(tmp_path, monkeypatch):
    monkeypatch.setattr("generate.list_templates", lambda: [])
    with pytest.raises(RuntimeError):
        prompt_settings(tmp_path / "tailored.yaml")


# ── resolve_tailored ─────────────────────────────────────────────────────────

MASTER = {
    "work": [
        {
            "name": "Acme",
            "position": "Engineer",
            "startDate": "2022-01",
            "endDate": "2023-06",
            "summary": "Built things.",
            "bullets": [
                {"id": "aabbccdd", "text": "Did the first thing", "tags": [], "priority": 1},
                {"id": "11223344", "text": "Did the second thing", "tags": [], "priority": 2},
            ],
        },
        {
            "name": "Dual Corp",
            "position": "Junior Engineer",
            "startDate": "2020-01",
            "endDate": "2021-12",
            "summary": "First role.",
            "bullets": [{"id": "aaaaaaaa", "text": "Junior work", "tags": [], "priority": 1}],
        },
        {
            "name": "Dual Corp",
            "position": "Senior Engineer",
            "startDate": "2021-12",
            "endDate": "2022-01",
            "summary": "Second role.",
            "bullets": [{"id": "bbbbbbbb", "text": "Senior work", "tags": [], "priority": 1}],
        },
    ],
    "publications": [
        {"name": "My Paper", "publisher": "ICUAS", "releaseDate": "2020-01-01", "summary": "..."}
    ],
}


def test_resolve_tailored_happy_path():
    tailored = {
        "source": "data/comprehensive_bio.yaml",
        "basics": {"name": "Test"},
        "work": [{"name": "Acme", "highlight_ids": ["11223344", "aabbccdd"]}],
    }
    result = resolve_tailored(tailored, MASTER)
    assert "source" not in result
    assert len(result["work"]) == 1
    job = result["work"][0]
    assert job["name"] == "Acme"
    assert job["position"] == "Engineer"
    assert job["startDate"] == "2022-01"
    assert job["endDate"] == "2023-06"
    assert job["summary"] == "Built things."
    assert job["highlights"] == ["Did the second thing", "Did the first thing"]


def test_resolve_tailored_publication_resolved_from_master():
    tailored = {
        "source": "data/comprehensive_bio.yaml",
        "work": [],
        "publications": [{"name": "My Paper"}],
    }
    result = resolve_tailored(tailored, MASTER)
    assert result["publications"] == [MASTER["publications"][0]]


def test_resolve_tailored_no_publications_removes_key():
    tailored = {"source": "data/comprehensive_bio.yaml", "work": [], "publications": []}
    result = resolve_tailored(tailored, MASTER)
    assert "publications" not in result


def test_resolve_tailored_disambiguates_by_position():
    tailored = {
        "source": "data/comprehensive_bio.yaml",
        "work": [
            {"name": "Dual Corp", "position": "Senior Engineer", "highlight_ids": ["bbbbbbbb"]}
        ],
    }
    result = resolve_tailored(tailored, MASTER)
    assert result["work"][0]["highlights"] == ["Senior work"]


def test_resolve_tailored_raises_on_duplicate_bullet_id():
    bad_master = {
        "work": [
            {
                "name": "X",
                "bullets": [{"id": "dup00000", "text": "a"}, {"id": "dup00000", "text": "b"}],
            }
        ]
    }
    with pytest.raises(ValueError, match="Duplicate bullet ID 'dup00000'"):
        resolve_tailored({"work": []}, bad_master)


def test_resolve_tailored_raises_on_unknown_company():
    tailored = {"work": [{"name": "Ghost Corp", "highlight_ids": []}]}
    with pytest.raises(ValueError, match="Company 'Ghost Corp' not found"):
        resolve_tailored(tailored, MASTER)


def test_resolve_tailored_raises_on_ambiguous_company_without_position():
    tailored = {"work": [{"name": "Dual Corp", "highlight_ids": []}]}
    with pytest.raises(ValueError, match="multiple entries"):
        resolve_tailored(tailored, MASTER)


def test_resolve_tailored_raises_on_unknown_position():
    tailored = {"work": [{"name": "Dual Corp", "position": "VP", "highlight_ids": []}]}
    with pytest.raises(ValueError, match="No master entry for 'Dual Corp' with position 'VP'"):
        resolve_tailored(tailored, MASTER)


def test_resolve_tailored_raises_on_unknown_bullet_id():
    tailored = {"work": [{"name": "Acme", "highlight_ids": ["deadbeef"]}]}
    with pytest.raises(ValueError, match="Bullet ID 'deadbeef' not found"):
        resolve_tailored(tailored, MASTER)


def test_resolve_tailored_raises_on_unknown_publication():
    tailored = {"work": [], "publications": [{"name": "Nonexistent Paper"}]}
    with pytest.raises(ValueError, match="Publication 'Nonexistent Paper' not found"):
        resolve_tailored(tailored, MASTER)


def test_source_path_traversal_rejected(tmp_path):
    evil_yaml = tmp_path / "evil.yaml"
    evil_yaml.write_text("secret: data\n")
    relative_escape = "../" * 10 + str(evil_yaml).lstrip("/")
    tailored_path = tmp_path / "tailored.yaml"
    tailored_path.write_text(f"source: {relative_escape}\nwork: []\n")

    import yaml as _yaml
    from generate import PROJECT_ROOT as _root

    data = _yaml.safe_load(tailored_path.read_text())
    candidate = (_root / data["source"]).resolve()
    assert not candidate.is_relative_to(_root)
