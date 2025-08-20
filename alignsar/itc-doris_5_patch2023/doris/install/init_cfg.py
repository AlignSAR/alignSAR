#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import os

def init_cfg():
    template_xml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doris_config_template.xml')
    xml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doris_config.xml')
    tree = ET.parse(template_xml_file)
    settings = tree.getroot()

    # Set source_path
    settings.find('source_path').text = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Prompt for doris_path
    valid = False
    while not valid:
        user_input = input("Enter the path to doris: ")
        if os.path.exists(user_input) and user_input.endswith('doris'):
            settings.find('doris_path').text = user_input
            valid = True
        else:
            print('The path is incorrect, use another path')

    # Prompt for cpxfiddle_path
    valid = False
    while not valid:
        user_input = input("Enter the path to cpxfiddle: ")
        if os.path.exists(user_input) and user_input.endswith('cpxfiddle'):
            settings.find('cpxfiddle_path').text = user_input
            valid = True
        else:
            print('The path is incorrect, use another path')

    # Prompt for snaphu_path
    valid = False
    while not valid:
        user_input = input("Enter the path to snaphu: ")
        if os.path.exists(user_input) and user_input.endswith('snaphu'):
            settings.find('snaphu_path').text = user_input
            valid = True
        else:
            print('The path is incorrect, use another path')

    # Scihub credentials
    user_input = input("Enter your username for scihub (https://scihub.copernicus.eu/dhus/#/self-registration): ")
    if user_input:
        settings.find('scihub_username').text = user_input
    else:
        print('Username field is empty, you can change it later in the doris_config.xml file')

    user_input = input("Enter your password for scihub: ")
    if user_input:
        settings.find('scihub_password').text = user_input
    else:
        print('Password field is empty, you can change it later in the doris_config.xml file')

    # USGS credentials
    user_input = input("Enter your username for srtm download (https://urs.earthdata.nasa.gov/users/new/): ")
    if user_input:
        settings.find('usgs_username').text = user_input
    else:
        print('Username field is empty, you can change it later in the doris_config.xml file')

    user_input = input("Enter your password for srtm download: ")
    if user_input:
        settings.find('usgs_password').text = user_input
    else:
        print('Password field is empty, you can change it later in the doris_config.xml file')

    print('Doris is initialized. If you want to make changes later, '
          'you can change the doris_config.xml file or run this script again.')

    tree.write(xml_file)

# Execute script
if __name__ == "__main__":
    init_cfg()
