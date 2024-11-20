#!/usr/bin/env bash

export CALIBRE_DIRECTORY="/Applications/calibre.app/Contents/MacOS"
CALIBRE_5_DIR="/Users/admin/code/calibre/calibre"

export CP="$(unalias -a; command -v gcp || command -v cp)"
export LS="$(unalias -a; command -v gls || command -v ls)"
export RM="$(unalias -a; command -v grm || command -v rm)"
export CUT="$(unalias -a; command -v gcut || command -v cut)"
export ECHO="$(unalias -a; command -v gecho || command -v echo)"
export HEAD="$(unalias -a; command -v ghead || command -v head)"
export PRINTF="$(unalias -a; command -v gprintf || command -v printf)"
export DIRNAME="$(unalias -a; command -v gdirname || command -v dirname)"
export BASENAME="$(unalias -a; command -v gbasename || command -v basename)"
export REALPATH="$(unalias -a; command -v grealpath || command -v realpath)"
export TPUT="tput -Txterm-256color"

export SCRIPT_PATH="$(${REALPATH} "${0}")"
export SCRIPT_FILE="$(${BASENAME} "${SCRIPT_PATH}")"
export SCRIPT_DIR="$(${DIRNAME} "${SCRIPT_PATH}")"
export PLUGIN_DIR="$(${DIRNAME} "${SCRIPT_DIR}")"
export BASE_DIR="$(${DIRNAME} "${PLUGIN_DIR}")"
export COMMON_DIR="${BASE_DIR}/common"

export DEBUGMODE="0"
export RD="$(${TPUT} setaf 1)"
export GN="$(${TPUT} setaf 2)"
export YL="$(${TPUT} setaf 3)"
export BL="$(${TPUT} setaf 4)"
export MG="$(${TPUT} setaf 5)"
export CY="$(${TPUT} setaf 6)"
export BD="$(${TPUT} bold)"
export NC="$(${TPUT} sgr0)"

ARGS="${BASH_SOURCE[@]}"
ARG1="${1}"
if [[ -n "${ARG1}" && "${ARG1,,}" =~ ^-?-d(ebug)?$ ]]; then
  DEBUGMODE="1"
fi

# /Users/admin/.asdf/installs/python/3.11.5

export PY3_HOME="$(asdf where python)"
export PY3_VERS="$(${BASENAME} "${PY3_HOME}")"
export PY3_MAJOR="$(${ECHO} "${PY3_VERS}" | ${CUT} -d '.' -f 1)"
export PY3_MINOR="$(${ECHO} "${PY3_VERS}" | ${CUT} -d '.' -f 2)"
export PY3_PATCH="$(${ECHO} "${PY3_VERS}" | ${CUT} -d '.' -f 3)"

# /Users/admin/dotasdf/installs/python/3.10.1/lib/python3.10/gettext.py
export PY3_LIB="${PY3_HOME}/lib"

export PY3_PKG_HOME="${PY3_LIB}/python${PY3_MAJOR}.${PY3_MINOR}"

export PYGETTEXT_FILE="gettext.py"

if [[ -n "${PYGETTEXT_DIRECTORY}" ]]; then
  export PYGETTEXT="${PYGETTEXT_DIRECTORY}/${PYGETTEXT_FILE}"
else
  export PYGETTEXT="${PY3_PKG_HOME}/${PYGETTEXT_FILE}"
  export PYGETTEXT_DIRECTORY="${PY3_PKG_HOME}"
fi

#######################################################################
#                                                                     #
#                        CALIBRE VARIABLES                            #
#                                                                     #
#######################################################################

