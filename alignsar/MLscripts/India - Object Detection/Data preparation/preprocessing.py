import rioxarray
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import matplotlib.cm as cm
import netCDF4 as nc
import os
import cv2
import  xml.dom.minidom
import math
import xmltodict
import matplotlib.patches as patches
import ast
from collections import namedtuple
from PIL import Image
import joblib
from joblib import Parallel, delayed
import albumentations as A
from matplotlib.image import imsave
 
#Data preparation
class Data_preparation:
    """This class corresponds to the data preparation and subtiling"""
    def read_data(path):
        """This function reads and cleans the data"""
        
        # Read netCDF file
        dataset = xr.open_dataset(path)
        
        #Convert dataset to pandas
        data = dataset.to_dataframe()
        
        #Obtain entropy
        entropy =dataset.variables['Entropy'].values
        
        #Remove nan
        #Find indices that you need to replace
        inds = np.isnan(entropy)
        entropy[inds] = np.nanmedian(entropy)
        #Place column means in the indices. Align the arrays using take
        
        #Read mask
        l1_y =dataset.variables['Oil region'].values
        
        return entropy, l1_y
    
    def get_tiles(entropy,l1_y,data_folder):
        """This function obtains the tiles for the image and the mask"""
        
        #Image dimensions
        x0 = 4300
        y0 = 2350
        
        #Get image tiles
        l1_x_00 = entropy[:x0,:y0]
        l1_x_01 = entropy[:x0,y0:]
        l1_x_10 = entropy[x0:,:y0]
        l1_x_11 = entropy[x0:,y0:]
        
        
        #Get masked tiles
        l1_y_00 = l1_y[:x0,:y0]
        l1_y_01 = l1_y[:x0,y0:]
        l1_y_10 = l1_y[x0:,:y0]
        l1_y_11 = l1_y[x0:,y0:]
        
        #Save masks
        plt.imsave(data_folder+"x_0.png", l1_x_00, cmap=cm.gray)
        plt.imsave(data_folder+"x_1.png", l1_x_01, cmap=cm.gray)
        plt.imsave(data_folder+"x_3.png", l1_x_10, cmap=cm.gray)
        plt.imsave(data_folder+"x_4.png", l1_x_11, cmap=cm.gray)

        plt.imsave(data_folder+"y_0.png", l1_y_00, cmap=cm.gray)
        plt.imsave(data_folder+"y_1.png", l1_y_01, cmap=cm.gray)
        plt.imsave(data_folder+"y_3.png", l1_y_10, cmap=cm.gray)
        plt.imsave(data_folder+"y_4.png", l1_y_11, cmap=cm.gray)
        
        #Save images
        plt.imsave(data_folder+"x.png", entropy, cmap=cm.gray)
        plt.imsave(data_folder+"y.png", l1_y, cmap=cm.gray)
    
    
