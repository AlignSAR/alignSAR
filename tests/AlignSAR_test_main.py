###################################################################################
########### Test of SAR benchmark dataset creation using AlignSAR tools ###########
######################## Author Xu Zhang, Date 2025.04 ############################

################################### NOTES #########################################
# There are two test mode you can choose:
# 1. if you set "mode = 1" in line 88, you will run the simple version test, which
# will download some intermediate data to save time and storage space. There
# are around 100 GB data need to be downloaded.
#
# 2. if you set "mode = 2" in line 88, you will run the complete version test, which
# will download all the data and start from the very beginning processing step.
# There are 46.2 GB need to be downloaded.
###################################################################################

########################### How to use the test scripts ###########################
# 1. download AlignSAR_test_main.py file
# 2. open terminal in folder path where you have AlignSAR_test_main.py
# 3. type 'python AlignSAR_test_main.py'
# 4. mode 1 will generate the SAR benchmark dataset in Netcdf format, mode 2 follow
# README to continue
###################################################################################

import requests
import os
import zipfile
import docker

def downloadData(url):
    url += "/download"
    filename = "downloaded_data.zip"
    extract_to = "."
    # downloading
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)

    print("Finish downloading", filename)

    print("Unzipping", filename)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Finish unzipping", filename)


def simpleVersion():
    print("simple version")

    # Step 1: download data
    # vv data
    print("49.7 GB, it takes some time to download")
    downloadData("https://surfdrive.surf.nl/files/index.php/s/m1vIWc2p9ffnrmt")
    # vh data
    print("47.3 GB, it takes some time to download")
    downloadData("https://surfdrive.surf.nl/files/index.php/s/Fa7HWzGnKhpsgBB")

    # raw SAR data
    print("130.8 MB, it takes some time to download")
    downloadData("https://surfdrive.surf.nl/files/index.php/s/TfqPqI7HTWeKCh7")

    # stack_vv_path = os.path.abspath("./stack_vv/")
    # stack_vh_path = os.path.abspath("./stack_vh/")
    # sar_folder_path = os.path.abspath("./unzipped_SAR_data/")

    os.system("python signature_extraction_case1.py")



def completeVersion():
    print("complete version")

    # Complete version #
    # Step 1: download data
    print("46.2 GB, it takes some time to download!!!")
    downloadData("https://surfdrive.surf.nl/files/index.php/s/R0CCetAaHyjl3Z8")

    # Step 2: pre-processing

    # install docker container and run it
    os.system("sudo docker build -t alignsar .")
    os.system("sudo docker run -it -v ./:/home/test alignsar")

    print("Not finished!!! Follow README to continue!!!")
    

def main():

    mode = 1  # 1 is simpleVersion, 2 is complete version

    if mode == 1:
        simpleVersion()
    elif mode == 2:
        completeVersion()
    else:
        print("Choose version type")


if __name__ == "__main__":
    main()





































