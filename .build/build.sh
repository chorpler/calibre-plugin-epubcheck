#!/usr/bin/env bash

# set -e

source ./setup_python.sh "${@}"

(
  ${CD} "${PLUGIN_DIR}"

  if [ -d "translations" ]; then
      ${CD} translations
      export PYTHONIOENCODING="UTF-8"
      for file in *.po; do
          FILE_TARGET="${file%.*}"
          ${PRINTF} "Compiling translation for: %s\n" "${FILE_TARGET}"
          CMD1="\"${CALIBRE_DEBUG}\" -c \"from calibre.translations.msgfmt import main; main()\" \"${FILE_TARGET}\""
          if [[ "${DEBUGMODE}" -eq 1 ]]; then
              ${PRINTF} "Running: '%s' ...\n" "${CMD1}"
          fi
          if [[ -n "${CALIBRE_DIRECTORY}" ]]; then
              "${CALIBRE_DEBUG}" -c "from calibre.translations.msgfmt import main; main()" "${FILE_TARGET}"
          else
              calibre-debug -c "from calibre.translations.msgfmt import main; main()" "${FILE_TARGET}"
          fi
      done
      ${CD} "${PLUGIN_DIR}"
  else
      ${ECHO} "No translations subfolder found"
  fi

  ${ECHO} "Copying common files for zip"
  ${CD} "${PLUGIN_DIR}"
  ${CP} "${COMMON_DIR}"/common_*.py . >/dev/null 2>&1

  python "${COMMON_DIR}/build.py"
  STATUS="${?}"
  if [[ "${STATUS}" -ne 0 ]]; then
      ${ECHO} "Build failed"
      exit 1
  fi

#   echo "Deleting common files after zip"
#   ${RM} common_*.py

  # Determine the zip file that just got created
  # shellcheck disable=SC2035
  PLUGIN_ZIP="$(${LS} -t *.zip | ${HEAD} -n 1)"
  PLUGIN_ZIP_PATH="$(${REALPATH} "${PLUGIN_ZIP}")"

  if [[ ! -s "${PLUGIN_ZIP_PATH}" ]]; then
    ${PRINTF} "ERROR: Failed to build plugin zip file at: %s\n" "${PLUGIN_ZIP_PATH}"
    exit 1
  fi

  ${PRINTF} "Installing plugin '%s' into calibre ...\n" "${PLUGIN_ZIP_PATH}"

  if [[ -n "${CALIBRE_DIRECTORY}" ]]; then
      "${CALIBRE_CUSTOMIZE}" -a "${PLUGIN_ZIP_PATH}"
  else
      calibre-customize -a "${PLUGIN_ZIP}"
  fi

  ${ECHO} "Build completed successfully"

  ${CD} "${SCRIPT_DIR}"
)

