#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stac.py
One-click NetCDF -> GeoTIFF -> GCP -> COG pipeline (fixed behavior)

Behavior:
  - Always run gdalwarp to create COG (EPSG:4326)
  - Always overwrite outputs (re-run regardless of existing files)
  - Always generate gcps.points
  - Output is always in the current working directory

Requirements:
  - GDAL command-line tools in PATH (gdal_translate, gdalwarp)
  - Python: rasterio, netCDF4, numpy
"""

import argparse
import os
import os.path as op
import re
import sys
import csv
import math
import subprocess
import warnings

import numpy as np
import rasterio
import netCDF4


def run_cmd(cmd, dryrun=False):
    """Run a shell command and print it."""
    print(cmd)
    if dryrun:
        return 0
    try:
        subprocess.check_call(cmd, shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


def clean_var_name(var_name: str) -> str:
    """Clean variable name: remove parentheses, replace spaces, lowercase."""
    name = re.sub(r"\([^)]+\)", "", var_name).strip()
    name = name.replace(" ", "-").lower()
    return name


def guess_gdal_type(np_dtype: np.dtype, allow_downcast: bool = True) -> str:
    """Map numpy dtype to GDAL type."""
    if np_dtype == np.uint8:
        return "Byte"
    if np_dtype in (np.float32,):
        return "Float32"
    if np_dtype in (np.float64,):
        return "Float32" if allow_downcast else "Float64"
    if np.issubdtype(np_dtype, np.integer):
        return "Int16"
    return "Float32"


def is_lon_name(name: str) -> bool:
    name = name.lower()
    return name in ["lon", "longitude", "lam", "x"]


def is_lat_name(name: str) -> bool:
    name = name.lower()
    return name in ["lat", "latitude", "phi", "y"]


def export_netcdf_variables_to_tif(nc_path, lon_name_pref, lat_name_pref, allow_downcast=True, dryrun=False):
    """Export NetCDF variables to GeoTIFF using gdal_translate."""
    outdir = os.getcwd()
    ds = netCDF4.Dataset(nc_path, "r")
    vars_dict = ds.variables

    lon_var = None
    lat_var = None

    for v in vars_dict:
        if v in lon_name_pref:
            lon_var = v
        if v in lat_name_pref:
            lat_var = v

    if lon_var is None or lat_var is None:
        for v in vars_dict:
            if lon_var is None and is_lon_name(v):
                lon_var = v
            if lat_var is None and is_lat_name(v):
                lat_var = v
            if lon_var and lat_var:
                break

    all_tifs = []
    lon_tif = None
    lat_tif = None

    for var in vars_dict:
        v = vars_dict[var]
        if not hasattr(v, "dtype"):
            continue
        if len(v.dimensions) != 2:
            continue

        gdal_type = guess_gdal_type(v.dtype, allow_downcast)
        name_clean = clean_var_name(var)

        if var == lon_var:
            out_name = "lon.tif"
        elif var == lat_var:
            out_name = "lat.tif"
        else:
            out_name = f"{name_clean}.tif"

        out_path = op.join(outdir, out_name)

        cmd = f'gdal_translate -ot {gdal_type} "NETCDF:{nc_path}:{var}" "{out_path}"'
        rc = run_cmd(cmd, dryrun=dryrun)
        if rc != 0:
            print(f"[warn] Failed to export variable: {var}")
            continue

        if var == lon_var:
            lon_tif = out_path
        if var == lat_var:
            lat_tif = out_path
        all_tifs.append(out_path)

    ds.close()
    return all_tifs, lon_tif, lat_tif


def make_gcps_csv(lon_tif, lat_tif, num_x, num_y, out_csv):
    """Create GCP CSV from lon/lat rasters."""
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    print("Reading longitude grid...")
    with rasterio.open(lon_tif) as ds:
        lon_grid = ds.read(1)

    print("Reading latitude grid...")
    with rasterio.open(lat_tif) as ds:
        lat_grid = ds.read(1)

    h, w = lat_grid.shape
    print(f"Grid size {w} x {h}")

    xs = list(range(0, w, max(1, math.floor(w / max(1, num_x - 1)))))
    if xs[-1] != w - 1:
        xs.append(w - 1)

    ys = list(range(0, h, max(1, math.floor(h / max(1, num_y - 1)))))
    if ys[-1] != h - 1:
        ys.append(h - 1)

    print(f"Point grid size {len(xs)} x {len(ys)}")

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        for y in ys:
            for x in xs:
                writer.writerow([f"{x + 0.5:.1f}", f"{y + 0.5:.1f}", f"{lon_grid[y][x]:.10f}", f"{lat_grid[y][x]:.10f}"])


def apply_gcps_and_warp_to_cog(tifs, gcps_csv, resample="near", dryrun=False):
    """Apply GCPs and warp all rasters to COG."""
    gcp_opts = ""
    with open(gcps_csv, "r") as f:
        reader = csv.reader(f)
        for x, y, lon, lat in reader:
            gcp_opts += f" -gcp {x} {y} {lon} {lat}"

    for tif in tifs:
        base = op.basename(tif)
        name, _ = op.splitext(base)
        if name.lower() in ["lon", "lat", "latitude", "longitude"]:
            continue
        if name.endswith("-cog"):
            continue

        temp_path = f"{name}_temp-georef.tif"
        cog_path = f"{name}-cog.tif"

        cmd1 = f'gdal_translate -strict -of GTiff -a_srs EPSG:4326 -stats {gcp_opts} "{tif}" "{temp_path}"'
        rc = run_cmd(cmd1, dryrun=dryrun)
        if rc != 0:
            print(f"[warn] gdal_translate failed for {tif}")
            continue

        cmd2 = f'gdalwarp -r {resample} -of COG -t_srs EPSG:4326 "{temp_path}" "{cog_path}"'
        rc = run_cmd(cmd2, dryrun=dryrun)
        if rc != 0:
            print(f"[warn] gdalwarp failed for {tif}")
        else:
            os.remove(temp_path)


def write_points_file(gcps_csv, out_points):
    """Create gcps.points file from gcps.csv."""
    lines = ["mapX,mapY,pixelX,pixelY,enable\n"]
    with open(gcps_csv, "r") as f:
        reader = csv.reader(f)
        for x, y, lon, lat in reader:
            lines.append(f"{lon},{lat},{x},-{y},1\n")
    with open(out_points, "w") as f:
        f.writelines(lines)


def parse_args():
    p = argparse.ArgumentParser(description="NetCDF -> GeoTIFF -> GCP -> COG pipeline")
    p.add_argument("--inputfile", required=True, help="Input NetCDF file")
    p.add_argument("--lon-name", default="Lon", help="Preferred longitude variable name")
    p.add_argument("--lat-name", default="Lat", help="Preferred latitude variable name")
    p.add_argument("--num-x", type=int, default=10, help="Number of GCP columns")
    p.add_argument("--num-y", type=int, default=10, help="Number of GCP rows")
    p.add_argument("--resample", default="near", help="gdalwarp resampling method")
    p.add_argument("--dryrun", action="store_true", help="Print commands without running them")
    return p.parse_args()


def main():
    args = parse_args()

    nc_path = op.abspath(args.inputfile)
    outdir = os.getcwd()

    lon_name_pref = [args.lon_name, args.lon_name.lower(), "lon", "longitude", "lam"]
    lat_name_pref = [args.lat_name, args.lat_name.lower(), "lat", "latitude", "phi"]

    all_tifs, lon_tif, lat_tif = export_netcdf_variables_to_tif(
        nc_path=nc_path,
        lon_name_pref=lon_name_pref,
        lat_name_pref=lat_name_pref,
        allow_downcast=True,
        dryrun=args.dryrun
    )

    if lon_tif is None or lat_tif is None:
        print("[error] Could not locate lon/lat rasters in NetCDF.")
        sys.exit(2)

    gcps_csv = op.join(outdir, "gcps.csv")
    make_gcps_csv(lon_tif, lat_tif, args.num_x, args.num_y, gcps_csv)

    apply_gcps_and_warp_to_cog(
        tifs=all_tifs,
        gcps_csv=gcps_csv,
        resample=args.resample,
        dryrun=args.dryrun
    )

    points_path = op.join(outdir, "gcps.points")
    write_points_file(gcps_csv, points_path)

    print("\n[done] STAC pipeline completed.")


if __name__ == "__main__":
    main()
