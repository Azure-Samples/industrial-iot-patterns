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

    def __getMESData(self, sqlDbConnectionString, oeeDate):
        oeeDate = "2022-06-30"  # overriding this as the the sample MES data is only available for this date
        productQualityQuery = f"""
            select 
                l.Id as PlantId, l.PlantName, l.UtcOffsetInHours, 
                a.Id as AssetId, a.AssetName,ag.NodeId, ag.StatusTagName, ag.UptimeTagValues, ag.DowntimeTagValues,
                s.Id as ShiftId, s.ShiftName, s.ShiftStartTime, s.ShiftEndTime,
                p.Id as ProductId, p.ProductName, p.IdealProductionUnitsPerMinute, pq.WorkOrder, pq.QuantityIn, pq.QuantityOut, pq.QuantityScraped
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

        with pyodbc.connect(sqlDbConnectionString) as conn:
            with conn.cursor() as cursor:
                qualitydf  = pd.read_sql(productQualityQuery, conn)
                downtimedf  = pd.read_sql(plannedDownTimeQuery, conn)
                return pd.merge(qualitydf, downtimedf, how="left",left_on = 'ShiftId', right_on = 'ShiftId')

    def __getMachineStatusData(self, kustodb, kustoConnectionString, oeeDate, mesdf):
        client = KustoClient(kustoConnectionString)

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
            queryResult = client.execute(kustodb, kustoQuery)    
            currentdf = dataframe_from_result_table(queryResult.primary_results[0])
            currentdf['ShiftId'] = row['ShiftId']
            currentdf['AssetId'] = row['AssetId']
            currentdf['TimeStatus'] = currentdf.apply(lambda x: 'UptimeMinutes' if x['MachineStatus'] in row['UptimeTagValues'] else 'DowntimeMinutes', axis=1)
            telemetrydf = telemetrydf.append(currentdf,ignore_index=True)

        telemetrydf = telemetrydf.groupby(['AssetId', 'ShiftId', 'TimeStatus'])['TotalDurationInMinutes'].sum().reset_index()
        telemetrydf = telemetrydf.pivot_table('TotalDurationInMinutes', ['AssetId', 'ShiftId'], 'TimeStatus')
        return telemetrydf

    def calculateOEE(self, oeeDate, sqlConnectionString, kustodb, kustoConnectionString):
        
        # Get MES Data and Calculate Quality
        mesdf = self.__getMESData(sqlConnectionString,oeeDate)
        mesdf["Quality"] = (mesdf["QuantityOut"] / (mesdf["QuantityOut"] + mesdf["QuantityScraped"]) ) * 100

        # Calculate Availability
        machinestatusdf = self.__getMachineStatusData(kustodb, kustoConnectionString, oeeDate, mesdf)
        oeedf = pd.merge(mesdf, machinestatusdf, how="left",left_on = ['ShiftId', 'AssetId'], right_on = ['ShiftId', 'AssetId'])
        oeedf['TotalProductionTimeInMinutes'] =  round((pd.to_datetime(oeedf['ShiftEndTime'],format='%H:%M:%S') -  pd.to_datetime(oeedf['ShiftStartTime'],format='%H:%M:%S')).dt.total_seconds() / 60)
        oeedf['PlannedProductionTimeInMinutes'] =  oeedf['TotalProductionTimeInMinutes'] - oeedf['PlannedDownTimeInMinutes']
        oeedf['Availability'] = ((oeedf['PlannedProductionTimeInMinutes'] - oeedf['DowntimeMinutes']) / oeedf['PlannedProductionTimeInMinutes']) * 100

        # Calculate Performance
        oeedf['CycleTimeInMinutes'] = (1 /  oeedf['IdealProductionUnitsPerMinute'])
        oeedf['Performance'] = (((oeedf['QuantityOut'] + oeedf['QuantityScraped']) *  oeedf['CycleTimeInMinutes']) / oeedf['PlannedProductionTimeInMinutes']) * 100

        # Calculate OEE
        oeedf['OEE'] =  ((oeedf['Availability']/100) * (oeedf['Performance']/100) * (oeedf['Quality']/100)) * 100

        # Calculate OEE Losses
        oeedf['AvailabilityLoss'] = ((oeedf['DowntimeMinutes'] / oeedf['CycleTimeInMinutes']) / ( oeedf['PlannedProductionTimeInMinutes'] / oeedf['CycleTimeInMinutes'])) * 100
        oeedf['QualityLoss'] = (oeedf['QuantityScraped'] / ( oeedf['PlannedProductionTimeInMinutes'] / oeedf['CycleTimeInMinutes'])) * 100
        oeedf['SpeedLoss'] = 100 - oeedf['AvailabilityLoss'] -  oeedf['QualityLoss'] - oeedf['OEE']

        return oeedf

    def saveOEE(self, oeedf, sqlConnectionString):
        with pyodbc.connect(sqlConnectionString) as conn:
            with conn.cursor() as cursor:
                for index, row in oeedf.iterrows():
                    insertQuery = f"""
                    INSERT INTO [dbo].[OEE]
                        ([PlantId],[AssetId],[ShiftId],[ProductId],[WorkOrder]
                        ,[TotalUnits],[GoodUnits],[ScrapedUnits],[Quality]
                        ,[PlannedDownTimeInMinutes],[DowntimeMinutes],[UptimeMinutes]
                        ,[TotalProductionTimeInMinutes],[PlannedProductionTimeInMinutes]
                        ,[Availability],[CycleTimeInMinutes],[Performance],[OEE]
                        ,[AvailabilityLoss],[QualityLoss],[SpeedLoss])
                    VALUES
                        ({row.PlantId},{row.AssetId},{row.ShiftId},{row.ProductId},'{row.WorkOrder}'
                        ,{row.QuantityIn},{row.QuantityOut},{row.QuantityScraped},{row.Quality}
                        ,{row.PlannedDownTimeInMinutes},{row.DowntimeMinutes},{row.UptimeMinutes}
                        ,{row.TotalProductionTimeInMinutes},{row.PlannedProductionTimeInMinutes}
                        ,{row.Availability},{row.CycleTimeInMinutes},{row.Performance},{row.OEE}
                        ,{row.AvailabilityLoss},{row.QualityLoss},{row.SpeedLoss})
                    """ 
                    #print(insertQuery)   
                    cursor.execute(insertQuery)
                    conn.commit()




