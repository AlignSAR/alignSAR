## Path
export ALIGNSAR_PATH="$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)"
export PATH="$ALIGNSAR_PATH/bin:$PATH"
export PYTHONPATH="$ALIGNSAR_PATH:$ALIGNSAR_PATH/rdrcode:$PYTHONPATH"
export SNAPGRAPHS="$ALIGNSAR_PATH/snap_graphs"
