#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os
from datetime import datetime
import argparse


def get_xml_path(sar_folder_path, folder_num, xml_num):
    """
    Get the path of a specific XML file inside a SAR SAFE folder.

    Parameters:
        sar_folder_path (str): Path to the SAR data directory containing SAFE folders.
        folder_num (int): Index of the target SAFE folder.
        xml_num (int): Index of the XML file within the 'annotation' folder.

    Returns:
        str: Full path to the selected XML file.
    """
    folders = [f for f in os.listdir(sar_folder_path)
               if os.path.isdir(os.path.join(sar_folder_path, f))]
    xml_dir = os.path.join(sar_folder_path, folders[folder_num], 'annotation')
    files = [f for f in os.listdir(xml_dir)
             if os.path.isfile(os.path.join(xml_dir, f))]
    return os.path.join(xml_dir, files[xml_num])


def get_global_attribute(sar_folder_path, folder_num, xml_num,
                         lon_max, lon_min, lat_max, lat_min,
                         master_date, CRP_LIST):
    """
    Extract global SAR attributes from the selected XML file.

    Parameters:
        sar_folder_path (str): Path to the SAR data directory containing SAFE folders.
        folder_num (int): Index of the target SAFE folder.
        xml_num (int): Index of the XML file within the 'annotation' folder.
        lon_max (float): Maximum longitude of the AOI.
        lon_min (float): Minimum longitude of the AOI.
        lat_max (float): Maximum latitude of the AOI.
        lat_min (float): Minimum latitude of the AOI.
        master_date (str): Master acquisition date (YYYY-MM-DD).
        CRP_LIST (str): Crop information (azimuth, range) for SLC cropping.

    Returns:
        dict: Dictionary containing global SAR metadata attributes.
    """
    xml_path = get_xml_path(sar_folder_path, folder_num, xml_num)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    sar_date_time = root.find(".//startTime").text[:10]
    sar_UTC_time = root.find(".//startTime").text[11:16]
    sar_instrument_mode = root.find(".//mode").text
    sar_pixel_spacing_range = root.find(".//rangePixelSpacing").text
    sar_pixel_spacing_azimuth = root.find(".//azimuthPixelSpacing").text
    sar_absolute_orbit = root.find(".//absoluteOrbitNumber").text
    sar_relative_orbit = (int(sar_absolute_orbit) - 73) % 175 + 1
    sar_view_azimuth = root.find(".//pass").text
    sar_view_incidence_angle = root.find(".//incidenceAngleMidSwath").text

    t = datetime.now().strftime('%Y-%m-%d')

    return {
        'processing_level': 'L1',
        'date_created': t,
        'creator_name': 'Xu Zhang',
        'creator_email': 'x.zhang-7@utwente.nl',
        'creator_url': 'https://research.utwente.nl/en/persons/xu-zhang',
        'institution': 'UT',
        'project': 'ESA Open SAR Library',
        'publisher_name': 'AlignSAR',
        'publisher_email': 'alignsar.project@gmail.com',
        'publisher_url': 'alignsar.nl',
        'geospatial_lat_min': lat_min,
        'geospatial_lat_max': lat_max,
        'geospatial_lon_min': lon_min,
        'geospatial_lon_max': lon_max,
        'sar_date_time': sar_date_time,
        'sar_master_date_time': master_date,
        'sar_UTC_time': sar_UTC_time,
        'sar_instrument_mode': sar_instrument_mode,
        'sar_looks_range': "1",
        'sar_looks_azimuth': "1",
        'sar_pixel_spacing_range': sar_pixel_spacing_range,
        'sar_pixel_spacing_azimuth': sar_pixel_spacing_azimuth,
        'sar_processing_software': 'doris',
        'sar_absolute_orbit': sar_absolute_orbit,
        'sar_relative_orbit': sar_relative_orbit,
        'sar_view_azimuth': sar_view_azimuth,
        'sar_view_incidence_angle': sar_view_incidence_angle,
        'sar_SLC_crop[azimuth,range]': CRP_LIST
    }


def main():
    """
    Command-line interface for extracting SAR metadata from XML files.
    """
    parser = argparse.ArgumentParser(description="Extract SAR global attributes from Sentinel-1 SAFE XML files.")
    parser.add_argument("--sar_folder", type=str, required=True, help="Path to the folder containing SAFE files")
    parser.add_argument("--folder_num", type=int, default=0, help="Index of SAFE folder to read")
    parser.add_argument("--xml_num", type=int, default=0, help="Index of XML file in annotation folder")
    parser.add_argument("--lon_max", type=float, required=True, help="Maximum longitude of AOI")
    parser.add_argument("--lon_min", type=float, required=True, help="Minimum longitude of AOI")
    parser.add_argument("--lat_max", type=float, required=True, help="Maximum latitude of AOI")
    parser.add_argument("--lat_min", type=float, required=True, help="Minimum latitude of AOI")
    parser.add_argument("--master_date", type=str, required=True, help="Master acquisition date (YYYY-MM-DD)")
    parser.add_argument("--crp_list", type=str, required=True, help="Crop information for SLC (azimuth, range)")

    args = parser.parse_args()

    attrs = get_global_attribute(
        args.sar_folder,
        args.folder_num,
        args.xml_num,
        args.lon_max,
        args.lon_min,
        args.lat_max,
        args.lat_min,
        args.master_date,
        args.crp_list
    )

    for key, value in attrs.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
