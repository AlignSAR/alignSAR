import rioxarray
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import xarray as xr
import numpy as np
import matplotlib.cm as cm
import h5py
import os
import pandas as pd
import collections, numpy
import time

class Labeling:
    """This class aims to perform the data labeling, based on the probability of belonging to each class """
    def get_data(x):
        #This functions reads the data of the NetCDF and convert is as pandas dataframe
        
        # read netCDF
        # groningen_x1 = xr.open_dataarray(x)
        groningen_x1 = nc.Dataset(x)
        
        #Convert to numpy array
        # xarr = groningen_x1.to_numpy()
        variable_names = groningen_x1.variables.keys()
        xarr = [np.array(groningen_x1.variables[variable_name][:]) for variable_name in variable_names]

        #Reshape the data
        # xarr_df = np.reshape(xarr, (xarr.shape[0]*xarr.shape[1],xarr.shape[2]))
        xarr_df = np.reshape(xarr, (len(xarr[0])*len(xarr[0][0]),len(xarr)))
        
        #Convert numpy array to pandas dataframe
        xdf = pd.DataFrame(xarr_df, columns=groningen_x1.signatures.to_numpy())

        return groningen_x1,xdf
        
    def obtain_labels(xdf, th, a,b):
        #This function assigns a label to each pixel
        
        #Cut the dataset according to a and b
        xdf = xdf[a:b]
        
        #Reset index
        xdf = xdf.reset_index()
        
        #Convert dataframe to numpy array
        df_np=xdf.to_numpy()
        
        #Initialize necessary variables
        df_reference = []
        l = []
        
        #Only necesary to print the progress of the pixel labeling, by printing the #of pixels that
        #have been already labeled 
        nn = int(len(xdf)*0.05)
        
        """CHANGE: START"""
        #Create one dataframe for each label
        ### You must add the additional labels of your data
        buildings = xdf['Buildings']
        railways = xdf['Railways']
        water = xdf['Water']
        roads = xdf['Roads']
        ##### label_5 = xdf['label_5']
        ##### label_6 = xdf['label_6']
        ##### ...
        ##### label_n = xdf['label_n']
        """CHANGE: END"""
        
        #For loop that goes over all pixels
        for i in range(len(xdf)):
            #Print the progress of the label assignation every 5%
            if i%nn==0:
                msg = "Loading " + str(i) + " images\n"
                print(msg)
            
            """CHANGE: START"""
            #If statements to obtain the labels for each pixel
            if buildings[i] >= th:
                #a_label = [1,0,0,0,0,...,0]
                l.append(0)
                df_reference.append(df_np[i])
            if railways[i] >= th:
                #a_label = [0,1,0,0,0,...,0]
                l.append(1)
                df_reference.append(df_np[i])
            if water[i] >= th:
                #a_label = [0,0,1,0,0,...,0]
                l.append(2)
                df_reference.append(df_np[i])
            if roads[i] >= th:
                #a_label = [0,0,0,1,0,...,0]
                l.append(3)
                df_reference.append(df_np[i])
            ### Add here the corresponding if statements, one for each additional label you have
            
            ##### if label_5[i] >= th:
            #####    #a_label = [0,0,0,1,0,...,0]
            #####    l.append(4)
            #####    df_reference.append(df_np[i])
            #####
            #####    ...
            #####
            ##### if label_n[i] >= th:
            #####    #a_label = [0,0,0,0,0,...,1]
            #####    l.append(n)
            #####    df_reference.append(df_np[i])
            
            #If none of the label layers was higher than the set th, the pixel will be classified as 
            #undefined pixel
            
            ### You must add the additional labels to the next if statment
            if buildings[i] == 0 and railways[i] == 0 and water[i] == 0 and roads[i] ==0:
            ##### if buildings[i] == 0 and railways[i] == 0 and water[i] == 0 and roads[i] ==0 and label_5[i] == 0 and ... and label_n[i] == 0:
                
                #a_label = [0,0,0,0,...,1]
                l.append(4)
                df_reference.append(df_np[i])
            """CHANGE: END"""
            
            #Get counter of elements per label
            counter = collections.Counter(l)
        #Add label column
        df_l_r = pd.DataFrame(df_reference,columns=list(xdf.columns))
        df_l_r['label']=l
        
        """CHANGE: START"""
        #Drop unnecessary layers
        ### Add after roads the additional layers
        df_l_r.drop(['Buildings','Railways','Water','Roads'], axis=1)
        """CHANGE: END"""
        return l,counter, df_l_r
    
    def create_csv(xdf,path):
        xdf = xdf.drop(['index'],axis=1)
        #Save all features
        if os.path.exists(path):
            with open(path, 'a') as f:
                xdf.to_csv(f, header=False)
        else:
            xdf.to_csv(path)  

        msg = "%%%%%%%%%%%%%%%Image processing done%%%%%%%%%%%%%%%"
        print(msg)


    
