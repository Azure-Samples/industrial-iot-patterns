# Operational Visibility with Anomaly Detection and Root Cause Analysis

Goal of this sample is to acceleratre deployment of [Industrial IoT Visibility Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/iiot-patterns/iiot-visibility-patterns). There is no one size fits all solution, as there are many considerations, please review them before moving your workload to production.

Operational Visiblity enables manufacturers to gain insights & drive decision-making to improve quality and be more efficient and improve safety. There are many data sources including Historians, IIoT telemetry, Operational Systems like MES, ERP, etc. that are key for building a Visibility Control Tower. In this sample we will use the IIoT telemetry data gathered from our previous Connectivity Sample and try to understand trends via time series analysis, perform anomaly detection, root cause analysis and trigger alerts & actions based on anomalies.

## High Level Design

![Operational Visibility Sample](../images/operational-visibility-sample.png)

## Pre-requisites

- You have [Connectivity Deployment Sample](https://github.com/iotrockstars/iot-iiot/blob/main/1-Connectivity/README.md) working, or have your IIoT data in Data Explorer already.

- Add new `Status` tag in Kepware which changes every 15 min. Use the [LineSimulationDemo-2.json](./LineSimulationDemo-2.json) file to update the configuration.

- Add the `Status` tag in [opcconfig.json](./opcconfig.json) file as shown.

- Copy the update file to EFLOW VM and verify the update in PowerShell:

    - `Copy-EflowVMFile -fromFile "opcconfig.json" -toFile ~\opcconfig\opcconfig.json -pushFile`

    - `Connect-EflowVm`

    - `sudo iotedge logs OPCPublisher --tail 20`

## **Time Series Analysis**

*Analyzing telemetry data can provide insights such as monitoring service health, physical production processes, and usage trends. Data Explorer contains native support for creation, manipulation, and analysis of multiple time series.
For this sample we will build some queries to perform time series analysis and also build a near real-time dashboard to montior all our lines.*

- Open [TimeSeriesQueries.kql](./TimeSeriesQueries.kql) file in Data Explorer Web UI

- Plot Temperature Sensor for Line 1 with Seasonal, Trend, and Residual components.

    <img src="../images/ts-query1.png"  height="60%" width="60%">
    

- Plot Anomalies for Humidity Sensor on Line 1.

    <img src="../images/ts-query2.png"  height="60%" width="60%">

- In the Data Explorer Web UI, click on Dashboards > New Dashboard > Import Dashboard file and import the [iiot-operational-visibility-dashboard.json](./iiot-operational-visibility-dashboard.json) file.

    <img src="../images/adx-dashboard-1.png"  height="50%" width="50%">

- Click on the `IIoT Operational Visibility` dashboard

    <img src="../images/adx-dashboard-2.png"  height="60%" width="60%">

    <img src="../images/adx-dashboard-3.png"  height="60%" width="60%">

    <img src="../images/adx-dashboard-4.png"  height="60%" width="60%">

    <img src="../images/adx-dashboard-5.png"  height="60%" width="60%">

    <img src="../images/adx-dashboard-6.png"  height="60%" width="60%">

## **Anomaly Detection and Root Cause Analysis**

*Anomaly detection is the first step towards predicitve maintenance. It helps understand our baseline of what "normal" looks like, and detects values that are above or below the normal line. It depends on the process and sensor calibration but a simple approach could be to set a hard threshold to send alerts if the normal value goes above/below 2 or 3 standard deviations. This works well when in normal scenarios.*

*For more complex scenarios, which includes analyzing & correlating multiple sensor values, a better approach may be to use machine learning algorithms that can detect trends over a large corpus of data and extract correlations between mulitple variables simultaneously.*

*In this sample we will use Metrics Advisor service to setup anomaly detection using machine learning (smart detection), and see how we can perform some root cause analysis.*

**Setup Metrics Advisor**

- Create a new [Metrics Advisor resource using azure portal](https://docs.microsoft.com/en-us/azure/applied-ai-services/metrics-advisor/quickstarts/web-portal#prerequisites) in the same region as your Data Explorer.

- Sign in to the [Metrics Advisor Portal](https://metricsadvisor.azurewebsites.net/) and verify the access.

- Assign Databse permissions to Metrics Advisor using [Managed Identity](https://docs.microsoft.com/en-us/azure/applied-ai-services/metrics-advisor/data-feeds-from-different-sources#azure-data-explorer-kusto) of the Metrics Advisor resource. Assign Database permissions using Permissions > Add, and then select the Metrics Advisor name in the Principals list.

    <img src="../images/ma-db-permissions.png"  height="50%" width="50%">
    

- Create the connection string as: `Data Source=<Data Explorer Cluster URI>;Initial Catalog=<Database>`

**Data onboarding**

- Add data feed to fetch data every 1 min using the above connection string and below query:

    `telemetry | where SourceTimestamp >= datetime(@IntervalStart) and SourceTimestamp < datetime(@IntervalEnd) | summarize avg(todouble(Value)) by ExpandedNodeId, DataSetWriterID, bin(SourceTimestamp, 1m) | project SensorTag = replace_string(ExpandedNodeId,"nsu=KEPServerEX;s=Simulator.",""), SensorValue = avg_Value, SourceTimestamp`

    <img src="../images/ma-add-feed-1.png"  height="60%" width="60%">

- Click on `Load Data`, select the Dimension, Measure and Timestamp columns as show below and `Verify Schema`

    <img src="../images/ma-add-feed-2.png"  height="60%" width="60%">

- Keep the other defaults AS-IS, we don't need to setup automatic rollups as we have already done the 1 minute rollup in our data explorer query. And use Smart filling for missing points.

- Provide a data feed name `iiotmfgdevdb` and click `Submit`

    <img src="../images/ma-add-feed-3.png"  height="60%" width="60%">

 - Click on the Visit Data Feed button, it should redirect to the data feed progress page. You can also click on Data feeds in the left navigation menu to see this page.

    <img src="../images/ma-add-feed-4.png"  height="60%" width="60%">

    <img src="../images/ma-add-feed-5.png"  height="60%" width="60%">


**Anomaly detection**

- From the Data feed page, click on the `SensorValue` Metric name to setup anomaly configuration. 

- Click on `Choose Series` and select all the `Humidity` tags.

- For the Metric-level configuration, select `Hard threshold`, `Above`, `55` and click Save. The dashboard should immediately show the anomalies based on the threshold.

    <img src="../images/ma-anomaly-1.png"  height="60%" width="60%">

- From the image above you can see that `Line4.Humidity` has most number of anomalies in that date range.

- Click on the `Line4.Humidity` and we can drill down further to understand the details of the anomaly.

    <img src="../images/ma-anomaly-2.png"  height="60%" width="60%">

**Root Cause Analysis**

- Let the Metrics Advisor run for few minutes and then click on `Incident hub` to perform deeper analysis on each of the anomaly incident.

    <img src="../images/ma-anomaly-3.png"  height="60%" width="60%">

- Click on `Diagnose` for further drill down and cross dimension diagnostic drill down.

    <img src="../images/ma-anomaly-4.png"  height="60%" width="60%">

- Add/Remove relevant cross dimensions in the chart to perform root cause analysis.

    <img src="../images/ma-anomaly-5.png"  height="60%" width="60%">

## **Alerts & Business Actions**

**Create Logic App Workflow**

*For this sample we have created a simple workflow to send an email with the anomal details*

- Update values in [anomaly-alert-workflow.json](anomaly-alert-workflow.json) file

    - `Ocp-Apim-Subscription-Key` : Key from Metrics Advisor Resource in Azure Portal
    
    - `x-api-key` : API key from the Metrics Advisor Portal

    - `To` : Email address to send the Alert Email

    - Replace additional connector details if you're using another email connector than the Office 365 Outlook connector.

    - Replace the placeholder subscription values (00000000-0000-0000-0000-000000000000) for your connection identifiers (connectionId and id) under the connections parameter ($connections) with your own subscription values. Also replace the resource group name `iiotsample` with your resource group name in connectionId

- Deploy new [logic app workflow using Azure CLI](https://docs.microsoft.com/en-us/azure/logic-apps/sample-logic-apps-cli-script#prerequisites):

    - `az logic workflow create --resource-group "iiotsample" --location "westus2" --name "anomaly-alert-workflow" --definition "anomaly-alert-workflow.json"`

- Open the Workflow in Azure Portal and copy HTTP POST URL

    <img src="../images/alert-1.png"  height="60%" width="60%">

**Create Metrics Advisor Hook**

- Open [Metrics Advisor Portal](https://metricsadvisor.azurewebsites.net/hook-setting) and create a new hook as shown below. Use the workflow HTTP POST URL copied from above step

    <img src="../images/alert-2.png"  height="60%" width="60%">

**Create Metrics Advisor Alerts**

- In Metrics Advisor Portal, click on `Data feeds` > `SensorValue` (Metric name) and add new Alerting Configuration as show below:

    <img src="../images/alert-3.png"  height="60%" width="60%">

- Example Alert Email

    <img src="../images/alert-4.png"  height="60%" width="60%">

- Click the Alert count on the Incident hub to drill down on each Alert.

    <img src="../images/alert-5.png"  height="60%" width="60%">

    <img src="../images/alert-6.png"  height="60%" width="60%">

## **Integration with Data Lakehouse**

*[Data Lakehouse](https://techcommunity.microsoft.com/t5/azure-synapse-analytics-blog/the-data-lakehouse-the-data-warehouse-and-a-modern-data-platform/ba-p/2792337) is an emerging pattern in the data platform world. The key aspect is that traditional Data Lakes have now advanced and many of the capabilities can overlap with a traditional Data Warehouse. In lot of scenarios it is much more flexible to store the raw data in a Data Lake and use services like [Azure Synapse Analytics](https://docs.microsoft.com/en-us/azure/synapse-analytics/overview-what-is) to process and query that data using T-SQL.*

*There are multiple ways to push telemetry data from IoT Hub to a Data lake. For this sample we will use the built-in route available in IoT Hub to push the data in AVRO format to a Data Lake. We will use this data in later samples to build machine learning models.*

**Create Data Lake**

- Create a [Storage Account](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-cli#create-a-storage-account-1) with hierarchical namespace 

- `az storage account create --name iiotmfgdatalake --resource-group iiotsample --location westus2 --sku Standard_RAGRS --kind StorageV2 --enable-hierarchical-namespace true`

- `az storage fs create -n raw --account-name iiotmfgdatalake --auth-mode login`

**Create Message Routing in IoT Hub**

- `az iot hub identity assign --name iiotmfghub --resource-group iiotsample --system-assigned`

- Assign `Storage Blob Data Contributor` permissions on `raw` data lake container to `iiotmfghub` managed identity

    <img src="../images/iothub-access.png"  height="50%" width="50%">

- Add new [routing endpoint to Storage](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-d2c#azure-storage-as-a-routing-endpoint)

    <img src="../images/iothub-route-1.png"  height="70%" width="70%">

    <img src="../images/iothub-route-2.png"  height="60%" width="60%">

- Validate data in Data Lake

    <img src="../images/iothub-route-3.png"  height="75%" width="75%">

