#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

class CreateBash(object):
    def __init__(self):
        pass

    def create(self, stack_folder, root_folder, nodes):
        # Load doris_config.xml
        xml_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'install', 'doris_config.xml'
        )
        tree = ET.parse(xml_file)
        settings = tree.getroot()

        source_path = settings.find('source_path').text
        doris_folder = os.path.dirname(settings.find('doris_path').text)
        cpxfiddle_folder = os.path.dirname(settings.find('cpxfiddle_path').text)
        snaphu_folder = os.path.dirname(settings.find('snaphu_path').text)

        # === doris_stack.sh ===
        file_path = os.path.join(stack_folder, 'doris_stack.sh')
        doris_run_script = os.path.join(source_path, 'doris_stack', 'main_code', 'doris_main.py')

        with open(file_path, 'w') as f:
            f.write('#!/bin/bash\n\n')
            f.write(f'#PBS -l nodes=1:ppn={nodes}\n\n')
            f.write(f'source_path={source_path}\n')
            f.write('export PYTHONPATH=$source_path:$PYTHONPATH\n')
            f.write(f'export PATH={doris_folder}:{cpxfiddle_folder}:{snaphu_folder}:$PATH\n')
            f.write(f'python3 {doris_run_script} -p {stack_folder}\n')

        os.chmod(file_path, 0o744)

        # === create_dem.sh ===
        file_path = os.path.join(stack_folder, 'create_dem.sh')
        doris_run_script = os.path.join(source_path, 'prepare_stack', 'create_dem.py')

        with open(file_path, 'w') as f:
            f.write('#!/bin/bash\n\n')
            f.write(f'source_path={source_path}\n')
            f.write('export PYTHONPATH=$source_path:$PYTHONPATH\n')
            f.write(f'python3 {doris_run_script} {stack_folder} SRTM3\n')

        os.chmod(file_path, 0o744)

        # === download_sentinel.sh ===
        file_path = os.path.join(stack_folder, 'download_sentinel.sh')
        doris_run_script = os.path.join(source_path, 'prepare_stack', 'download_sentinel_data_orbits.py')

        with open(file_path, 'w') as f:
            f.write('#!/bin/bash\n\n')
            f.write(f'source_path={source_path}\n')
            f.write('export PYTHONPATH=$source_path:$PYTHONPATH\n')
            f.write(f'python3 {doris_run_script} {stack_folder}\n')

        os.chmod(file_path, 0o744)
