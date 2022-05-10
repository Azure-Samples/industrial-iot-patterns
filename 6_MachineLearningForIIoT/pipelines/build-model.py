import pandas as pd
import numpy as np
from azureml.core import Run, Workspace, Environment, Experiment
from azureml.core import Dataset, Datastore, Workspace
from azureml.core.model import Model
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report

import argparse
import time
import pandas as pd
import os
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("--modelname", type=str, required=True)
parser.add_argument("--selectedfeatures", type=str, required=True)
args, _ = parser.parse_known_args()

current_run = None
current_ws = None

trainDatasetName = "iiot-quality-train"
testDatasetName = "iiot-quality-test"
targetColumnName = "Quality"

modelName = args.modelname   #"iiot-quality-lgbm"
modelFileName = modelName + ".pkl"
features =  args.selectedfeatures.split(",")     #['S16','S20','S19','S18','S29','S41','S9','S10','S8','S11','S14','S13','S28','S15','S26','S33','S7','S3','S39']

def init():
    global current_run, current_ws
    print("init() is called.")
    current_run = Run.get_context()
    current_ws = current_run.experiment.workspace
    #current_ws = Workspace.from_config()

def buildmodel():
    print("buildmodel() is called.")

    # Get Datasets
    trainds = Dataset.get_by_name(current_ws,trainDatasetName)
    testds = Dataset.get_by_name(current_ws,testDatasetName)
    traindf = trainds.to_pandas_dataframe()
    testdf = testds.to_pandas_dataframe()

    print("Training rows => ",traindf.shape[0])
    print("Test rows => ",testdf.shape[0])

    # Train / Test datasets
    X_train = traindf[features]
    y_train = traindf[targetColumnName]

    X_test = testdf[features]
    y_test = testdf[targetColumnName]

    # Replace null values with "median" and normalize all numeric values using MinMaxScaler
    numeric_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', MinMaxScaler())])
    transformations = ColumnTransformer(transformers=[('num', numeric_transformer, X_train.columns)])

    # Build classifier pipeline with preprocessing steps as above, and LightGBM model
    # Only use training dataset for build the model
    classifierPipeline = Pipeline(steps=[('preprocessor', transformations),('classifier', LGBMClassifier())])
    model = classifierPipeline.fit(X_train, y_train)

    # Run the model and extract predictions
    y_pred = classifierPipeline.predict(X_test)

    # Score the model against true values
    trainingScore = classifierPipeline.score(X_train, y_train)
    testScore = classifierPipeline.score(X_test, y_test)
    print('Training set score: {:.4f}'.format(trainingScore))
    print('Test set score: {:.4f}'.format(testScore))
    print(classification_report(y_test, y_pred))

    current_run.log("training_accuracy",trainingScore)
    current_run.log("test_accuracy",testScore)

    # Save and Register Model
    pickle.dump(classifierPipeline, open(modelFileName, 'wb'))
    modeltags = { 
        "experiment": current_run.experiment.name,
        "run_id": current_run.id,
        "train_dataset_name" : trainds.name,
        "train_dataset_version" : trainds.version,
        "test_dataset_name" : testds.name,
        "test_dataset_version" : testds.version
    }
    model = Model.register(model_path=modelFileName, model_name=modelName, 
                           tags=modeltags, description="Light GBM model model for iiot quality prediction",workspace=current_ws)

    print("model built and registered")
    
init()
buildmodel()