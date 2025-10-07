#!/bin/bash
set -euo pipefail

# Set up directory structure
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Activate the virtual environment (created at build time)
source "${VENV_DIR}/bin/activate"

# Point COMPSs to this project and run with the virtualenv interpreter.
export COMPSS_HOME="${SCRIPT_DIR}"
PYCOMPSS_HOME="${COMPSS_HOME}/Bindings/python/3"

# Set the python path
export PYTHONPATH="${SCRIPT_DIR}"
export PYTHONPATH=${PYCOMPSS_HOME}:${PYTHONPATH}

# Set LD lib path
export LD_LIBRARY_PATH="${JAVA_HOME}/lib/server:${SCRIPT_DIR}/Bindings/bindings-common/lib:${LD_LIBRARY_PATH:-}"

# Change to the app directory to avoid appdir being /
cd "${SCRIPT_DIR}"

echo "Init complete. Executing main command..."
exec "$@"