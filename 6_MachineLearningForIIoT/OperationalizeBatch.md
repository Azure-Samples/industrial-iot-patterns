# Operationalizing machine learning models with batch pipelines

Goal of this sample is to acceleratre deployment of [Industrial IoT Prediction Patterns](TODO). There is no one size fits all solution, as there are many [considerations](TODO), please review them before moving your workload to production.

In the previous step we used some of the [Exploratory Data Analysis](../5_ExplorationDataAnalysis/README.md) techniques to select initial features for model and also perform a baseline modeling to understand what algorithms may work well with our dataset. For this sample we will select an algorithm and build an end to end machine learning pipeline to a) train and register a new model and b) run the model on new data and store predictions for reporting. 

## High Level Design

![Operationalizing machine learning models with batch pipelines](../images/ml-ops-batch.png)

## Pre-requisites

- You have [Exploratory Data Analysis](../5_ExplorationDataAnalysis/README.md) working.

- Create an autoscaled compute cluster with system assigned identity

    - `az ml computetarget create amlcompute --name "cpu-cluster" --max-nodes 2 --vm-size "STANDARD_DS3_V2" --assign-identity '[system]' -w iiotml -g iiotsample`

- Assign Database permissions in Data Explorer to above created 'cpu-cluster' managed identity

    <img src="../images/ml-ops-1.png"  height="60%" width="60%">

- Go to the Notebooks section in Machine Learning Studio portal and upload the files from `pipelines` folder
    
    - <IMAGE here> 


## Building Model Training Pipeline

- Open and run [01-build-retrain-pipeline.ipynb](./pipelines/01-build-retrain-pipeline.ipynb) notebook and create a machine learning pipeline that:
    1. Builds and registers train and test datasets.
    2. Builds and registers a new model based on 
    the features provided as a parameter.

    <img src="../images/ml-model-train-1.png"  height="60%" width="60%">

    <img src="../images/ml-model-train-2.png"  height="60%" width="60%">

    <img src="../images/ml-model-train-3.png"  height="60%" width="60%">
    
## Building Model Prediction Pipeline

- Create a folder in the DataLake named `predictionresults`, associated with the Datastore

- Open and run [02-build-prediction-pipeline.ipynb](./pipelines/02-build-prediction-pipeline.ipynb) notebook and create prediction pipeline that:
    1. Gets the registered model 
    1. Gets the latest sensor data from data explorer
    1. Runs the model and saves the prediction results to data lake

    <img src="../images/ml-model-predict-1.png"  height="60%" width="60%">

    <img src="../images/ml-model-predict-2.png"  height="60%" width="60%">

    <img src="../images/ml-model-predict-3.png"  height="60%" width="60%">

- Create Synapse Workspace

- Create [Azure ML Linked Service](https://docs.microsoft.com/en-us/azure/synapse-analytics/machine-learning/quickstart-integrate-azure-machine-learning)

    - ...

## Integrating Model Prediction with Synapse Pipelines

- TODO

## Reporting Prediction Results

- TODO