# ENVIRONMENT VARIABLE              | DESCRIPTION                                                                                                                                                                                                                                                                                                                                                                                         #
# --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# CALIBRE_CONFIG_DIRECTORY          | sets the folder where configuration files are stored/read.                                                                                                                                                                                                                                                                                                                                          #
# CALIBRE_TEMP_DIR                  | sets the temporary folder used by calibre                                                                                                                                                                                                                                                                                                                                                           #
# CALIBRE_CACHE_DIRECTORY           | sets the folder calibre uses to cache persistent data between sessions                                                                                                                                                                                                                                                                                                                              #
# CALIBRE_OVERRIDE_DATABASE_PATH    | allows you to specify the full path to metadata.db. Using this variable you can have metadata.db be in a location other than the library folder. Useful if your library folder is on a networked drive that does not support file locking.                                                                                                                                                          #
# CALIBRE_DEVELOP_FROM              | used to run from a calibre development environment. See Setting up a calibre development environment.                                                                                                                                                                                                                                                                                               #
# CALIBRE_OVERRIDE_LANG             | used to force the language used by the interface (ISO 639 language code)                                                                                                                                                                                                                                                                                                                            #
# CALIBRE_TEST_TRANSLATION          | used to test a translation .po file (should be the path to the .po file)                                                                                                                                                                                                                                                                                                                            #
# CALIBRE_NO_NATIVE_FILEDIALOGS     | causes calibre to not use native file dialogs for selecting files/folders.                                                                                                                                                                                                                                                                                                                          #
# CALIBRE_NO_NATIVE_MENUBAR         | causes calibre to not create a native (global) menu on Ubuntu Unity and similar Linux desktop environments. The menu is instead placed inside the window, as is traditional.                                                                                                                                                                                                                        #
# CALIBRE_USE_SYSTEM_THEME          | by default, on Linux, calibre uses its own builtin Qt style. This is to avoid crashes and hangs caused by incompatibilities between the version of Qt calibre is built against and the system Qt. The downside is that calibre may not follow the system look and feel. If you set this environment variable on Linux, it will cause calibre to use the system theme – beware of crashes and hangs. #
# CALIBRE_SHOW_DEPRECATION_WARNINGS | causes calibre to print deprecation warnings to stdout. Useful for calibre developers.                                                                                                                                                                                                                                                                                                              #
# CALIBRE_NO_DEFAULT_PROGRAMS       | prevent calibre from automatically registering the filetypes it is capable of handling with Windows.                                                                                                                                                                                                                                                                                                #
# QT_QPA_PLATFORM                   | On Linux set this to wayland to force calibre to use Wayland and xcb to force use of X11.                                                                                                                                                                                                                                                                                                           #
# SYSFS_PATH                        | Use if sysfs is mounted somewhere other than /sys                                                                                                                                                                                                                                                                                                                                                   #
# http_proxy, https_proxy           | used on Linux to specify an HTTP(S) proxy                                                                                                                                                                                                                                                                                                                                                           #

# | Environment Variable     | Purpose                                                                                                                                                                                                                                                        |
# | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
# | CALIBRE_CONFIG_DIRECTORY | If using calibre portable, set this to the location of the Calibre Settings subfolder. Otherwise calibre-customize in build.cmd will insert into your main calibre.                                                                                            |
# | CALIBRE_DIRECTORY        | Custom variable I added support for, used by build.cmd. Set to folder location of your calibre-debug.exe. Only necessary if calibre is not in your path.                                                                                                       |
# | PYGETTEXT_DIRECTORY      | Custom variable I added support for, used by generate-pot.cmd. Set to folder location of your Python pygettext.py file. Default location assumed to be C:\Python310\Tools\i18n. Could be useful if you have a different version of Python or install location. |
# | CALIBRE_GITHUB_TOKEN     | Custom variable I added support for, used by release.cmd. Authorised releasers will set it to their API token key.                                                                                                                                             |

export CALIBRE_HOME="${CALIBRE_5_DIR}"
export CALIBRE_DEVELOP_FROM="${CALIBRE_HOME}/src"

export CALIBRE_CUSTOMIZE="${CALIBRE_DIRECTORY}/calibre-customize"
export CALIBRE_DEBUG="${CALIBRE_DIRECTORY}/calibre-debug"

if [[ ! -x "${CALIBRE_CUSTOMIZE}" ]]; then
  ${PRINTF} "ERROR: Could not find calibre-customize at: '%s'\n" "${CALIBRE_CUSTOMIZE}"
  exit 1
