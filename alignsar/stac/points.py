#!/usr/bin/env python3
import os
import os.path
import csv


def main():
    points = "mapX,mapY,pixelX,pixelY,enable\n"
    with open("gcps.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            x, y, lon, lat = row
            points += f"{lon},{lat},{x},-{y},1\n"

    with open("gcps.points", "w") as file:
        file.write(points)


if __name__ == "__main__":
    main()
