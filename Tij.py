from PyQt5.QtCore import *
import math
import numpy as np
import pandas as pd
from datetime import datetime
import time
print(datetime.now())

# This program aims to compute the gravity model for destination choice probability and the mode choice functions

layer1 = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_P_shopping.shp","s_path_shop","ogr")
layer2 = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_p_services.shp","s_path_serv","ogr")
layer3 = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_p_touring.shp","s_path_tour","ogr")
layer4 = QgsVectorLayer("/Users/laurentcazor/Documents/Master Thesis/QGIS - Final/Full network/S_p_leisure.shp|layername=S_p_leisure","s_path_leis","ogr")

layers = [layer1, layer2, layer3, layer4]

def sigmoid(b0, b1, b2, b3, X):
    X = float(X)/30000
    try:
        S = 1/(1+math.exp(-(b0+b1*X+b2*X**2+b3*math.sqrt(X))))
    except OverflowError:
        S = 'inf'
    return S

# Gravity model distance-decay parameters

Beta = [-0.0833, -0.0833, -0.0351, -0.0351]


#Bike mode choice parameters
A_0_l = [-0.44391129463248735, 0.045421282463330465, -3.904112256228761, 0.5687733506577125]
A_1_l = [-8.295618349118543, -3.751848767649791, 0.3791578463667172, -0.9215795742380404]
A_2_l = [-2.0871942229142797, -1.6994613073684237, -1.940943420795848, 0.019770984624589937]
A_3_l = [1.5641575146847442, -2.4196921105723215, 5.526990391189266, -3.331767479111909]

#Ebike mode choice parameters
B_0_l = [-0.6498748953606043, -0.29797345841414963, -3.3602305317530834, -0.7290932553055972]
B_1_l = [-3.1822681067845404, -2.1398819794608994, 2.201028708826716, -1.4593795193621433]
B_2_l = [-0.976798293893275, -1.3330152115670482, -2.5280686380753137, -0.019578406245738936]
B_3_l = [0.04333028543699834, -1.5403262612251727, 4.310711954186476, -0.588298193854497]


for i in range (len(layers)):
    layer=layers[i]
    A_0 = A_0_l[i]
    A_1 = A_1_l[i]
    A_2 = A_2_l[i]
    A_3 = A_3_l[i]
    B_0 = B_0_l[i]
    B_1 = B_1_l[i]
    B_2 = B_2_l[i]
    B_3 = B_3_l[i]
    
    # Creation of a new field for each decay function
    layer_provider=layer.dataProvider()
    layer_provider.addAttributes([QgsField("exp",QVariant.Double, "float",8,3)])
    layer_provider.addAttributes([QgsField("Tij",QVariant.Double, "float",8,3)])
    layer_provider.addAttributes([QgsField("fbike",QVariant.Double, "float",8,3)])
    layer_provider.addAttributes([QgsField("febike",QVariant.Double, "float",8,3)])
    layer.updateFields()
    print (layer.fields().names())

    # Update the fields
    features = layer.getFeatures()
    
    
    
    for f in features:
        id = f.id()
        X = f['Distance']
        exp = math.exp(Beta[i]*float(X)/1000)
        att = {4:exp}
        layer_provider.changeAttributeValues({id:att})
        fbike = sigmoid(A_0, A_1, A_2, A_3, X)
        febike = sigmoid(B_0, B_1, B_2, B_3, X)
        attr_value={6:fbike}
        layer_provider.changeAttributeValues({id:attr_value})
        attr_value2={7:febike}
        layer_provider.changeAttributeValues({id:attr_value2})
    layer.commitChanges()
    
    for f in features:
        id = f.id()
        exp = f.attributes()[4]
        sum_exp = 0
        for g in features:
            exp_2 = g.attributes()[4]
            if (f['FromID'] == g['FromID']):
                sum_exp+=exp_2
        Tij = exp/sum_exp
        attr = {5:Tij}
        layer_provider.changeAttributeValues({id:attr})
    layer.commitChanges()

print(datetime.now())
        