# This program computes a layer with the shortest path for each OD-pair
# An improvement would be to make a loop so that the algorithm is run for each purpose in one run

#Definition of inputs and outputs
#==================================
##Routing tools=group
##access=vector point
##amenities=vector point
##network=vector line
##distance=number 1600
##Routes=output vector line

#Algorithm body
#==================================
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from qgis.core import *
from qgis.gui import *
import time

LINEID = 'Distance'
POINTID1 = 'FromFID'
POINTID2 = 'ToFid'
FromToID='FromToFID'

import processing
#Layers that will be used in the algorithm: the network, all the points, the relations between them
network_url="/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Project Shapefiles/Full_network.shp"
points_url="/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Project Shapefiles/Destinations/Points_Services.gpkg|layername=Points_Services"
relations_url = "/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Project Shapefiles/ODServices.gpkg|layername=ODServices"
# creation of work layers
access_layer = iface.addVectorLayer(points_url,"Points","ogr")
amenities_layer = iface.addVectorLayer(points_url,"Points","ogr")
network_layer = iface.addVectorLayer(network_url,"Network","ogr")
relations_layer = iface.addVectorLayer(relations_url,"Relations","ogr")

# Skapa ett resultatslager (Från Astrids kod)
crs = network_layer.crs().toWkt()
outLayer = QgsVectorLayer('Linestring?crs='+ crs, 'connector_lines' , 'memory')
outdp = outLayer.dataProvider()

#add the two point ID field
outdp.addAttributes([QgsField(LINEID, QVariant.String),
                     QgsField(POINTID1, QVariant.String),
                     QgsField(POINTID2, QVariant.String),
                     QgsField(FromToID, QVariant.String)])
outLayer.updateFields()

distance = 50000
feedback = QgsProcessingFeedback()

## prepare graph
vl = network_layer
strategy = QgsNetworkDistanceStrategy ()
director = QgsVectorLayerDirector(vl, -1, '', '', '', QgsVectorLayerDirector.DirectionBoth)
director.addStrategy(strategy)
crs = vl.crs()
builder = QgsGraphBuilder( network_layer.crs() )

## prepare points
access_features = access_layer.getFeatures()
access_count = access_layer.featureCount()
amenities_features = amenities_layer.getFeatures()
amenities_count = amenities_layer.featureCount()
point_count = access_count + amenities_count
relations_count=relations_layer.featureCount()
points = []
ids = []

for f in access_features:
    points.append(f.geometry().asPoint())
    ids.append(f['U_ID'])
for f in amenities_features:
    points.append(f.geometry().asPoint())
    ids.append(f['U_ID'])

print("start graph build", datetime.now())
tiedPoints = director.makeGraph( builder, points )
graph = builder.graph()
print("end graph build", datetime.now())
time.sleep(3)
route_vertices = []


a=0
b=0

for feature in relations_layer .getFeatures():

    #count percentage done and no features
    a=a+1
    
    if a == 1:
        old_point_id=feature["destination_id"]
    
    #if a/15000==int(a/15000):
        #print (int((a/relations_count)*100),'%')

    
    point_id=feature["origin_id"]
    near_id=feature["destination_id"]
    
    from_point = tiedPoints[point_id]
    to_point = tiedPoints[near_id]
    from_id = graph.findVertex(from_point)
    to_id = graph.findVertex(to_point)
    if point_id != old_point_id:
        (tree,cost) = QgsGraphAnalyzer.dijkstra(graph,from_id,0)

    if tree[to_id] != -1 and (cost[to_id] <= distance or distance <= 0):
        costToPoint=cost [to_id]
        #print(costToPoint)
        route = [graph.vertex(to_id).point()]
        curPos = to_id 
        # Iterate the graph
        while curPos != from_id:
            curPos = graph.edge(tree[curPos]).fromVertex()
            route.insert(0, graph.vertex(curPos).point())
        connector = QgsFeature(outLayer.fields())
        connector.setGeometry(QgsGeometry.fromPolylineXY(route))
        #print(curPos, type(curPos))
                        
        res = connector.setAttribute(0,str(costToPoint))
        res = connector.setAttribute(1,str(feature["origin_id"]))
        res = connector.setAttribute(2,str(feature["destination_id"]))
        res = connector.setAttribute(3,str(feature["origin_id"])+ '-' +str(feature["destination_id"]))
        res = outdp.addFeatures([connector])

    old_point_id=point_id

QgsProject.instance().addMapLayer(outLayer)



print("end", datetime.now())