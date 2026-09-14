python := "python"

# Regenerate the most recently modified tailored.yaml
regen:
    #!/usr/bin/env bash
    latest=$(find data/jobs -name 'tailored.yaml' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    if [ -z "$latest" ]; then
        echo "No tailored.yaml found in data/jobs/" >&2
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

# First-time setup: unpack the example and install git hooks
setup:
    {{python}} scripts/setup.py

# (Re)generate example PDFs
examples:
    {{python}} scripts/generate_examples.py

# Pack the example files into the tracked archive (run after `just examples` or editing the example)
pack-examples:
    tar czf examples/example-materials.tar.gz \
        data/comprehensive_bio.yaml \
        data/jobs/example/senior-cloud-platform-engineer/.generate.yaml \
        "data/jobs/example/senior-cloud-platform-engineer/Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf" \
        data/jobs/example/senior-cloud-platform-engineer/resume.pdf \
        data/jobs/example/senior-cloud-platform-engineer/tailored.yaml \
        "hand_crafted_resumes/Robin Codewright - Cloud Engineer (example).pdf" \
        "hand_crafted_resumes/Robin Codewright - Full Stack Developer (example).pdf"
