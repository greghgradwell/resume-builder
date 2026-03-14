#!/usr/bin/env python3
import argparse
import tempfile
from pathlib import Path

import yaml

from pdf import generate_pdf
from render import load_yaml, render_html

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SIDECAR_NAME = ".generate.yaml"


def list_templates() -> list[dict]:
    templates = []
    for d in sorted(TEMPLATES_DIR.iterdir()):
        meta_file = d / "meta.yaml"
        if d.is_dir() and meta_file.exists():
            meta = yaml.safe_load(meta_file.read_text())
            if not isinstance(meta, dict):
                raise RuntimeError(f"Template '{d.name}': meta.yaml must be a YAML mapping")
            if "description" not in meta:
                raise RuntimeError(f"Template '{d.name}': meta.yaml missing required 'description' field")
            templates.append({**meta, "name": d.name})
    return templates


def load_sidecar(data_path: Path) -> dict | None:
    sidecar = data_path.parent / SIDECAR_NAME
    if not sidecar.exists():
        return None
    data = yaml.safe_load(sidecar.read_text())
    if not isinstance(data, dict) or "template" not in data or "output" not in data:
        raise RuntimeError(f"Malformed sidecar {sidecar}. Run with --reconfigure to recreate it.")
    return data


def save_sidecar(data_path: Path, template: str, output: str) -> None:
    sidecar = data_path.parent / SIDECAR_NAME
    sidecar.write_text(yaml.safe_dump({"output": output, "template": template}, sort_keys=True))


def prompt_settings(data_path: Path) -> tuple[str, Path]:
    templates = list_templates()
    if not templates:
        raise RuntimeError(f"No templates found in {TEMPLATES_DIR}")
    print("\nAvailable templates:\n")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t['name']:<12} — {t['description']}")

    while True:
        raw = input("\nSelect template [1]: ").strip() or "1"
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(templates):
                chosen = templates[idx]["name"]
                break
        except ValueError:
            pass
        print(f"  Enter a number between 1 and {len(templates)}.")

    default_output = "resume.pdf"
    raw_output = input(f"Output filename [{default_output}]: ").strip()
    output_path = data_path.parent / Path(raw_output or default_output).name

    return chosen, output_path


def resolve_tailored(tailored_data: dict, master_data: dict) -> dict:
    bullet_lookup: dict[str, str] = {}
    company_lookup: dict[str, list[dict]] = {}
    for job in master_data.get("work", []):
        company_lookup.setdefault(job["name"], []).append(job)
        for bullet in job.get("bullets", []):
            bid = bullet["id"]
            if bid in bullet_lookup:
                raise ValueError(f"Duplicate bullet ID '{bid}' in master resume")
            bullet_lookup[bid] = bullet["text"]

    pub_lookup: dict[str, dict] = {}
    for pub in master_data.get("publications", []):
        pub_lookup[pub["name"]] = pub

    resolved_work = []
    for entry in tailored_data.get("work", []):
        company = entry["name"]
        if company not in company_lookup:
            raise ValueError(f"Company '{company}' not found in master resume")

        candidates = company_lookup[company]
        if len(candidates) > 1:
            if "position" not in entry:
                raise ValueError(
                    f"Company '{company}' has multiple entries in master; "
                    f"add 'position:' to the tailored work entry for disambiguation"
                )
            position = entry["position"]
            matches = [j for j in candidates if j["position"] == position]
            if not matches:
                raise ValueError(f"No master entry for '{company}' with position '{position}'")
            master_job = matches[0]
        else:
            master_job = candidates[0]

        highlight_ids = entry.get("highlight_ids", [])
        highlights = []
        for bid in highlight_ids:
            if bid not in bullet_lookup:
                raise ValueError(f"Bullet ID '{bid}' not found in master (referenced by {company})")
            highlights.append(bullet_lookup[bid])

        resolved_entry: dict = {"name": master_job["name"], "position": master_job["position"]}
        for field in ("startDate", "endDate", "summary"):
            if field in master_job:
                resolved_entry[field] = master_job[field]
        resolved_entry["highlights"] = highlights
        resolved_work.append(resolved_entry)

    resolved_pubs = []
    for pub_entry in tailored_data.get("publications", []):
        name = pub_entry["name"]
        if name not in pub_lookup:
            raise ValueError(f"Publication '{name}' not found in master resume")
        resolved_pubs.append(pub_lookup[name])

    resolved = {k: v for k, v in tailored_data.items() if k != "source"}
    resolved["work"] = resolved_work
    if resolved_pubs:
        resolved["publications"] = resolved_pubs
    elif "publications" in resolved:
        del resolved["publications"]

    return resolved


def main():
    parser = argparse.ArgumentParser(description="Generate PDF resume from YAML")
    parser.add_argument("--data", required=True, help="Path to resume YAML file")
    parser.add_argument("--reconfigure", action="store_true", help="Re-prompt even if .generate.yaml exists")
    parser.add_argument("--keep-html", action="store_true", help="Also save the HTML alongside the PDF")
    args = parser.parse_args()

    data_path = Path(args.data).resolve()
    sidecar = None if args.reconfigure else load_sidecar(data_path)

    if sidecar:
        template = sidecar["template"]
        valid = {t["name"] for t in list_templates()}
        if template not in valid:
            raise ValueError(f"Unknown template '{template}' in sidecar. Run with --reconfigure to choose a new one.")
        output_path = data_path.parent / Path(sidecar["output"]).name
        print(f"\nUsing saved settings ({SIDECAR_NAME}):")
        print(f"  template: {template}")
        print(f"  output:   {output_path}\n")
    else:
        template, output_path = prompt_settings(data_path)
        save_sidecar(data_path, template, output_path.name)
        print(f"\nSaved settings to {data_path.parent / SIDECAR_NAME}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_yaml(str(data_path))

    if "source" in data:
        master_path = (PROJECT_ROOT / data["source"]).resolve()
        if not master_path.is_relative_to(PROJECT_ROOT):
            raise ValueError(f"'source' path escapes project root: {data['source']}")
        master = load_yaml(str(master_path))
        data = resolve_tailored(data, master)
    elif any("highlight_ids" in job for job in data.get("work", [])):
        raise ValueError("File contains 'highlight_ids' but no 'source' field")

    html = render_html(data, template=template)

    if args.keep_html:
        html_path = output_path.with_suffix(".html")
        html_path.write_text(html)
        print(f"Rendered:  {html_path}")
        pages = generate_pdf(str(html_path), str(output_path))
    else:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as tmp:
                tmp.write(html)
                tmp_path = tmp.name
            pages = generate_pdf(tmp_path, str(output_path))
        finally:
            if tmp_path is not None:
                Path(tmp_path).unlink(missing_ok=True)

    print(f"Generated: {output_path} ({pages} page{'s' if pages != 1 else ''})")


if __name__ == "__main__":
    main()
