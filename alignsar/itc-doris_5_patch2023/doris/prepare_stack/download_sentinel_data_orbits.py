#!/usr/bin/env python3
# This file contains a function to check which files for sentinel are available, which ones are downloaded and a quality
# check for the files which are downloaded.

import ssl
import re
import os, sys
import datetime
import base64
import subprocess
from fiona import collection
from fastkml import kml
from lxml import etree
import xml.etree.ElementTree as ET

from urllib.parse import quote_plus
from urllib.request import Request, urlopen, urlretrieve

def sentinel_available(start_day='', end_day='', sensor_mode='', product='', level='', track='', polarisation='', orbit_direction='', ROI='', user='', password=''):
    # Build query string
    string = ''
    if sensor_mode:
        string += ' AND sensoroperationalmode:' + sensor_mode
    if product:
        string += ' AND producttype:' + product
    if level:
        string += ' AND ' + level
    if orbit_direction:
        string += ' AND orbitdirection:' + orbit_direction
    if track:
        string += ' AND relativeorbitnumber:' + track
    if start_day:
        start = datetime.datetime.strptime(start_day, '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        start = (datetime.datetime.now() - datetime.timedelta(days=350)).strftime('%Y-%m-%d')
    if end_day:
        end = datetime.datetime.strptime(end_day, '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        end = datetime.datetime.now().strftime('%Y-%m-%d')
    if polarisation:
        string += ' AND polarisationmode:' + polarisation
    if ROI:
        shape_str = load_shape_info(ROI)
        string += ' AND footprint:"Intersects(POLYGON(' + shape_str + '))"'

    date_string = f'beginPosition:[{start}T00:00:00.000Z TO {end}T23:59:59.999Z] AND endPosition:[{start}T00:00:00.000Z TO {end}T23:59:59.999Z]'
    string += ' AND ' + date_string

    string = string[5:] + '&rows=1000'
    url = 'https://scihub.copernicus.eu/dhus/search?q=' + quote_plus(string)

    print('Requesting available products: ' + url)
    request = Request(url)
    base64string = base64.b64encode(f'{user}:{password}'.encode('utf-8')).decode('ascii')
    request.add_header("Authorization", "Basic %s" % base64string)

    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    try:
        dat = urlopen(request, context=gcontext)
    except Exception:
        print('not possible to connect this time')
        return [], [], []

    html_dat = dat.read().decode('utf-8', 'ignore')

    parser = etree.HTMLParser()
    tree = etree.fromstring(html_dat.encode('utf-8'), parser)
    products = [data for data in tree.iter(tag='entry')]
    links = [data.find('link').attrib for data in tree.iter(tag='entry')]
    dates = [data.findall('date')[1].text for data in tree.iter(tag='entry')]

    print('Following products will be downloaded')
    for link in links:
        print(link)

    return products, links, dates

def sentinel_available_gnss(start_day='', end_day='', sensor_mode='', product='', level='', track='', polarisation='', orbit_direction='', ROI='', user='', password=''):
    string = ''
    string += ' AND ' + 'platformname:Sentinel-1'
    if sensor_mode:
        string += ' AND sensoroperationalmode:' + sensor_mode
    if product:
        string += ' AND producttype:' + product
    if level:
        string += ' AND ' + level
    if orbit_direction:
        string += ' AND orbitdirection:' + orbit_direction
    if track:
        string += ' AND relativeorbitnumber:' + track
    if start_day:
        start = datetime.datetime.strptime(start_day, '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        start = (datetime.datetime.now() - datetime.timedelta(days=350)).strftime('%Y-%m-%d')
    if end_day:
        end = datetime.datetime.strptime(end_day, '%Y-%m-%d').strftime('%Y-%m-%d')
    else:
        end = datetime.datetime.now().strftime('%Y-%m-%d')
    if polarisation:
        string += ' AND polarisationmode:' + polarisation
    if ROI:
        shape_str = load_shape_info(ROI)
        string += ' AND footprint:"Intersects(POLYGON(' + shape_str + '))"'

    date_string = f'beginPosition:[{start}T00:00:00.000Z TO {end}T23:59:59.999Z] AND endPosition:[{start}T00:00:00.000Z TO {end}T23:59:59.999Z]'
    string += ' AND ' + date_string

    string = string[5:]
    url = 'https://scihub.copernicus.eu/gnss/search?q=' + quote_plus(string)

    print('Requesting available products: ' + url)
    request = Request(url)
    base64string = base64.b64encode(f'{user}:{password}'.encode('utf-8')).decode('ascii')
    request.add_header("Authorization", "Basic %s" % base64string)

    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    try:
        dat = urlopen(request, context=gcontext)
    except Exception:
        print('not possible to connect this time')
        return [], [], []

    html_dat = dat.read().decode('utf-8', 'ignore')

    parser = etree.HTMLParser()
    tree = etree.fromstring(html_dat.encode('utf-8'), parser)
    products = [data for data in tree.iter(tag='entry')]
    links = [data.find('link').attrib for data in tree.iter(tag='entry')]
    dates = [data.findall('date')[1].text for data in tree.iter(tag='entry')]

    print('Following products will be downloaded')
    for link in links:
        print(link)

    return products, links, dates

def load_shape_info(shapefile):
    if shapefile.endswith('.shp'):
        with collection(shapefile, "r") as inputshape:
            for shape in inputshape:
                dat = shape['geometry']['coordinates']
                st = '(' + ','.join(f'{p[0]} {p[1]}' for p in dat[0]) + ')'
                break
    elif shapefile.endswith('.kml'):
        with open(shapefile, 'r', encoding='utf-8') as f:
            doc = f.read()
        k = kml.KML()
        k.from_string(doc)
        shape = list(list(k.features())[0].features())[0].geometry.exterior.coords[:]
        st = '(' + ','.join(f'{p[0]} {p[1]}' for p in shape) + ')'
    else:
        print('format not recognized! Pleas creat either a .kml or .shp file.')
        return []
    return st

def sentinel_check_validity(products=[], destination_folder='', user='', password='', remove=True):
    valid_files = []
    invalid_files = []

    if not products:
        print('Nothing to check')
        return

    for product in products:
        date = str(product.findall('date')[1].text)
        date = datetime.datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S')

        name = str(product.find('title').text)

        track = str(product.find('int[@name="relativeorbitnumber"]').text)
        data_type = str(product.find(".//str[@name='filename']").text)[4:16]
        pol = str(product.find(".//str[@name='polarisationmode']").text).replace(' ', '')
        direction = str(product.find(".//str[@name='orbitdirection']").text)
        if direction == 'ASCENDING':
            direction = 'asc'
        elif direction == 'DESCENDING':
            direction = 'dsc'

        trackfolder = os.path.join(destination_folder, 's1_' + direction + '_t' + track)
        typefolder = os.path.join(trackfolder, data_type + '_' + pol)
        datefolder = os.path.join(typefolder, date.strftime('%Y%m%d'))

        xml_dir = os.path.join(datefolder, name + '.xml')
        file_dir = os.path.join(datefolder, name + '.SAFE.zip')
        kml_dir = os.path.join(datefolder, name + '.kml')
        preview_dir = os.path.join(datefolder, name + '.jpg')

        if os.path.exists(file_dir):
            uuid = product.find('id').text
            valid_dat = sentinel_quality_check(file_dir, uuid, user, password)
        else:
            valid_dat = False

        if not valid_dat:
            if os.path.exists(file_dir) and remove:
                os.system('rm ' + file_dir)
            if os.path.exists(xml_dir) and remove:
                os.system('rm ' + xml_dir)
            if os.path.exists(kml_dir) and remove:
                os.system('rm ' + kml_dir)
            if os.path.exists(preview_dir) and remove:
                os.system('rm ' + preview_dir)
            invalid_files.append(file_dir)
        else:
            valid_files.append(file_dir)

    return invalid_files, valid_files

def sentinel_download(products=[], xml_only=False,  destination_folder='', project_folder='', user='', password=''):
    if not products:
        print('No files to download')
        return

    wget_base = ('wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 '
                 '--continue --tries=20 --no-check-certificate --user=' + user + ' --password=' + password + ' ')

    for product in products:
        date = str(product.findall('date')[1].text)
        date = datetime.datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S')

        url = '"' + product.findall('link')[0].attrib['href'][:-6] + quote_plus('$value') + '"'
        name = str(product.find('title').text)

        track = str(product.find('int[@name="relativeorbitnumber"]').text)
        data_type = str(product.find(".//str[@name='filename']").text)[4:16]
        pol = str(product.find(".//str[@name='polarisationmode']").text).replace(' ', '')
        direction = str(product.find(".//str[@name='orbitdirection']").text)
        if direction == 'ASCENDING':
            direction = 'asc'
        elif direction == 'DESCENDING':
            direction = 'dsc'

        trackfolder = os.path.join(destination_folder, direction + '_t' + track.zfill(3))
        if not os.path.exists(trackfolder):
            os.mkdir(trackfolder)
        typefolder = os.path.join(trackfolder, data_type + '_' + pol)
        if not os.path.exists(typefolder):
            os.mkdir(typefolder)
        datefolder = os.path.join(typefolder, date.strftime('%Y%m%d'))
        if not os.path.exists(datefolder):
            os.mkdir(datefolder)

        xml_dir = os.path.join(datefolder, name + '.xml')
        file_dir = os.path.join(datefolder, name + '.SAFE.zip')
        kml_dir = os.path.join(datefolder, name + '.kml')
        preview_dir = os.path.join(datefolder, name + '.jpg')

        if project_folder:
            datefolder = os.path.join(project_folder, 's1', date.strftime('%Y%m%d') + '_t' + track)
            if not os.path.exists(datefolder):
                os.mkdir(datefolder)
            sentinel_folder = os.path.join(datefolder, 'sentinel_1')
            if not os.path.exists(sentinel_folder):
                os.mkdir(sentinel_folder)

            xml_project = os.path.join(datefolder, 'sentinel_1', name + '.xml')
            link_project = os.path.join(datefolder, 'sentinel_1', name + '.SAFE.zip')
            kml_project = os.path.join(datefolder, 'sentinel_1', name + '.kml')
            preview_project = os.path.join(datefolder, 'sentinel_1', name + '.jpg')

        # Save .xml files
        prod = etree.ElementTree(product)
        if not os.path.exists(xml_dir):
            prod.write(xml_dir, pretty_print=True)
        if project_folder:
            if not os.path.exists(xml_project):
                prod.write(xml_project, pretty_print=True)

        prev = "'preview'"
        png = "'quick-look.png'"
        kmls = "'map-overlay.kml'"
        dats = "'" + name + ".SAFE'"

        preview_url = url[:-10] + '/Nodes(' + dats + ')/Nodes(' + prev + ')/Nodes(' + png + ')/' + quote_plus('$value') + '"'
        kml_url = url[:-10] + '/Nodes(' + dats + ')/Nodes(' + prev + ')/Nodes(' + kmls + ')/' + quote_plus('$value') + '"'

        if not xml_only:
            if not os.path.exists(file_dir):
                wget_data = wget_base + url + ' -O ' + file_dir
                print('download url is:' + wget_data)
                os.system(wget_data)

                uuid = product.find('id').text
                valid = sentinel_quality_check(file_dir, uuid, user, password)
            else:
                valid = True

            if valid:
                if not os.path.exists(preview_dir):
                    wget_preview = wget_base + preview_url + ' -O ' + preview_dir
                    os.system(wget_preview)
                if not os.path.exists(kml_dir):
                    wget_kml = wget_base + kml_url + ' -O ' + kml_dir
                    os.system(wget_kml)

                if project_folder:
                    if not os.path.exists(preview_project):
                        os.system('cp ' + preview_dir + ' ' + preview_project)
                    if not os.path.exists(kml_project):
                        os.system('cp ' + kml_dir + ' ' + kml_project)
                    if not os.path.exists(link_project):
                        os.system('ln -s ' + file_dir + ' ' + link_project)
            else:
                os.system('rm ' + file_dir)
                os.system('rm ' + xml_dir)
                if project_folder:
                    os.system('rm ' + xml_project)

def sentinel_orbit_gnss_download(products=[], xml_only=False,  destination_folder='', project_folder='', user='', password=''):
    if not products:
        print('No files to download')
        return

    wget_base = ('wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 '
                 '--continue --tries=20 --no-check-certificate --user=' + user + ' --password=' + password + ' ')

    for product in products:
        date = str(product.findall('date')[1].text)
        _ = datetime.datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S')

        url = '"' + product.findall('link')[0].attrib['href'][:-6] + quote_plus('$value') + '"'
        name = str(product.find('title').text)
        wget_data = wget_base + url + ' -O ' + os.path.join(destination_folder, name)
        print('download url is:' + wget_data)
        os.system(wget_data)

def sentinel_quality_check(filename, uuid, user, password):
    checksum_url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + uuid + "')/Checksum/Value/" + quote_plus('$value')
    request = Request(checksum_url)
    base64string = base64.b64encode(f'{user}:{password}'.encode('utf-8')).decode('ascii')
    request.add_header("Authorization", "Basic %s" % base64string)

    try:
        dat = urlopen(request)
    except Exception:
        print('not possible to connect this time')
        return False

    html_dat = dat.read().decode('utf-8', 'ignore').strip().lower()

    # md5 on mac/linux
    try:
        if sys.platform.startswith('darwin'):
            out = subprocess.check_output(f'md5 {filename}', shell=True).decode('utf-8', 'ignore').strip()
            # Format: MD5 (file) = <hash>
            md5 = out.split('=')[-1].strip()
        elif sys.platform.startswith('linux'):
            out = subprocess.check_output(f'md5sum {filename}', shell=True).decode('utf-8', 'ignore').strip()
            md5 = out.split()[0]
        else:
            print('This function only works on mac or linux systems!')
            return False
    except Exception:
        return False

    return (md5.lower() == html_dat)

def download_orbits_1(start_date, end_date, pages=30, precise_folder='', restituted_folder =''):
    pass

def download_orbits(start_date, end_date, pages=30, precise_folder='', restituted_folder =''):
    pages_res = min(pages, 60)
    pages_poe = pages
    last_precise = ''

    start_num = int(start_date[0:4] + start_date[5:7] + start_date[8:10])
    end_num = int(end_date[0:4] + end_date[5:7] + end_date[8:10])

    if precise_folder:
        for i in range(pages_poe):
            url = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/?page=' + str(i + 1)
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            try:
                page = urlopen(url, context=gcontext)
            except TypeError:
                page = urlopen(url)

            html = page.read().decode('utf-8', 'ignore').split('\n')
            orb_files = []

            for line in html:
                if re.search('<a .*href=.*>', line):
                    if re.search('EOF', line):
                        datm = re.search('<a href=.*>(.*)</a>', line)
                        if datm:
                            orb_files.append(datm.group(1))
            
            if not last_precise and orb_files:
                last_precise = orb_files[0]

            for orb in orb_files:
                filename = os.path.join(precise_folder, orb)
                if int(orb[42:50]) + 1 <= end_num and int(orb[42:50]) + 1 >= start_num:
                    urlf = 'http://aux.sentinel1.eo.esa.int/POEORB/'+orb[25:29]+'/'+orb[29:31]+'/'+orb[31:33]+'/'+orb+'.EOF'
                    if not os.path.exists(filename):
                        try:
                            urlretrieve(urlf, filename)
                        except Exception:
                            pass
                        print(orb + ' downloaded')
                    else:
                        print(orb + ' already downloaded')
                else:
                    print(orb + ' is out of date range')

            if orb_files and int(orb[42:50]) < start_num:
                break

    if restituted_folder:
        now = datetime.datetime.now()
        last_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        diff = datetime.timedelta(days=25)

        print('Time difference to last date is ' + str((now - last_date).days))

        if now - last_date < diff:
            for i in range(pages_res):
                url = 'https://qc.sentinel1.eo.esa.int/aux_resorb/?page=' + str(i + 1)
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                try:
                    page = urlopen(url, context=gcontext)
                except TypeError:
                    page = urlopen(url)

                html = page.read().decode('utf-8', 'ignore').split('\n')
                orb_files = []

                for line in html:
                    if re.search('<a .*href=.*>', line):
                        if re.search('EOF', line):
                            datm = re.search('<a href=.*>(.*)</a>', line)
                            if datm:
                                orb_files.append(datm.group(1))

                for orb in orb_files:
                    filename = os.path.join(precise_folder, orb)
                    if int(orb[42:50]) + 1 <= end_num and int(orb[42:50]) + 1 >= start_num:
                        urlf = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/' + orb
                        if not os.path.exists(filename):
                            try:
                                urlretrieve(urlf, filename)
                            except Exception:
                                pass
                            print(orb + ' downloaded')
                        else:
                            print(orb + ' already downloaded')
                    else:
                        print(orb + ' is out of date range')

                if orb_files and int(orb[42:50]) < start_num:
                    break

# Actually execute the code...
if __name__ == "__main__":

    stack_folder = sys.argv[1]

    xml_file = os.path.join(os.path.join(stack_folder, 'doris_input.xml'))
    tree = ET.parse(xml_file)
    settings = tree.getroot()[0]
    print('reading xml file stack ' + xml_file)

    ROI = settings.find('.shape_file_path').text
    polarisation = settings.find('.polarisation').text
    archive_folder = settings.find('.sar_data_folder').text
    track = settings.find('.track').text
    orbit_folder = settings.find('.orbits_folder').text

    start_date = settings.find('.start_date').text
    end_date = settings.find('.end_date').text

    level = 'L1'
    sensor_mode = 'IW'
    product = 'SLC'
    orbit_precice_product = 'AUX_POEORB'

    xml_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_xml_file = os.path.join(os.path.join(xml_name, 'install', 'doris_config.xml'))
    print('reading xml file settings doris ' + config_xml_file)
    tree = ET.parse(config_xml_file)
    settings = tree.getroot()
    user = settings.find('.scihub_username').text
    password = settings.find('.scihub_password').text

    precise_folder = os.path.join(orbit_folder, 'precise')
    if not os.path.exists(precise_folder):
        os.makedirs(precise_folder)
    restituted_folder = os.path.join(orbit_folder, 'restituted')
    if not os.path.exists(restituted_folder):
        os.makedirs(restituted_folder)
    
    products_orbits, links_orbits, dates_orbits = sentinel_available_gnss(
        start_day=start_date, end_day=end_date, product=orbit_precice_product,
        user='gnssguest', password='gnssguest'
    )
    
    sentinel_orbit_gnss_download(products_orbits, destination_folder=precise_folder, user='gnssguest', password='gnssguest')
    # download_orbits(start_date, end_date, pages=300, precise_folder=precise_folder, restituted_folder=restituted_folder)
    # download_orbits_1(start_date, end_date, pages=300, precise_folder=precise_folder, restituted_folder=restituted_folder)