fi

if [[ ! -x "${CALIBRE_DEBUG}" ]]; then
  ${PRINTF} "ERROR: Could not find calibre-debug at: '%s'\n" "${CALIBRE_DEBUG}"
  exit 1
fi


# export PYGETTEXT_DIRECTORY=""
# export CALIBRE_GITHUB_TOKEN=""

if [[ "${DEBUGMODE}" == "1" ]]; then
  ${PRINTF} "%s" "${CY}"
  ${PRINTF} "\n"
  ${PRINTF} "================================================================================================================\n"
  ${PRINTF} "= BEGIN DEBUG INFO                                                                                             =\n"
  ${PRINTF} "================================================================================================================\n"
  ${PRINTF} "SCRIPT_PATH          = %s\n" "${SCRIPT_PATH}"
  ${PRINTF} "SCRIPT_FILE          = %s\n" "${SCRIPT_FILE}"
  ${PRINTF} "SCRIPT_DIR           = %s\n" "${SCRIPT_DIR}"
  ${PRINTF} "PLUGIN_DIR           = %s\n" "${PLUGIN_DIR}"
  ${PRINTF} "BASE_DIR             = %s\n" "${BASE_DIR}"
  ${PRINTF} "COMMON_DIR           = %s\n" "${COMMON_DIR}"
  ${PRINTF} "PY3_HOME             = %s\n" "${PY3_HOME}"
  ${PRINTF} "PY3_VERS             = %s\n" "${PY3_VERS}"
  ${PRINTF} "PY3_MAJOR            = %s\n" "${PY3_MAJOR}"
  ${PRINTF} "PY3_MINOR            = %s\n" "${PY3_MINOR}"
  ${PRINTF} "PY3_PATCH            = %s\n" "${PY3_PATCH}"
  ${PRINTF} "PY3_LIB              = %s\n" "${PY3_LIB}"
  ${PRINTF} "PY3_PKG_HOME         = %s\n" "${PY3_PKG_HOME}"
  ${PRINTF} "PYGETTEXT_DIRECTORY  = %s\n" "${PYGETTEXT_DIRECTORY}"
  ${PRINTF} "PYGETTEXT            = %s\n" "${PYGETTEXT}"
  ${PRINTF} "CALIBRE_DIRECTORY    = %s\n" "${CALIBRE_DIRECTORY}"
  ${PRINTF} "CALIBRE_HOME         = %s\n" "${CALIBRE_HOME}"
  ${PRINTF} "CALIBRE_DEVELOP_FROM = %s\n" "${CALIBRE_DEVELOP_FROM}"
  ${PRINTF} "CALIBRE_CUSTOMIZE    = %s\n" "${CALIBRE_CUSTOMIZE}"
  ${PRINTF} "CALIBRE_DEBUG        = %s\n" "${CALIBRE_DEBUG}"
  ${PRINTF} "================================================================================================================\n"
  ${PRINTF} "=  END  DEBUG INFO                                                                                             =\n"
  ${PRINTF} "================================================================================================================\n"
  ${PRINTF} "%s" "${NC}"
  ${PRINTF} "\n"
fi

if [[ ! -s "${PYGETTEXT}" ]]; then
  ${PRINTF} "ERROR: Could not find python gettext file %s at: %s\n" "${PYGETTEXT_FILE}" "${PYGETTEXT}"
  exit 1
fi

# cd ..

# PYGETTEXT=C:\Python310\Tools\i18n\pygettext.py
# if defined PYGETTEXT_DIRECTORY (
#     set PYGETTEXT=%PYGETTEXT_DIRECTORY%\pygettext.py
# )

# echo "Regenerating translations .pot file"
# python ${PYGETTEXT} -d generate-cover -p translations action.py config.py dialogs.py ../common/common_*.py

# unset PYGETTEXT


# /usr/local/Cellar/python@3.11/3.11.3/Frameworks/Python.framework/Versions/3.11/share/doc/python3.11/examples/Tools/i18n/pygettext.py