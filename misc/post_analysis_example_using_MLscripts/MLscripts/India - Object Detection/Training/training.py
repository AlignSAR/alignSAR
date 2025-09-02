# Importing the required libraries
from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
import os
import random
import pandas as pd

#Data preparation
class Training:
    """This class corresponds to the training of the model"""
    def yolo(pt_model,data,epochs,imgsz,batch,name):
        """This function reads and cleans the data"""
        model = YOLO(pt_model)
        results =model.train(data = data,
            epochs = epochs,
            imgsz = imgsz,
            batch = batch,
            name = name,
            workers=8)
