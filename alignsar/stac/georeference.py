import os
import os.path
import csv


def main():
    skips = [
        "lat",
        "latitude",
        "lon",
        "longitude",
    ]

    gcps = ""
    with open("gcps.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            x, y, lon, lat = row
            gcps += f" -gcp {x} {y} {lon} {lat}"

    for filename in os.listdir("."):
        name, ext = os.path.splitext(filename)
        if ext != ".tif":
            continue
        if name.endswith("-cog"):
            continue
        if name in skips:
            continue

        print(f"gdal_translate -strict -of GTiff -a_srs EPSG:4326 -stats {gcps} {filename} temp.tif")
        print(f"gdalwarp -r near -of COG -t_srs EPSG:4326 temp.tif {name}-cog.tif")
        print(f"del temp.tif")


if __name__ == "__main__":
    main()
