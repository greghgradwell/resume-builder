python := "python"

# Regenerate the most recently modified tailored.yaml
regen:
    #!/usr/bin/env bash
    latest=$(find jobs -name 'tailored.yaml' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -z "$latest" ]; then
        echo "No tailored.yaml found in jobs/" >&2
        exit 1
    fi
    echo "Regenerating: $latest"
    {{python}} scripts/generate.py --data "$latest" --keep-html

# Generate a specific tailored resume
generate path:
    {{python}} scripts/generate.py --data "{{path}}" --keep-html

# Fetch/update Google Fonts
fonts:
    {{python}} scripts/fetch_fonts.py
