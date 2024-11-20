#!/usr/local/bin/bash

set -e

source "setup_python.sh"

"${SCRIPT_DIR}/build.sh"

# cd ..

python "${PLUGIN_DIR}/common/release.py" "${CALIBRE_GITHUB_TOKEN}"

# cd .build
set +e
