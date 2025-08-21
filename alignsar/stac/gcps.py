#!/usr/bin/env python3
import sys
import math
import warnings
import rasterio


def main():
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    lon_filename = sys.argv[1] if len(sys.argv) > 1 else "lon.tif"
    lat_filename = sys.argv[2] if len(sys.argv) > 2 else "lat.tif"
    num_x = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    num_y = int(sys.argv[4]) if len(sys.argv) > 4 else 10

    print("Reading longitude grid...")
    with rasterio.open(lon_filename) as ds:
        lon_grid = ds.read(1)

    print("Reading latitude grid...")
    with rasterio.open(lat_filename) as ds:
        lat_grid = ds.read(1)

    h, w = lat_grid.shape
    print("Grid size %d x %d" % (w, h))

    xs = list(range(0, w, math.floor(w / (num_x - 1))))
    if xs[-1] != w - 1:
        xs.append(w - 1)

    ys = list(range(0, h, math.floor(h / (num_y - 1))))
    if ys[-1] != h - 1:
        ys.append(h - 1)

    print("Point grid size %d x %d" % (len(xs), len(ys)))

    with open("gcps.csv", "w") as file:
        for y in ys:
            for x in xs:
                file.write("%0.1f,%0.1f,%f,%f\n" % (x + 0.5, y + 0.5, lon_grid[y][x], lat_grid[y][x]))


if __name__ == "__main__":
    main()
