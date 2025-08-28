#!/usr/bin/env python3
"""
wgs2radar: Radar-code vector reference data with respect to a SAR image
(Doris-based workflow)

Dependencies:
- doris (available in PATH)
- GDAL
- shapely, geopandas
- alignsar (alignsar_utils + rdrcode helpers)

Usage:
    python rdrCode_main.py --inputFile input_card.txt

Requirements:
    - Doris processing completed up to the coarse-orbits stage
    - doris and gdal must be callable from the shell
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

from alignsar.alignsar_utils import read_param_file
from alignsar.rdrcode.rdrCode_prep_ref_data import (
    prepare_poly_ref_data,
    get_doris_process_bounds,
    alter_input_file,
    execute_rdrcode,
)

# Minimum required keys expected in the parameter card
REQUIRED_KEYS = {
    "dorisProcessDir",
    "refDataFile",
}

def unquote(s: str) -> str:
    """
    Remove surrounding quotes and whitespace from a string.
    Commonly needed because Doris/AlignSAR parameter cards
    often store values like:  '/path/to/dir'
    """
    if not isinstance(s, str):
        return s
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == "'") or (s[0] == s[-1] == '"')):
        return s[1:-1].strip()
    return s

def require_params(params: Dict[str, Any], keys: Iterable[str]) -> None:
    """Ensure all required keys are present in the parameter dictionary."""
    missing = [k for k in keys if k not in params]
    if missing:
        raise KeyError(f"Missing required parameter(s) in input card: {', '.join(missing)}")

def check_path_exists(p: str | Path, what: str) -> Path:
    """Verify a path exists and return it as a Path object."""
    p = Path(unquote(str(p)))
    if not p.exists():
        raise FileNotFoundError(f"{what} not found: {p}")
    return p

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Radar-code vector reference files with respect to a SAR image.\n"
            "Requires Doris processing up to coarse-orbits stage and doris/gdal available in PATH."
        )
    )
    parser.add_argument(
        "--inputFile",
        required=True,
        help="Full path to the input parameter card"
    )
    args = parser.parse_args()

    try:
        # Validate the parameter card file exists
        card_path = check_path_exists(args.inputFile, "Input parameter card")

        # Read parameters from the card
        params = read_param_file(str(card_path))
        require_params(params, REQUIRED_KEYS)

        # Unquote paths if they are wrapped in quotes
        params["dorisProcessDir"] = unquote(params["dorisProcessDir"])
        params["refDataFile"] = unquote(params["refDataFile"])

        # Step 1: Determine Doris processing bounds (xmin, ymin, xmax, ymax)
        xmin, ymin, xmax, ymax = get_doris_process_bounds(
            params["dorisProcessDir"], params["refDataFile"]
        )

        # Step 2: Prepare polygon reference data (clip/reproject to extent)
        prepare_poly_ref_data(params, extent=[xmin, ymin, xmax, ymax])

        # Step 3: Create or update rdrCode input card
        rdr_input_card = "input_radarcode"
        rdrCode_input_fnames = alter_input_file(rdr_input_card, params)

        # Step 4: Execute radar-coding process
        execute_rdrcode(params, rdrCode_input_fnames)

        print("Done.")
        return 0

    except (FileNotFoundError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
    except Exception as e:
        # Catch any unexpected error and show its type
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
