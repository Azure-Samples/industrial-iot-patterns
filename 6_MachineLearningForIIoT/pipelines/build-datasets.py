from azureml.core import Run
from azureml.core import Dataset, Datastore, Workspace
from sklearn.model_selection import train_test_split

import argparse
import time
import pandas as pd
import os

from datetime import timedelta
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table

#parser = argparse.ArgumentParser()
#parser.add_argument("--name", required=True)
#args, _ = parser.parse_known_args()

current_run = None
current_ws = None
dataStoreName = "iiotmfgdatalakestore"
classColumnName = "Quality"

trainFileName = "/iiot-quality-train.csv"
testFileName = "/iiot-quality-test.csv"
validationFileName = "/iiot-quality-validation.csv"

trainDatasetName = "iiot-quality-train"
testDatasetName = "iiot-quality-test"

qualityDataFile = "qualitydata/batch-quality-data.csv"
cluster = "https://iiotmfgdev.westus2.kusto.windows.net"
db = "mfgdb"
query = "opcua_raw | where payload contains 'BatchNumber' and unixtime_milliseconds_todatetime(todouble(payload.SourceTimestamp)) between (datetime(2022-05-04T20:32:00.000Z).. datetime(2022-05-05T00:50:00.000Z)) | mv-apply payload on (extend key = tostring(bag_keys(payload)[0]) | extend value = payload[key] | summarize b = make_bag(pack(key, value)) ) | evaluate bag_unpack(b)"

def init():
    global current_run, current_ws
    print("init() is called.")
    current_run = Run.get_context()
    current_ws = current_run.experiment.workspace
    #current_ws = Workspace.from_config()

def getDataFromKusto():
    kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster)
    client = KustoClient(kcsb)
    response = client.execute(db, query)
    return dataframe_from_result_table(response.primary_results[0])

def buildTrainTestDatasets():
    print("buildTrainTestDatasets() is called.")
    
    # Get telemetry data from Data Explorer for model training
    telemetrydf = getDataFromKusto()
    telemetrydf["SourceTimestamp"] = pd.to_datetime(telemetrydf["SourceTimestamp"],unit='ms')
    print("Rows => {0}".format(telemetrydf.shape[0]))
    print("Columns => {0}".format(telemetrydf.shape[1]))
    telemetrydf.head(5)

    # Get quality data from data lake via data store
    iiotmfgdatalakestore = Datastore.get(current_ws,dataStoreName)
    qualitydf = Dataset.Tabular.from_delimited_files(path = [(iiotmfgdatalakestore, qualityDataFile)]).to_pandas_dataframe()
    print("Rows => {0}".format(qualitydf.shape[0]))
    print("Columns => {0}".format(qualitydf.shape[1]))
    qualitydf.head()

    # Join Telemetry and Quality Data
    traindf = pd.merge(telemetrydf,qualitydf, on='BatchNumber')
    print("Rows => {0}".format(traindf.shape[0]))
    print("Columns => {0}".format(traindf.shape[1]))
    traindf.head()

    # Upload the training datasets to data lake
    train,other = train_test_split(traindf, test_size=0.30, shuffle=True,stratify=traindf[classColumnName],random_state=100)
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    
    train.to_csv("{0}{1}".format(data_folder,trainFileName),index=False)
    test,val = train_test_split(other, test_size=0.50, shuffle=True,stratify=other[classColumnName],random_state=100)
    test.to_csv("{0}{1}".format(data_folder,testFileName),index=False)
    val.to_csv("{0}{1}".format(data_folder,validationFileName),index=False)

    iiotmfgdatalakestore.upload_files(files=["{0}{1}".format(data_folder,trainFileName)], overwrite=True)
    iiotmfgdatalakestore.upload_files(files=["{0}{1}".format(data_folder,testFileName)], overwrite=True)
    iiotmfgdatalakestore.upload_files(files=["{0}{1}".format(data_folder,validationFileName)], overwrite=True)

    train_dataset = Dataset.Tabular.from_delimited_files(path=[(iiotmfgdatalakestore, trainFileName)])
    test_dataset = Dataset.Tabular.from_delimited_files(path=[(iiotmfgdatalakestore, testFileName)])


    # Register the training and test datasets
    train_dataset = train_dataset.register(workspace=current_ws, name=trainDatasetName, 
                                           description="iiot quality training dataset",tags={"run_id": current_run.id},
                                           create_new_version=True)

    test_dataset = test_dataset.register(workspace=current_ws, name=testDatasetName, 
                                           description="iiot quality test dataset",tags={"run_id": current_run.id},
                                           create_new_version=True)

    print("train / test dataset updated.")
    
init()
buildTrainTestDatasets()