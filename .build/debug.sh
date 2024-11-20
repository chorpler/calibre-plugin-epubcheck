#!/usr/local/bin/bash

set -x 

source "setup_python.sh"

"${SCRIPT_DIR}/build.sh"

export CALIBRE_DEVELOP_FROM=
export CALIBRE_OVERRIDE_LANG=

echo "Starting calibre in debug mode"

set +x 

calibre-debug -g
