#!/usr/bin/env python3

import re
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = PROJECT_ROOT / "fonts"

FONT_SPECS = {
    "Inter": [400, 500, 600, 700],
    "Lato": [400, 700],
    "Source Sans 3": [400, 600, 700],
    "Montserrat": [500, 600, 700],
    "Raleway": [500, 600, 700],
    "Merriweather": [400, 700],
    "Source Serif 4": [400, 600, 700],
}

WEIGHT_NAMES = {
    400: "regular",
    500: "medium",
    600: "semibold",
    700: "bold",
}

# User-Agent strings to get different font formats from Google Fonts CSS v2 API
UA_WOFF2 = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
UA_TTF = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"

GOOGLE_FONTS_CSS_URL = "https://fonts.googleapis.com/css2"


def build_css_url(family: str, weights: list[int]) -> str:
    weight_str = ";".join(str(w) for w in sorted(weights))
    family_param = f"family={family.replace(' ', '+')}:wght@{weight_str}"
    return f"{GOOGLE_FONTS_CSS_URL}?{family_param}&display=swap"


def parse_font_faces(css_text: str, latin_only: bool = True) -> list[dict]:
    faces = []
    # Split into blocks by @font-face, keeping any preceding comments
    blocks = re.finditer(
        r"(?:/\*\s*([\w-]+)\s*\*/\s*)?@font-face\s*\{([^}]+)\}",
        css_text,
        re.DOTALL,
    )
    for block in blocks:
        subset_comment = block.group(1)  # None if no comment present
        # If subset comments exist and we want latin only, filter
        if latin_only and subset_comment is not None and subset_comment != "latin":
            continue

        body = block.group(2)
        family_match = re.search(r"font-family:\s*'([^']+)'", body)
        weight_match = re.search(r"font-weight:\s*(\d+)", body)
        style_match = re.search(r"font-style:\s*(\w+)", body)
        url_match = re.search(r"url\(([^)]+)\)", body)

        if not all([family_match, weight_match, url_match]):
            continue

        faces.append(
            {
                "family": family_match.group(1),
                "weight": int(weight_match.group(1)),
                "style": style_match.group(1) if style_match else "normal",
                "url": url_match.group(1),
            }
        )
    return faces


def download_file(url: str, dest: Path) -> None:
    if dest.exists():
        return
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    print(f"  Downloaded: {dest.relative_to(PROJECT_ROOT)}")


def font_filename(family: str, weight: int, ext: str) -> str:
    family_slug = family.lower().replace(" ", "-")
    weight_name = WEIGHT_NAMES.get(weight, str(weight))
    return f"{family_slug}-{weight_name}.{ext}"


def fetch_font_family(family: str, weights: list[int]) -> list[dict]:
    family_dir = FONTS_DIR / family.lower().replace(" ", "-")
    downloaded = []

    # TTF: Google Fonts legacy UA only returns one weight per request
    for weight in weights:
        css_url = build_css_url(family, [weight])
        resp = requests.get(css_url, headers={"User-Agent": UA_TTF}, timeout=30)
        resp.raise_for_status()
        faces = parse_font_faces(resp.text)
        for face in faces:
            dest = family_dir / font_filename(face["family"], face["weight"], "ttf")
            download_file(face["url"], dest)
            downloaded.append(
                {
                    "family": face["family"],
                    "weight": face["weight"],
                    "style": face["style"],
                    "ttf_path": str(dest.relative_to(FONTS_DIR)),
                    "woff2_path": str(
                        (
                            family_dir / font_filename(face["family"], face["weight"], "woff2")
                        ).relative_to(FONTS_DIR)
                    ),
                }
            )

    # WOFF2: single request with all weights, filter latin subset
    css_url = build_css_url(family, weights)
    resp = requests.get(css_url, headers={"User-Agent": UA_WOFF2}, timeout=30)
    resp.raise_for_status()
    for face in parse_font_faces(resp.text):
        dest = family_dir / font_filename(face["family"], face["weight"], "woff2")
        download_file(face["url"], dest)

    return downloaded


def generate_fonts_css(all_faces: list[dict]) -> str:
    lines = []
    for face in all_faces:
        lines.append(
            f"""@font-face {{
  font-family: '{face["family"]}';
  font-style: {face["style"]};
  font-weight: {face["weight"]};
  font-display: swap;
  src: url('{face["woff2_path"]}') format('woff2'),
       url('{face["ttf_path"]}') format('truetype');
}}"""
        )
    return "\n\n".join(lines) + "\n"


def main():
    print("Fetching Google Fonts...\n")
    all_faces = []

    for family, weights in FONT_SPECS.items():
        print(f"[{family}] weights: {weights}")
        faces = fetch_font_family(family, weights)
        all_faces.extend(faces)

    css_content = generate_fonts_css(all_faces)
    css_path = FONTS_DIR / "fonts.css"
    css_path.write_text(css_content)
    print(f"\nGenerated: {css_path.relative_to(PROJECT_ROOT)}")
    print(f"Total font faces: {len(all_faces)}")


if __name__ == "__main__":
    main()
