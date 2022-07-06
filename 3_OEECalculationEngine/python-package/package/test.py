import json
from typing import List
import pandas as pd
from manufacturingmetrics.oee import OEE
from dotenv import load_dotenv
load_dotenv() 

oee = OEE()
oeedf = oee.calculateOEE ("2022-07-04")
print(oeedf.head())

# import pkg_resources
# for d in pkg_resources.working_set:
#      print(d)

#configJson = json.loads('{ "oeeDate": "2022-06-19" }')