# AlignSAR Demo — example.md

> 🚀 A fully reproducible step-by-step AlignSAR demonstration, including **Docker preprocessing**, **Conda environment setup**, **data download**, and **script execution**.  
> Tested on **Linux (Ubuntu)**.  
> **Last updated:** 2025-09-02

---

## 🧭 Table of Contents

- [Background and Goal](#background-and-goal)  
- [Prerequisites](#prerequisites)  
- [Quick Start](#quick-start-tldr)  
- [Step 1: Clone the repository and build the Docker image](#step-1-clone-the-repository-and-build-the-docker-image)  
- [Step 2: Create a Conda environment and install dependencies](#step-2-create-a-conda-environment-and-install-dependencies)  
- [Step 3: Download demo datasets](#step-3-download-demo-datasets)  
- [Step 4: Run DORIS preprocessing (inside Docker)](#step-4-run-doris-preprocessing-inside-docker)  
- [Step 5: Generate radar coding parameters and run RadarCode](#step-5-generate-radar-coding-parameters-and-run-radarcode)  
- [Step 6: Run benchmark scripts](#step-6-run-benchmark-scripts)  

---

## 📌 Background and Goal

This demo walks through the **full AlignSAR pipeline**, from preprocessing raw SAR stacks to running benchmark scripts for feature extraction and metadata generation.  

The workflow covers:
- Cloning and building AlignSAR with Docker
- Setting up a Python/Conda environment for post-processing
- Running DORIS stack generation
- Executing RadarCode and benchmark tools

---

## 🛠 Prerequisites

- Linux OS (tested on Ubuntu)
- `docker` installed and running
- `conda` available (`miniconda` or `anaconda`)
- Stable internet connection for dataset download

---

## ⚡ Quick Start

```bash
# Create working directory
mkdir /mnt/example && cd /mnt/example

# Clone and build AlignSAR
git clone https://github.com/AlignSAR/alignSAR.git
cd alignSAR && sudo docker build -t alignsar .

# Set up Conda environment
cd /mnt/example
conda create -n alignsar python=3.10 -c conda-forge -y
conda activate alignsar
conda install -c conda-forge gdal==3.8.5 rasterio geopandas pyproj rioxarray -y
pip install alignsar

# Download datasets
curl -L -o pre-process.zip "https://surfdrive.surf.nl/files/index.php/s/TfqPqI7HTWeKCh7/download"
curl -L -o benchmark.zip "https://surfdrive.surf.nl/files/index.php/s/3J1f2m1nT4vG3eE/download"
unzip pre-process.zip -d pre-process
unzip benchmark.zip -d benchmark
```

---

## 1️⃣ Step 1: Clone the repository and build the Docker image

```bash
mkdir /mnt/example
cd /mnt/example
git clone https://github.com/AlignSAR/alignSAR.git
cd alignSAR/
sudo docker build -t alignsar .
```

---

## 2️⃣ Step 2: Create a Conda environment and install dependencies

```bash
cd /mnt/example
conda create -n alignsar python=3.10 -c conda-forge -y
conda activate alignsar
conda install -c conda-forge gdal==3.8.5 rasterio geopandas pyproj rioxarray -y
pip install alignsar
```

---

## 3️⃣ Step 3: Download demo datasets

```bash
curl -L -o pre-process.zip "https://surfdrive.surf.nl/files/index.php/s/TfqPqI7HTWeKCh7/download"
curl -L -o benchmark.zip "https://surfdrive.surf.nl/files/index.php/s/3J1f2m1nT4vG3eE/download"

unzip pre-process.zip -d pre-process
unzip benchmark.zip -d benchmark
```

---

## 4️⃣ Step 4: Run DORIS preprocessing (inside Docker)

```bash
cd /mnt/example/pre-process
sudo docker run -it -v .:/home/test alignsar

# Inside Docker:
cd /home/test/stack_vh
bash doris_stack.sh
cd /home/test/stack_vv
bash doris_stack.sh
exit

# Back on host:
sudo chmod -R 777 *
```

---

## 5️⃣ Step 5: Generate radar coding parameters and run RadarCode

```bash
cd /mnt/example/pre-process/rdrcoding
python create_parm.py
rdrCode.py --inputFile input_card.txt
```

---

## 6️⃣ Step 6: Run benchmark scripts

```bash
cd /mnt/example/benchmark

signature_extraction.py   --doris_stack_dir_vv /mnt/example/benchmark/stack_vv   --doris_stack_dir_vh /mnt/example/benchmark/stack_vh   --master_date 20220214   --crop_first_line 500   --crop_last_line 1440   --crop_first_pixel 16000   --crop_last_pixel 18350   --lines_full 2842   --pixels_full 22551   --netcdf_lines 2350   --netcdf_pixels 940   --lam_file /mnt/example/benchmark/stack_vv/lam.raw   --phi_file /mnt/example/benchmark/stack_vv/phi.raw   --sar_folder_path /mnt/example/benchmark/unzipped_SAR_data   --max_images 30

Meta_info_extraction_global_local.py   --sar_folder /mnt/example/benchmark/unzipped_SAR_data/   --folder_num 0   --xml_num 0   --lon_max 6.6342616   --lon_min 6.4574795   --lat_max 53.12726   --lat_min 53.12726   --master_date 20220214   --crp_list '[500, 1440, 16000, 18350]'

stac.py   --inputfile netcdf_20220109_full_attributes.nc   --lon-name lon.tif   --lat-name lat.tif   --num-x 10   --num-y 10
```



