import requests
import pickle
import os
import numpy as np
from datetime import datetime


def get_nitrogen_levels(lon, lat):
    """
    This function returns the mean nitrogen level of the soil in the given location
    The function takes two arguments:
        - lon: the longitude of the location
        - lat: the latitude of the location
    The function uses the soilgrids API to get the nitrogen level of the soil
    It returns Float Value which is nitrogen level in mg/kg
    """
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=nitrogen&depth=0-5cm&depth=0-30cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&depth=60-100cm&depth=100-200cm&value=Q0.5&value=Q0.05&value=Q0.95&value=mean"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
            
        layers = data["properties"]["layers"]            
        nitrogen_layer = None
        for layer in layers:
            if layer.get("name") == "nitrogen":
                nitrogen_layer = layer
                break
                
        if not nitrogen_layer or not nitrogen_layer.get("depths"):
            return None
            
        mean_nitrogen = 0
        count = 0
        for depth in nitrogen_layer["depths"]:
            if depth.get("values") and "mean" in depth["values"]:
                mean_nitrogen += depth["values"]["mean"]
                count += 1
                
        if count == 0:
            return None
            
        mean_nitrogen = mean_nitrogen / count
        return mean_nitrogen / 10  
        
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"Data processing error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

 
def get_soil_type(lon, lat):
    """
    This function returns the soil type of the soil in the given location
    The function takes two arguments:
        - lon: the longitude of the location
        - lat: the latitude of the location
    The function uses the soilgrids API to get the soil type of the soil
    It returns String Value which is soil type
    """
    url = f"https://rest.isric.org/soilgrids/v2.0/classification/query?lon={lon}&lat={lat}"


    response = requests.get(url)
    data = response.json()
    soilClass = data["wrb_class_name"]
    if(soilClass == "Vertisols" or soilClass == "Gleysols"):
        return "Clayey"
    elif(soilClass == "Arenosols" or soilClass == "Regosols"):
        return "Sandy"
    elif(soilClass == "Fluvisols" or soilClass == "Cambisols"):
        return "Loamy"
    elif(soilClass == "Nitisols" or soilClass == "Luvisols"):
        return "Red"
    elif(soilClass == "Phaeozems" or soilClass == "Black Sand Deposits"):
        return "Black"
    else:
        return "Other"
        
def get_phosphorus_levels(lon, lat):
    """
    This function returns the phosphorus level of the soil in the given location
    The function takes two arguments:
        - lon: the longitude of the location
        - lat: the latitude of the location
    The function uses the isda-africa API to get the phosphorus level of the soil
    It returns Float Value which is phosphorus level in mg/kg
    """
    url = (f"https://api.isda-africa.com/v1/soilproperty?key=AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4&lat={lat}&lon={lon}&property=phosphorous_extractable&depth=0-20")
    
    try:
        response = requests.get(url)
        data = response.json()
        return data["property"]["phosphorous_extractable"][0]["value"]["value"]
    except:
        return None

def get_potassium_levels(lon, lat):
    """
    This function returns the potassium level of the soil in the given location
    The function takes two arguments:
        - lon: the longitude of the location
        - lat: the latitude of the location
    The function uses the isda-africa API to get the potassium level of the soil
    It returns Float Value which is potassium level in g/kg
    """
    url = "https://api.isda-africa.com/v1/soilproperty?key=AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4&lat=31.2357&lon=30.0444&property=potassium_extractable&depth=0-20"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        
        
        potassium_data = data["property"]["potassium_extractable"]

            
        value = potassium_data[0]["value"]["value"]
        if value is None:
            return None
            
        return float(value)/ 10
        
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"Data processing error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def get_moisture_level(lon, lat):
    """
    This function returns the moisture level of the soil in the given location
    The function takes two arguments:
        - lon: the longitude of the location
        - lat: the latitude of the location
    The function uses the isda-africa API to get the moisture level of the soil
    It returns Float Value which is moisture level in %
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=soil_moisture_1_3cm&start_date={datetime.now().strftime('%Y-%m-%d')}&end_date={datetime.now().strftime('%Y-%m-%d')}"
    try:
        response = requests.get(url)
        data = response.json()
        mean_moisture = 0
        for item in data["hourly"]["soil_moisture_1_3cm"]:
            mean_moisture += item
        mean_moisture = mean_moisture / len(data["hourly"]["soil_moisture_1_3cm"])
        return mean_moisture * 100
    except:
        return None
        

def get_fertilizer_recommendation(Temperature,
                                  Humadity,
                                  Moisture,
                                  Soil_Type,
                                  Nitrogen,
                                  Phosphorus,
                                  Potassium):
    """
    This function returns the fertilizer recommendation for the given elements
    The function takes one argument:
        - Elements: a list of elements
    """
    if(Nitrogen == None and Soil_Type == "Other" and Potassium == None):
        return None
    
    try:
        with open("../SatellitorMLModel/Artifacts/fertilizer.pkl", "rb") as f:
            model = pickle.load(f)
            encode_ferti = pickle.load(f)
            encode_soil = pickle.load(f)
        
        soil_type = encode_soil.transform([Soil_Type])
        fertilizer = model.predict([[Temperature, Humadity, Moisture, soil_type[0], Nitrogen, Phosphorus, Potassium]])
        fertilizer = encode_ferti.inverse_transform(fertilizer)
        return fertilizer[0]
    except:
        return None


print(get_nitrogen_levels(30.0444,31.2357))