import json
from typing import List
import pyodbc
import urllib
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import os

class OEE(): 

    def __init__(self):
        super().__init__()
        server = os.getenv("sql_server")
        database = os.getenv("sql_db_name")
        username = os.getenv("sql_username")
        password = os.getenv("sql_password")
        driver= '{ODBC Driver 17 for SQL Server}'
        self.connectionString = 'DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password

    def __getMESData(self,oeeDate):
        oeeDate = "2022-06-30"  # overriding this as the the sample MES data is only available for this date
        productQualityQuery = f"""
            select 
                l.Id as PlantId, l.PlantName, l.UtcOffsetInHours, 
                a.Id as AssetId, a.AssetName,ag.NodeId, ag.StatusTagName, ag.UptimeTagValues, ag.DowntimeTagValues,
                s.Id as ShiftId, s.ShiftName, s.ShiftStartTime, s.ShiftEndTime,
                p.ProductName, p.IdealProductionUnitsPerMinute, pq.WorkOrder, pq.QuantityIn, pq.QuantityOut, pq.QuantityScraped
            from 
                [Assets] as a, 
                Locations as l, 
                AssetTags as ag, 
                Shifts as s,
                Products as p,
                ProductQuality as pq
            where 
                a.PlantId = l.Id  and 
                ag.AssetId = a.Id and 
                pq.ShiftId = s.Id and
                pq.AssetId = a.Id and
                p.Id = pq.ProductId and
                pq.CreatedTimeStamp = '{oeeDate}'
            order by l.Id, a.Id
        """   
        plannedDownTimeQuery = f"""
            select 
                ShiftId, sum(PlannedDownTimeInMinutes) as PlannedDownTimeInMinutes
            from ShiftPlannedDownTime
            where CreatedTimeStamp = '{oeeDate}'
            group by ShiftId
        """

        with pyodbc.connect(self.connectionString) as conn:
            with conn.cursor() as cursor:
                qualitydf  = pd.read_sql(productQualityQuery, conn)
                downtimedf  = pd.read_sql(plannedDownTimeQuery, conn)
                return pd.merge(qualitydf, downtimedf, how="left",left_on = 'ShiftId', right_on = 'ShiftId')

    def __getMachineStatusData(self, oeeDate, mesdf):
        aadTenantId = os.getenv("kusto_aad_tenant_id")
        cluster = os.getenv("kusto_cluster_url")
        appId = os.getenv("kusto_app_id")
        appSecret = os.getenv("kusto_app_secret")
        db = os.getenv("kusto_db_name")
        client = KustoClient(KustoConnectionStringBuilder.with_aad_application_key_authentication
                            (cluster,appId,appSecret,aadTenantId))
        
        mesdf = mesdf.reset_index()
        telemetrydf = pd.DataFrame(columns = ['MachineStatus', 'TotalDurationInMinutes','ShiftId','AssetId'])
        for index, row in mesdf.iterrows():
            startDateTime = datetime.strptime(oeeDate + " " + row["ShiftStartTime"].strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S') + timedelta(hours=row['UtcOffsetInHours'])
            endDateTime = datetime.strptime(oeeDate + " " + row["ShiftEndTime"].strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S') + timedelta(hours=row['UtcOffsetInHours'])
            kustoQuery = f"""
                let _startTime = datetime({startDateTime.strftime('%Y-%m-%d %H:%M:%S')});
                let _endTime =  datetime({endDateTime.strftime('%Y-%m-%d %H:%M:%S')});
                telemetry
                | where ExpandedNodeId == "{row['StatusTagName']}"
                | where SourceTimestamp >= _startTime and SourceTimestamp  <= _endTime
                | order by SourceTimestamp asc
                | extend prevValue = prev(Value), prevTimestamp = prev(SourceTimestamp,1, _startTime)
                | where prevValue != todouble(Value)
                | project ExpandedNodeId, Value, prevTimestamp, SourceTimestamp
                | extend nextValue = next(Value),  nextTimestamp = next(prevTimestamp,1, _endTime)
                | where nextValue != todouble(Value)
                | project Duration = todouble(datetime_diff("second",nextTimestamp,prevTimestamp)), MachineStatus = tostring(Value)
                | summarize sum(Duration) by MachineStatus
                | project MachineStatus, TotalDurationInMinutes = round(sum_Duration / 60)
            """
            #print(kustoQuery)
            queryResult = client.execute(db, kustoQuery)    
            currentdf = dataframe_from_result_table(queryResult.primary_results[0])
            currentdf['ShiftId'] = row['ShiftId']
            currentdf['AssetId'] = row['AssetId']
            currentdf['TimeStatus'] = currentdf.apply(lambda x: 'UptimeMinutes' if x['MachineStatus'] in row['UptimeTagValues'] else 'DowntimeMinutes', axis=1)
            telemetrydf = telemetrydf.append(currentdf,ignore_index=True)

        telemetrydf = telemetrydf.groupby(['AssetId', 'ShiftId', 'TimeStatus'])['TotalDurationInMinutes'].sum().reset_index()
        telemetrydf = telemetrydf.pivot_table('TotalDurationInMinutes', ['AssetId', 'ShiftId'], 'TimeStatus')
        return telemetrydf

    def calculateOEE(self, oeeDate):
        
        # Get MES Data and Calculate Quality
        mesdf = self.__getMESData(oeeDate)
        mesdf["Quality"] = (mesdf["QuantityOut"] / (mesdf["QuantityOut"] + mesdf["QuantityScraped"]) ) * 100

        # Calculate Availability
        machinestatusdf = self.__getMachineStatusData(oeeDate, mesdf)
        oeedf = pd.merge(mesdf, machinestatusdf, how="left",left_on = ['ShiftId', 'AssetId'], right_on = ['ShiftId', 'AssetId'])
        oeedf['PotentialProductionTimeInMinutes'] =  round((pd.to_datetime(oeedf['ShiftEndTime'],format='%H:%M:%S') -  pd.to_datetime(oeedf['ShiftStartTime'],format='%H:%M:%S')).dt.total_seconds() / 60)
        oeedf.to_csv("oeedf.csv")

        # Calculate Performance


        # Calculate OEE


        return oeedf