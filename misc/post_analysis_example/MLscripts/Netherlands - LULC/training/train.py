import pandas as pd
import numpy as np
import keras

from sklearn.utils import shuffle
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn import preprocessing

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
import seaborn as sns
import matplotlib.pyplot as plt

import keras
from keras.callbacks import EarlyStopping

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import cohen_kappa_score


class Train():
    def read_data(path,features):
        """This class reads and prepares the data to be fed into the network"""
        
        # Read and clean data
        df_ = pd.read_csv(path, index_col=0)
        df_.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_ = df_.dropna()
        df_ = df_.reset_index()
        
        #Prepare input data
        X=df_.drop(['label','index'], axis=1)
        X2 = df_[features]

        #Normalize data
        scaler = preprocessing.MinMaxScaler()
        d = scaler.fit_transform(X2)
        scaled_X = pd.DataFrame(d, columns=X2.columns)

        #Convert input data to numpy array
        X = np.array(scaled_X)
        
        #Prepare target data
        Y=df_['label']

        # convert integers to dummy variables (i.e. one hot encoded) - categorical
        dummy_y = np_utils.to_categorical(Y)
        return X,dummy_y
    
    def model_arch(X):
        # build a model
        model_6 = Sequential()
        model_6.add(Dense(128, input_shape=(X.shape[1],), activation='relu')) # input shape is (features,)
        model_6.add(Dense(units=64, kernel_initializer='uniform', activation='tanh'))
        model_6.add(Dense(units=64, kernel_initializer='uniform', activation='tanh'))
        model_6.add(Dense(units=64, kernel_initializer='uniform', activation='tanh'))
        model_6.add(Dense(units=32, kernel_initializer='uniform', activation='tanh'))
        model_6.add(Dense(units=16, kernel_initializer='uniform', activation='tanh'))
        #model_6.add(Dropout(0.25))
        model_6.add(Dense(units=8, kernel_initializer='uniform', activation='tanh'))
        #model_6.add(Dropout(0.5))
        model_6.add(Dense(4, activation='softmax'))
        model_6.summary()

        # compile the model
        model_6.compile(optimizer='adam', 
                      loss='categorical_crossentropy', # this is different instead of binary_crossentropy (for regular classification)
                      metrics=['accuracy'])
        return model_6
    
    def fit_model(model_6,X,dummy_y,epochs,batch_size,model_path):
        #Train the model
        his = keras.callbacks.History()
        es = keras.callbacks.EarlyStopping(monitor='val_loss', 
                                           mode='min',
                                           restore_best_weights=True) # important - otherwise you just return the last weigths...
        mcp_save =keras.callbacks.ModelCheckpoint(model_path, save_best_only=True, monitor='accuracy', mode='max')

        # now we just update our model fit call
        history = model_6.fit(X,
                            dummy_y,
                            epochs=epochs, # you can set this to a big number!
                            batch_size=batch_size,
                            shuffle=True,
                            validation_split=0.2,
                            verbose=1,
                            callbacks=[mcp_save,his])
        return history
    
    def results(model_path,X,dummy_y):
        #Obtain model's results from training
        
        #Load model weights
        model_6 = keras.models.load_model(model_path)
        
        #Predict
        preds = model_6.predict(X) # see how the model did!
        print(preds[0]) # i'm spreading that prediction across three nodes and they sum to 1
        print(np.sum(preds[0])) # sum it up! Should be 1
        ## [9.9999988e-01 1.3509347e-07 6.7064638e-16]
        ## 1.0

        #Get confusion matrix
        print("Confusion matrix")
        matrix = confusion_matrix(dummy_y.argmax(axis=1), preds.argmax(axis=1))
        print(matrix)
        print("Classification report")
        # more detail on how well things were predicted
        print(classification_report(dummy_y.argmax(axis=1), preds.argmax(axis=1)))
        K = cohen_kappa_score(dummy_y.argmax(axis=1), preds.argmax(axis=1))
        print("Kappa coefficient")
        print(K)