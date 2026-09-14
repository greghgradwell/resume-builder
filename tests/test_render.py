from pathlib import Path
import pytest
from jinja2 import TemplateNotFound
from render import render_html, load_yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def resume_data():
    return load_yaml(str(PROJECT_ROOT / "tests" / "fixtures" / "sample_bio.yaml"))


@pytest.fixture
def modern_html(resume_data):
    return render_html(resume_data, template="modern")


def test_render_html_contains_name(modern_html, resume_data):
    assert resume_data["basics"]["name"] in modern_html


def test_render_html_links_style_css(modern_html):
    assert "modern/style.css" in modern_html


def test_render_html_links_base_css(modern_html):
    assert "templates/base.css" in modern_html


def work_entry_html(**job_fields):
    job = {"name": "Acme", "position": "Engineer", "startDate": "2022-01", "highlights": ["Did things"]}
    return render_html({"basics": {"name": "Test"}, "work": [{**job, **job_fields}]}, template="modern")


def test_render_html_shows_work_location_after_company():
    assert '<div class="entry-subtitle">Acme · Austin, TX</div>' in work_entry_html(location="Austin, TX")


def test_render_html_shows_company_alone_without_location():
    assert '<div class="entry-subtitle">Acme</div>' in work_entry_html()


def test_render_html_unknown_template_raises():
    with pytest.raises(TemplateNotFound):
        render_html({}, template="nonexistent")
