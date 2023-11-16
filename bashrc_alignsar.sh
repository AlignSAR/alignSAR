## Path
export ALIGNSAR_PATH="$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)"
export PATH="$ALIGNSAR_PATH/bin:$PATH"
export PYTHONPATH="$ALIGNSAR_PATH/rdrcode:$ALIGNSAR_PATH/python:$PYTHONPATH"
export SNAPGRAPHS="$ALIGNSAR_PATH/snap_graphs"
