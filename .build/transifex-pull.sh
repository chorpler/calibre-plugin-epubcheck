#!/usr/local/bin/bash

set -e

source "setup_python.sh"

# @pushd
# @cd ..
(
  cd "${PLUGIN_DIR}"
  tx pull -f -a
  cd "${SCRIPT_DIR}"
)

set +e
