:warning: In progress

# Overall Equipment Effectiveness(OEE) and KPI Calculation Engine

Goal of this sample is to acceleratre deployment of [Industrial IoT Transparency Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/iiot-patterns/iiot-transparency-patterns). There is no one size fits all solution, as there are many considerations, please review them before moving your workload to production.

## High Level Design

![Overall Equipment Effectiveness(OEE) and KPI Calculation Engine](../images/oee.png)

## Pre-requisites

- You have [Operational Visibility](../2_OperationalVisibility/README.md) sample working.

## Setup Sample MES Database

- Create a [Single SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/database/single-database-create-quickstart?view=azuresql&tabs=azure-portal)

    - Open `Networking` tab and make sure `Allow Azure services and resources to access this server`  is (checked)

- Run the [sqldb/mes.sql](sqldb/mes.sql) script to create the tables and sample data

## Setup Synapse Workspace

- Create a [Synapse Workspace](https://docs.microsoft.com/en-us/azure/synapse-analytics/quickstart-create-workspace) with default settings. 

- Create 2 [Linked Services](https://docs.microsoft.com/en-us/azure/data-factory/concepts-linked-services?tabs=data-factory) in Synapse Workspace connected to:

    1. [SQL Database](https://docs.microsoft.com/en-us/azure/data-factory/connector-azure-sql-database?tabs=data-factory#create-an-azure-sql-database-linked-service-using-ui) created above
    1. [Azure Data Explorer](https://docs.microsoft.com/en-us/azure/data-factory/connector-azure-data-explorer?tabs=data-factory#create-a-linked-service-to-azure-data-explorer-using-ui) created in the prerequisites.

- Upload new Workspace package [package/dist/manufacturingmetrics-0.1.0-py3-none-any.whl](package/dist/manufacturingmetrics-0.1.0-py3-none-any.whl)  

    <img src="../images/sparkpool-2.png"  height="60%" width="60%">

- Create a new Apache Spark Pool

    <img src="../images/sparkpool-1.png"  height="60%" width="60%">

- Upload the [package/requirements.txt](package/requirements.txt) file, select the workspace package created above and click `Apply`. Wait until the packages are deployed.

    <img src="../images/sparkpool-3.png"  height="60%" width="60%">

## Calculate OEE using Synapse Notebook

- Open `Develop` tab, click on `+` and Import the [notebook/CalculateOEE.ipynb](notebook/CalculateOEE.ipynb)

- Attach the notebook to the spark cluster created above.

- In first cell, update the values for `sqldbLinkedServiceName` and `kustolinkedServiceName` as created above

- In second cell, update the `oeeDate` to a date which has telemetry data in Data Explorer.

- Run both the cells

- Open SQL Database created above and verify the data in `OEE` table

## Visualize OEE in Power BI

- *In Progress...*

## Additional Resources 

- Build package
    - `cd package`
    - `pip install wheel setuptools`
    - `python setup.py bdist_wheel`
