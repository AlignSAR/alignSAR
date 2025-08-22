# AlignSAR
The AlignSAR tools are used to extract representative SAR signatures, and ultimately offer FAIR-guided open SAR benchmark dataset library designed for SAR-based artificial intelligence applications, while ensuring interoperability and consistency with existing and upcoming initiatives and technologies, facilitating wider exploitation of SAR data and its integration and combination with other datasets. This library will contain meaningful and accurate SAR signatures created by integrating and aligning multi-SAR images and other geodetic measurements in time and space. Related link: https://www.alignsar.nl

## Installation

Python version `>=3.10` is required to install MOTrainer.

MOTrainer can be installed from PyPI:

```sh
pip install alignsar
```

We suggest using conda
 to create an isolated environment for the installation to avoid conflicts.
 
## Dockerfile Setup

1. **Preparation**  
   Install Docker and download the [`Dockerfile`](https://github.com/AlignSAR/alignSAR) from the repository into a dedicated directory.  
   This file automatically installs Doris-5 and related third-party tools.

2. **Build the image**
   ```bash
   docker build -t alignsar .
````

3. **Run the container**

   ```bash
   docker run -it -v /your_local_path:/path_in_docker alignsar
   ```

   * `-it`: interactive mode
   * `-v`: mount a local path to the container

---

### SAR Benchmark Dataset Processing

Please refer to the [AlignSAR\_tutorial.pdf](https://github.com/AlignSAR/alignSAR/blob/main/tutorial/AlignSAR_tutorial.pdf) for the complete SAR benchmark dataset processing procedure and demonstration.

---

### Tutorial and Sample Data

A set of sample data covering the city of Groningen, the Netherlands, can be found in [`/examples/data/data_links.txt`](examples/data/data_links.txt).

---

### Citations

\[1] Ling Chang, Anurag Kulshrestha, Bin Zhang and Xu Zhang (2023). Extraction and analysis of radar scatterer attributes.

\[2] Anurag Kulshrestha, Ling Chang and Alfred Stein (2024). Radarcoding reference data for SAR training data creation.

\[3] Ling Chang, Jose Manuel Delgado Blasco, Andrea Cavallini, Andy Hooper, Anurag Kulshrestha, Milan Lazecky, Wojciech Perz.

\[4] Ling Chang, Xu Zhang, Anurag Kulshrestha, Serkan Girgin, Alfred Stein, Jose Manuel Delgado Blasco, Angie Catalina Flórez.


