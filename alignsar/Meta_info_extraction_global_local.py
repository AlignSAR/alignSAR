import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta

# The functions in this file will be called in 'signature_extraction.py' file for feature extraction. 
# Corresponding path setting is mentioned in 'signature_extraction.py'. 

def get_xml_path(sar_folder_path, folder_num, xml_num):
    items = os.listdir(sar_folder_path)
    # create 'folders' list to contain all the sar image folders, e.g., folders=[S1A_IW_SLC__1SDV_20220109T171712_20220109T171740_041387_04EBB7_25EB.SAFE, ...]
    folders = [item for item in items if os.path.isdir(os.path.join(sar_folder_path,item))]
    # choose one sar image folder and come into it, attach xml folder 'annotation' to it
    xml_path = sar_folder_path + folders[folder_num] + '/annotation'
    items = os.listdir(xml_path)
    # create 'files' list to contain all the xml files, e.g., files=[s1a-iw1-slc-vh-20220109t171712-20220109t171738-041387-04ebb7-001.xml, ...]
    files = [item for item in items if os.path.isfile(os.path.join(xml_path,item))]
    # return one of the xml file path, depend on 'xml_num'
    return sar_folder_path + folders[folder_num] + '/annotation/' + files[xml_num]


def get_global_attribute(sar_folder_path, folder_num, xml_num,lon_max,lon_min,lat_max,lat_min,master_date,CRP_LIST):
    print(sar_folder_path, folder_num, xml_num,lonmax,lonmin,lat.max,lat.min,master_date,CRP_LIST)
    xml_path = get_xml_path(sar_folder_path,folder_num,xml_num)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    swath = root.find(".//swath").text

    sar_date_time = root.find(".//startTime").text[:10] # end to date
    sar_master_date_time = "20220214"
    sar_UTC_time = root.find(".//startTime").text[11:16]
    sar_instrument_mode = root.find(".//mode").text
    sar_looks_range = "1"
    sar_looks_azimuth = "1"
    sar_pixel_spacing_range = root.find(".//rangePixelSpacing").text
    sar_pixel_spacing_azimuth = root.find(".//azimuthPixelSpacing").text
    sar_processing_software = "doris"
    sar_absolute_orbit = root.find(".//absoluteOrbitNumber").text
    sar_relative_orbit = (int(sar_absolute_orbit)-73) % 175 +1
    sar_view_azimuth = root.find(".//pass").text
    sar_view_incidence_angle = root.find(".//incidenceAngleMidSwath").text
    sar_SLC_crop = CRP_LIST # read from input file
    now = datetime.now()
    t = now.strftime('%Y-%m-%d')

    Global_attr = {'processing_level':'L1', 'date_created': t, 'creator_name': 'Xu Zhang', 'creator_email': 'x.zhang-7@utwente.nl', \
                'creator_url': 'https://research.utwente.nl/en/persons/xu-zhang', 'institution': 'UT', 'project': 'ESA Open SAR Library', 'publisher_name': 'AlignSAR', \
                'publisher_email': 'alignsar.project@gmail.com', 'publisher_url': 'alignsar.nl', 'geospatial_lat_min': '53.108846741824934', \
                'geospatial_lat_max': '53.45763298862386', 'geospatial_lon_min': '5.376860616873864', 'geospatial_lon_max': '6.8439575842848654', \
               'sar_date_time':sar_date_time, 'sar_master_date_time':sar_master_date_time, 'sar_UTC_time':sar_UTC_time, 'sar_instrument_mode':sar_instrument_mode, \
                'sar_looks_range':sar_looks_range, 'sar_looks_azimuth':sar_looks_azimuth, 'sar_pixel_spacing_range':sar_pixel_spacing_range, \
                'sar_pixel_spacing_azimuth':sar_pixel_spacing_azimuth, 'sar_processing_software':sar_processing_software, \
                'sar_absolute_orbit':sar_absolute_orbit,'sar_relative_orbit':sar_relative_orbit, 'sar_view_azimuth':sar_view_azimuth, 'sar_view_incidence_angle':sar_view_incidence_angle, \
                'sar_SLC_crop[azimuth,range]':sar_SLC_crop}
    return Global_attr


