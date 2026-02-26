from pathlib import Path
import pytest
from jinja2 import TemplateNotFound
from render import render_html, load_yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_render_html_contains_name():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert data["basics"]["name"] in html


def test_render_html_links_style_css():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert "modern/style.css" in html


def test_render_html_links_base_css():
    data = load_yaml(str(PROJECT_ROOT / "data" / "resume.yaml"))
    html = render_html(data, template="modern")
    assert "templates/base.css" in html


def test_render_html_unknown_template_raises():
    with pytest.raises(TemplateNotFound):
        render_html({}, template="nonexistent")