class Augmentations:
    """This class performs the different data augmentations to obtain a larger dataset"""
    def pascalVOC_yolo(labels,labels_yolo):
        """This function converts the original labels from pascalVOC xml file to yolo"""
        
        #Open Xml file
        with open(labels, 'r') as file:
            xml = file.read()

        xml_dict = xmltodict.parse(xml)
        class_dict = {'oil': 0}
        
        #Get image dimensions
        img_w = int(xml_dict['annotation']['size']['width'])
        img_h = int(xml_dict['annotation']['size']['height'])
        
        #Save bbox coordinates into a list
        coord = list()
        with open(labels_yolo, 'w') as file:
            for bb in xml_dict['annotation']['object']:
                class_num = class_dict[bb['name']]
                x =(float(bb['bndbox']['xmin'])+float(bb['bndbox']['xmax'])) /2 / img_w
                y =(float(bb['bndbox']['ymin'])+float(bb['bndbox']['ymax'])) /2 / img_h
                w = float(bb['bndbox']['xmax'])-float(bb['bndbox']['xmin'])
                h = float(bb['bndbox']['ymax'])-float(bb['bndbox']['ymin'])
                
                w /= img_w
                h /= img_h
                
                #Save yolo annotations
                coord.append([x, y, w, h])
                line = f'{class_num} {x} {y} {w} {h}\n'
                file.write(line)
                
        return coord, img_w, img_h

    
    def yolo_coco(yolo_annotation_path,image_width,image_height):
        """This function converts the original labels from yolo xml file to coco"""
        bboxes = []
        category_ids = []
        
        #Open yolo annotations
        with open(yolo_annotation_path, "r") as f:
            lines = f.readlines()
        
        #Get bboxes and convert to COCO format
        for line in lines:
            parts = line.strip().split()
            class_index = int(parts[0])
            x_center, y_center, box_width, box_height = map(float, parts[1:5])

            # Convert YOLO coordinates to COCO format
            x_min = int((x_center - box_width / 2) * image_width)
            y_min = int((y_center - box_height / 2) * image_height)
            coco_width = int(box_width * image_width)
            coco_height = int(box_height * image_height)

            bboxes.append([x_min,y_min,coco_width,coco_height])
            category_ids.append(class_index)

        return bboxes, category_ids
    
    def augmentations_definition():
        """This function defines the augmentations to perform"""
        #Horizontal flip
        transform0 = A.Compose([
                        A.HorizontalFlip(p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Vertical flip
        transform1 = A.Compose([
                        A.VerticalFlip(p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random Rotate 90
        transform2 = A.Compose([
                        A.RandomRotate90(p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #ShiftScaleRotate
        transform3 = A.Compose([
                        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=5, border_mode=0, p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random Crop
        transform4 = A.Compose([
                        A.RandomCrop(3000,1500),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random horizontal + scr
        transform5 = A.Compose([
                    A.HorizontalFlip(p=1),
                    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=5, border_mode=0, p=1),
                    ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random vertical + scr
        transform6 = A.Compose([
                    A.VerticalFlip(p=1),
                    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=5, border_mode=0, p=1),
                    ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #ShiftScaleRotate2
        transform7 = A.Compose([
                        A.ShiftScaleRotate(shift_limit=-0.15, scale_limit=-0.15, rotate_limit=3, border_mode=0, p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random horizontal + scr + crop
        transform8 = A.Compose([
                    A.HorizontalFlip(p=1),
                    A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=10, border_mode=0, p=1),
                    A.RandomCrop(3000,1500)
                    ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random vertical + scr + crop
        transform9 = A.Compose([
                    A.VerticalFlip(p=1),
                    A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=10, border_mode=0, p=1),
                    A.RandomCrop(3000,1500)
                    ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random Rotate 45
        transform10 = A.Compose([
                        A.Rotate(limit = 45,p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))

        #Random Rotate 180
        transform11 = A.Compose([
                        A.Rotate(limit = 45,p=1),
                        A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=10, border_mode=0, p=1),
                        ], bbox_params=A.BboxParams(format='coco', label_fields=['category_ids']))
        
        
        
        return transform0, transform1, transform2, transform3, transform4, transform5, transform6, transform7, transform8, transform9, transform10, transform11
    
    def perform_augmentations(transforms,img_path, bboxes, category_ids,c):
        """This function performs the augmentations using the coco annotations"""
        #Read image
        image = cv2.imread(img_path)
        #Try transforms
        for t in transforms:
            try:
                
                transformed = t(image=image, bboxes=bboxes, category_ids=category_ids)
                print(c)
            #If transform cannot be performed, stop the cycle
            except:
                print('Transformations achieved until transformation #', c-1, ' please update c and the transformations list, commenting the transformations already performed')
                break
                
            #Save augmented image
            image = transformed['image']
            bboxes = transformed['bboxes']
            p = img_path[:-4]+'_'+str(c)+'.png'
            l = img_path[:-4]+'_'+str(c)+'.txt'
            cv2.imwrite(p,image)
            c=c+1

            img_width = image.shape[1]
            img_height = image.shape[0]
            coord = list()
            class_num = 0
            
            #Save augmented bboxes
            with open(l,'w') as file:
                for bbox in bboxes:
                    x_min, y_min, w, h = bbox
                    x_min, x_max, y_min, y_max = int(x_min), int(x_min + w), int(y_min), int(y_min + h)

                    x = (x_min + x_max) / 2 / img_width
                    y = (y_min + y_max) / 2 / img_height
                    w = (x_max - x_min) / img_width
                    h = (y_max - y_min) / img_height

                    coord.append([x, y, w, h])
                    line = f'{class_num} {x} {y} {w} {h}\n'

                    file.write(line)
                
            transformed=None

        
                             