# get the first xml file in first sar image folder, e.g., S1A_IW_SLC__1SDV_20220109T171712_20220109T171740_041387_04EBB7_25EB.SAFE/annotation/s1a-iw1-slc-vh-20220109t171712-20220109t171738-041387-04ebb7-001.xml
# print(get_global_attribute(sar_folder_path,2,0))



VV_amplitude_attr={
    'Units': 'voltage [linear]',\
    'Format': 'float32',\
    'Description': 'the absolute value of every complex number in VV channel'
}



VH_amplitude_attr={
    'Units': 'voltage [linear]',\
    'Format': 'float32',\
    'Description': 'the absolute value of every complex number in VH channel'
}



VV_interferometric_phase_attr={
    'Units': 'radians',\
    'Format': 'float32',\
    'Range': 'between -pi and +pi',\
    'Description': 'phase difference between master and slave acquisition'
}


VV_coherence_attr={
    'Units': 'unitless',\
    'Format': 'float32',\
    'Range': 'between 0 and 1',\
    'Description': 'the correlation between master and slave acquisition'
}



Intensity_summation_attr={
    'Units': 'voltage [linear]',\
    'Format': 'float32',\
    'Description': 'the summation of the intensity in VV and VH channel'
}



Intensity_difference_attr={
    'Units': 'voltage [linear]',\
    'Format': 'float32',\
    'Description': 'the intensity difference between VV and VH channel'
}


Intensity_ratio_attr={
    'Units': 'voltage [linear]',\
    'Format': 'float32',\
    'Description': 'the intensity ratio between VV and VH channel'
}


Cross_pol_correlation_coefficient_attr={
    'Units': 'unitless',\
    'Format': 'float32',\
    'Description': 'it is derived from the polarimetric covariance matrix',\
    'Reference': 'Lee, J.S.; Pottier, E. Polarimetric Radar Imaging: From Basics to Applications; CRC Press: Boca Raton, FL, USA, 2017'
}



Cross_pol_cross_product_attr={
    'Units': '',\
    'Format': 'float32',\
    'Description': 'it is derived from the polarimetric covariance matrix',\
    'Reference': 'Lee, J.S.; Pottier, E. Polarimetric Radar Imaging: From Basics to Applications; CRC Press: Boca Raton, FL, USA, 2017'
}




Entropy_attr={
    'Units': '',\
    'Format': 'float32',\
    'Description': 'it is derived from the polarimetric covariance matrix',\
    'Reference': 'Lee, J.S.; Pottier, E. Polarimetric Radar Imaging: From Basics to Applications; CRC Press: Boca Raton, FL, USA, 2017'
}



Buildings_attr={
    'Units': '',\
    'Format': 'float64',\
    'Range': 'between 0 and 1',\
    'Description': 'the integer value 1 indicates the location of buildings. The values between 0 and 1 show the fuzzy boundary between buildings and non building areas.',\
    'Source': 'topographic base map TOP10NL'
}



Railways_attr={
    'Units': '',\
    'Format': 'float64',\
    'Range': 'between 0 and 1',\
    'Description': 'the integer value 1 indicates the location of railways. The values between 0 and 1 show the fuzzy boundary between railways and non railways.',\
    'Source': 'topographic base map TOP10NL'
}



Water_attr={
    'Units': '',\
    'Format': 'float64',\
    'Range': 'between 0 and 1',\
    'Description': 'the integer value 1 indicates the location of water bodies. The values between 0 and 1 show the fuzzy boundary between water and non water areas.',\
    'Source': 'topographic base map TOP10NL'
}


Roads_attr={
    'Units': '',
    'Format': 'float64',
    'Range': 'between 0 and 1',
    'Description': 'the integer value 1 indicates the location of roads. The values between 0 and 1 show the fuzzy boundary between roads and non roads.',
    'Source': 'topographic base map TOP10NL'
}


Lon_attr ={
    'Units': 'degree',\
    'Format': 'float32',\
    'Description': 'longitude of each pixel'
}


Lat_attr ={
    'Units': 'degree',\
    'Format': 'float32',\
    'Description': 'latitude of each pixel'
}
