import json
from typing import List
import pandas as pd
import os
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from manufacturingmetrics.oee import OEE
from dotenv import load_dotenv
load_dotenv() 

server = os.getenv("sql_server")
database = os.getenv("sql_db_name")
username = os.getenv("sql_username")
password = os.getenv("sql_password")
driver= '{ODBC Driver 17 for SQL Server}'
sqlConnectionString = 'DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password

aadTenantId = os.getenv("kusto_aad_tenant_id")
cluster = os.getenv("kusto_cluster_url")
appId = os.getenv("kusto_app_id")
appSecret = os.getenv("kusto_app_secret")
kustodb = os.getenv("kusto_db_name")
kustoConnectionString = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster,appId,appSecret,aadTenantId)

oeeDate = "2022-07-04"
oee = OEE()
oeedf = oee.calculateOEE (oeeDate,sqlConnectionString, kustodb, kustoConnectionString)
oee.saveOEE(oeeDate, oeedf, sqlConnectionString)
oeedf.to_csv("oeedf.csv")
print(oeedf.head())

# import pkg_resources
# for d in pkg_resources.working_set:
#      print(d)

#configJson = json.loads('{ "oeeDate": "2022-06-19" }')