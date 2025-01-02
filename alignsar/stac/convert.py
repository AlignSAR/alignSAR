import sys
import re
import netCDF4


def main():
    formats = {
        "unit8": "Byte",
        "float32": "Float32",
        "float64": "Float32",
    }

    filename = sys.argv[1] if len(sys.argv) > 1 else None
    if not filename:
        print("Please enter a filename.")
        sys.exit(1)

    try:
        ds = netCDF4.Dataset(filename, "r")
    except:
        print("Invalid NetCDF file.")
        sys.exit(1)

    for var in ds.variables:
        name = re.sub(r"\([^)]+\)", "", var).strip().replace(" ", "-").lower()

        format = formats.get(ds.variables[var].Format)
        if not format:
            print(f"Invalid data format {ds.variables[var].Format}.")
            sys.exit(1)

        cmd = 'gdal_translate -ot {} "NETCDF:{}:{}" {}.tif'.format(
            format,
            filename,
            var,
            name
        )
        print(cmd)

    ds.close()


if __name__ == "__main__":
    main()
