from PyQt5.QtCore import *
import math

layer_work=QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_p_work.shp|layername=S_p_work","s_path_w","ogr")
layer_school = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_p_school.shp|layername=S_p_school","s_path_s","ogr")

layers = [layer_work, layer_school]

def sigmoid(b0, b1, b2, b3, X):
    X = float(X)/30000
    try:
        S = 1/(1+math.exp(-(b0+b1*X+b2*X**2+b3*math.sqrt(X))))
    except OverflowError:
        S = 'inf'
    return S


#Bike 
A_0=[0.5949151637706399,0.9115555869794606]
A_1=[-7.2431452984131885, -7.636374579701152]
A_2=[0.05740860644694539, -1.2157114090978611]
A_3=[-0.18442318504135605, 1.5517784148616156]

#Ebike
B_0=[0.07166876549536741, -0.7878218754292144]
B_1=[-2.3744188449615566, -0.961680067350114]
B_2=[-1.7157610670509382, -1.2542727587685056]
B_3=[-0.6012328640390996, -0.3794066253090387]



for i in range (len(layers)):
    layer = layers[i]
# Creation of a new field for each decay function
    layer_provider=layer.dataProvider()

    
    for k in range (5,10):
        layer_provider.deleteAttributes([k])
    layer.updateFields()
    layer_provider.addAttributes([QgsField("Tij_bike",QVariant.Double, "float",8,3)])
    layer_provider.addAttributes([QgsField("Tij_ebike",QVariant.Double, "float",8,3)])
    layer.updateFields()
    print (layer.fields().names())

# Update the fields
    features = layer.getFeatures()
    for f in features:
        id = f.id()
        Num = f.attributes()[4]
        X = f.attributes()[0]
        fbike = float(Num)*sigmoid(A_0[i], A_1[i], A_2[i], A_3[i], X)
        febike = float(Num)*sigmoid(B_0[i], B_1[i], B_2[i], B_3[i], X)
        attr_value={5:fbike}
        layer_provider.changeAttributeValues({id:attr_value})
        attr_value2={6:febike}
        layer_provider.changeAttributeValues({id:attr_value2})
    layer.commitChanges()

    