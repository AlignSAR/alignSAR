# 0.	Dockerfile installation:

- To build the AlignSAR docker image, a user should install docker and download Dockerfile (that can automatically install Doris-5 and its relevant third-party software tools) provided in the github repository (https://github.com/AlignSAR/alignSAR) to a dedicated directory. Inside the directory, the user can build the image using:

docker build -t alignsar .

and test the image by running an interactive terminal session using:

docker run -it -v /your_local_path:/path_you_want_to_set_in_docker alignsar 

Note that one needs to run these commands in terminal, and in the same folder as the ‘docker’ file stored. Here ‘alignsar’ is to be mounted, and can be customized by the end user. Here the argument ‘-it’ is to run the docker image using interface mode in the terminal, while ‘-v’ is to mount the local disk to
docker. Afterward, the Doris-5 installation directory should be modified by editing the files
/root/DorisITCupdate/doris/doris_stack/main_code/doris_main.py (Line 5) and
/root/DorisITCupdate/doris/install/doris_config.xml (Line 2). Specifically, Line 5:
‘sys.path.append(‘/home/username/software/’)’ should be changed to
‘sys.path.append(‘/root/Doris5ITCupdate/’)’ and Line 2: change to ‘<source_path>/root/Doris5ITCupdate/doris</source_path>’.

- To unmount ’alignsar’ one can directly close the terminal.

- To check whether the Dockerfile is initiated after running the commands above, for instance, one can run ‘which doris’ and ‘doris -v’, and receive the information in the terminal:
root@1f6eb227bd0d:/# which doris
/usr/local/bin/doris
root@1f6eb227bd0d:/# doris -v

INFO    : @(#)Doris InSAR software, $Revision: 4.0.8 $, $Author: TUDelft $
Software name:    Doris (Delft o-o Radar Interferometric Software)
Software version: version  4.0.8 (04-09-2014)
                     build      Wed Jan  1 11:08:16 2025

Note that AlignSAR provides SAR data preprocessing workflow using 1) Doris, and 2) LiCSAR and SNAP. ‘Dockerfile’ can install Doris-5 and its relevant third-party software tools, while DockerFile_LiCSAR_SNAP is another dockerfile we offered, which can install LiCSAR and SNAP software. The methods and workflow description can be found in the tutorial ‘AlignSAR_tutorial.pdf’. In case of not building and running the Dockerfile(s), one can also manually install Doris, LiCSAR and SNAP and customize preferred processing environment. 

# 1.	SAR benchmark dataset processing procedure and demonstration 
Please refer to Alignsar_tutorial.pdf