class Filtering:
    """This class balances the data to have the same number of elements per class
       ideally, we would like to have about 1000 elements per class, if any class has 
       a very low number of elements you might consider removing it or joining two
       similar classes together"""
    
    def get_data(data):
        #This function gets the data and concatenates it
        
        #Create empty dataframe to store all data from each image
        df_ = pd.DataFrame()
        
        #Loop for over the N csv files
        for i in data:
            #Read csv file
            df = pd.read_csv(i,on_bad_lines='skip')
            #Concatenate with already created dataframe
            df_ = pd.concat([df_,df],ignore_index = True)
        return df_
    
    def clean_data(df_):
        #This function applies the necessary transformations to the data
        
        def toDB(x):
            #Converstion to Db
            return 10*(np.log10(x))
        
        #Drom unnamed unnecessary label
        clean=df_.drop(['Unnamed: 0'], axis=1)
        
        #Convert amplitudes to DB
        df_['VV amplitude (linear)'] = df_['VV amplitude (linear)'].apply(toDB)
        df_['VH amplitude (linear)'] = df_['VH amplitude (linear)'].apply(toDB)

        #Replace entropy nan values with the median 
        entropy =df_['Entropy'].values
        #Find indices that you need to replace
        inds_entropy = np.isnan(entropy)
        entropy[inds_entropy] = np.nanmedian(entropy)
        df_['Entropy'] = entropy

        #Replace Cross-pol correlation coefficient nan values with the median 
        Cross =df_['Cross-pol correlation coefficient'].values
        #Find indices that you need to replace
        inds_Cross = np.isnan(Cross)
        Cross[inds_Cross] = np.nanmedian(Cross)
        df_['Cross-pol correlation coefficient'] = Cross

        #Get the counter of labels with the clean dataset
        counter = collections.Counter(clean['label'])
        
        """CHANGE: START"""
        #Drop undefined pixels
        
        ### Modify according to the number of layer assigned to the undefined class
        ### in this case label#4 is the undefined class
        clean = clean.drop(clean[clean['label'] == 4].index)
        """CHANGE: END"""
        return clean,counter
    
    def sample(clean,path_data,counter):
        #Function that undersamples the data based on the min number of elements of the counter
        
        #Reset index
        clean.reset_index()
        
        """CHANGE: START"""
        #Get one dataframe per class
        ### Add the additional labels
        class_0 = clean[clean['label'] == 0]
        class_1 = clean[clean['label'] == 1]
        class_2 = clean[clean['label'] == 2]
        class_3 = clean[clean['label'] == 3]
        ##### class_4 = clean[clean['label'] == 4]
        ##### ...
        ##### class_n = clean[clean['label'] == n]

        #Drop the other labels
        ### Add the additional labels
        class_0=class_0.drop(['Railways','Water','Roads'], axis=1) #Buildings
        ### Modify each one of these adding the additional features to drop
        ##### class_0=class_0.drop(['Railways','Water','Roads',...,'label_n'], axis=1) #Buildings
        class_1=class_1.drop(['Buildings','Water','Roads'], axis=1) #Railways
        class_2=class_2.drop(['Railways','Buildings','Roads'], axis=1) #Water
        class_3=class_3.drop(['Railways','Water','Buildings'], axis=1) #Roads
        ### Add the other created dataframes for the layers
        ##### ...
        ##### class_n = class_n.drop(['Railways','Water','Buildings','Roads',...,label_n-1'], axis=1) #Roads
        
        #Sort by % of belonging to the class
        ### Add additional labels
        class_0 = class_0.sort_values(by=['Buildings'], ascending=False)
        class_1 = class_1.sort_values(by=['Railways'], ascending=False)
        class_2 = class_2.sort_values(by=['Water'], ascending=False)
        class_3 = class_3.sort_values(by=['Roads'], ascending=False)
        ##### ...
        ##### class_n = class_n.sort_values(by=['Label_n'], ascending=False)

        #Get minimum value
        min_ = min(counter.values())

        #Undersample each class
        ### Add the additional classes
        class_0_under = class_0.sample(min_)
        class_2_under = class_2.sample(min_)
        class_3_under = class_3.sample(min_)
        ##### ...
        ##### class_n_under = class_n.sample(min_)

        #Concatenate the classes and drop label layers
        
        ### Add the additional classes
        frames = [class_0_under,class_1,class_2_under,class_3_under]
        ##### frames = [class_0_under,class_1,class_2_under,class_3_under,...,class_n_under]
        result = pd.concat(frames)
        ### Add the additional classes
        result=result.drop(['Buildings','Railways','Water','Roads'], axis=1)
        ##### result=result.drop(['Buildings','Railways','Water','Roads',...,'label_n'], axis=1)
        """CHANGE: END"""
        
        result1 = result.sample(frac=1).reset_index(drop=True)
        result1.to_csv(path_data)

        return result1
