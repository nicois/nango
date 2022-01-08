#!/bin/bash
set -euo pipefail
set -x

VERSION_STRING=$(git describe --always --tags --dirty)
YMD="$(date +%Y.%m.%d)"
SUFFIX=".8"


# Get the previous tag, if possible
[[ "$VERSION_STRING" =~ ^v[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+ ]] && PREVIOUS_TAG="$BASH_REMATCH"
# Set version tag if the current commit is tagged with vX.Y.Z
[[ "$VERSION_STRING" =~ ^v[[:digit:]]+\.[[:digit:]]+\.[[:digit:]]+$ ]] && VERSION_TAG="$VERSION_STRING"

PACKAGER_VENV=~/.venv.packager
if [[ ! -d "$PACKAGER_VENV" ]] ; then
    # FIXME: use requirements-build.txt
    python3 -m venv "${PACKAGER_VENV}"
    "${PACKAGER_VENV}/bin/pip" install -U pip build twine
fi

. "${PACKAGER_VENV}/bin/activate"

if [[ -f "pyproject.toml" ]] ; then
    [[ -d dist ]] && rm -rf dist
    echo "Building $(pwd)"
    if [[ -v VERSION_TAG ]] ; then
        VERSION_STRING="$VERSION_TAG" chronic python -m build
        if [[ -f ~/.pypirc ]] ; then
            echo "Uploading ${VERSION_TAG} to prod pypi"
            python3 -m twine upload --repository pypi dist/*
        fi
    elif [[ "$VERSION_STRING" != *-dirty ]] ; then
        VERSION_STRING="${YMD}${SUFFIX}" chronic python -m build
        if [[ -f ~/.pypirc ]] ; then
            echo "Uploading ${YMD} to test pypi"
            python3 -m twine upload --repository testpypi dist/*
        fi
    else
        VERSION_STRING="$YMD" chronic python -m build
        echo "Not uploading ${YMD} anywhere"
    fi
fi
