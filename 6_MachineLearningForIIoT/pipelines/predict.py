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

from datetime import timedelta
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azureml.data.datapath import DataPath

import argparse
import time
import os
import pickle
import joblib
import json

parser = argparse.ArgumentParser()
parser.add_argument("--modelname", type=str, required=True)
parser.add_argument("--selectedfeatures", type=str, required=True)
parser.add_argument("--kustocluster", type=str, required=True)
parser.add_argument("--kustodb", type=str, required=True)
parser.add_argument("--kustoquery", type=str, required=True)
parser.add_argument("--resultdatastorename", type=str, required=True)
parser.add_argument("--resultfilename", type=str, required=True)
args, _ = parser.parse_known_args()

current_run = None
current_ws = None

modelName = args.modelname
features =  args.selectedfeatures.split(",")     #['S16','S20','S19','S18','S29','S41','S9','S10','S8','S11','S14','S13','S28','S15','S26','S33','S7','S3','S39']
resultfilename = args.resultfilename
resultdatastorename = args.resultdatastorename
query = args.kustoquery
cluster = args.kustocluster
db = args.kustodb

def init():
    global current_run, current_ws
    print("init() is called.")
    current_run = Run.get_context()
    current_ws = current_run.experiment.workspace
    #current_ws = Workspace.from_config()


def getDataFromKusto(q):
    kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster)
    client = KustoClient(kcsb)
    response = client.execute(db, q)
    return dataframe_from_result_table(response.primary_results[0])
    
def modelprediction():
    print("modelprediction() is called.")

    # Get Latest Model
    currentmodel = joblib.load(Model.get_model_path(modelName,_workspace=current_ws))

    # Get Latest Data for Prediction
    testdf = getDataFromKusto(query)
    print(testdf.head(5))

    # Predict Results
    predictionResults = currentmodel.predict(testdf[features])
    print(predictionResults)

    # Save Prediction Results
    resultdf = testdf[features]
    resultdf["Prediction"] = predictionResults
    resultdf["BatchNumber"] = testdf["BatchNumber"]
    resultdf["SourceTimestamp"] = pd.to_datetime(testdf["SourceTimestamp"].astype(int), unit="ms")

    resultsDirectoryName = "predictionresults"  # Make sure this matches with the directory name in the Data Lake
    data_folder = os.path.join(os.getcwd(), resultsDirectoryName)
    os.makedirs(data_folder, exist_ok=True)

    resultdf.to_csv("{0}/{1}".format(data_folder,resultfilename),index=False)

    resultsdatastore = Datastore.get(current_ws,resultdatastorename) 
    Dataset.File.upload_directory(src_dir=resultsDirectoryName, target=DataPath(resultsdatastore, "/{0}/".format(resultsDirectoryName)), pattern="*.csv", overwrite=True) 

    print("model prediction results saved")
    
init()
modelprediction()