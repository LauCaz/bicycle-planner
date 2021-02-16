# This Python program ranks the different kinds of improvements by flow, according to VGU recommendations
# The output is a list of the different road IDs that have the highest flows for each kind of infrastructure
# A good improvement would be to create a separate layer for each selected IDs, which is done manually now

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from qgis.core import *
from qgis.gui import *

D = datetime.now()

layer = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Files/test_subdivisions/split_dissolved.shp")

request = QgsFeatureRequest()

# set order by flow (descending)
clause = QgsFeatureRequest.OrderByClause('Flow', ascending=False)
orderby = QgsFeatureRequest.OrderBy([clause])
request.setOrderBy(orderby)


for i in range(2,6):
    Distance = 0
    Links_ID = []
    Flows = []
    features = layer.getFeatures(request)
    for f in features:
        # Conditions: good infrastructure, and not inside actual infrastructure
        if (f['Infra_VGU'] == i) and (f['Infra']==0):
            Links_ID.append(f['ID'])
            Distance += f['Length']
            Flows += [f['Flow']]
        else:
            pass
        if Distance > 100000:
            break
    print("Distance_"+str(i), Distance)
    print("Links_"+str(i), Links_ID)
    print("Flows_"+str(i), Flows)
    
print(datetime.now()-D)


