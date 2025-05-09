from fastapi import FastAPI
import ee
import requests
import pickle
import psycopg2
import numpy as np
import requests
from bs4 import BeautifulSoup
import random
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Optional,Dict
import json
from constants.coordinates import province_coords
from constants.provinces import provinces
from constants.greenInfrastructure import green_infra_costs, high_ndvi_air, low_ndvi_air
from constants.news import news_sites, energy_sites
from constants.renewableEnergy import renewable_energy_projects_high_poverty, renewable_energy_projects_low_poverty
from models.AQI import calculate_aqi_ispu
from models.potentialScore import PotentialScoreCalculator
from utils.functions import convert_json_string_to_dict, remove_json_wrapper

app = FastAPI()
carbon_sites = "https://www.investing.com/commodities/carbon-emissions-historical-data"
headers = {'User-Agent': 'Mozilla/5.0'}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# try:
#     # ee.Initialize(project='davidsiddiii')
#     ee.Initialize(project='ee-kurniakharisma17')
# except Exception as e:
#     print("Error initializing Earth Engine:", str(e))

try:
    with open("poverty_model.pkl", "rb") as f:
        poverty_model = pickle.load(f)
except Exception as e:
    print("Error loading poverty model:", str(e))
    poverty_model = None

# try:
#     with open("pm25_ispu_model.dill", "rb") as f:
#         ispu_model= dill.load(f)
#         print("ISPU model loaded successfully")

# except Exception as e:
#     print("Error loading ISPU model:", str(e))
#     ispu_model = None

# try:
#     with open("potential_model.dill", "rb") as f:
#         potential_model= dill.load(f)
#         print("potential model loaded successfully")

# except Exception as e:
#     print("Error loading potential model:", str(e))
#     potential_model = None

with open('kota_coords.json', 'r') as json_file:
    district_coords = json.load(json_file)

with open('citiesList.json', 'r') as json_file:
    cityprovince_dict = json.load(json_file)

cities = []

for key, value in district_coords.items():
    lat, lon = eval(value) # This safely converts the string to a tuple
    district_coords[key] = (lat, lon)
    cities.append(key)


def get_db_connection():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def get_exchange_rate():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code == 200:
        return response.json().get("rates", {}).get("IDR", 16000)  
    return 16000


def scrape_news(sites):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for site in sites:
        try:
            response = requests.get(site, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles.extend([article.text.strip().lower() for article in soup.find_all('h2')])
        except Exception as e:
            print(f"Error scraping {site}: {e}")
    return articles if articles else ["No relevant news found"]

def get_category(title, mapping):
    title_lower = title.lower()
    for category, keywords in mapping.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    return random.choice(list(mapping.keys()))

# articles = scrape_news(news_sites)
# energy_articles = scrape_news(energy_sites)

def safe_float(value, default=0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert value '{value}' to float, using {default} instead")
        return default

from datetime import datetime, timedelta
import ee

def fetch_province_environmental_data():
    """
    Fetches environmental data for all provinces using province_coords dictionary.
    """
    features = []

    for province, (lat, lon) in province_coords.items():
        point = ee.Geometry.Point(lon, lat)
        feature = ee.Feature(point, {"province": province})
        features.append(feature)

    feature_collection = ee.FeatureCollection(features)

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=150)).strftime('%Y-%m-%d')

    # Preload all necessary image collections
    ndvi = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterDate(start_date, end_date).select("NDVI").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date).mean()
    
    soil_moisture = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select("VV") \
        .mean()

    no2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
        .filterDate(start_date, end_date).select("NO2_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    co = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CO") \
        .filterDate(start_date, end_date).select("CO_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    so2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_SO2") \
        .filterDate(start_date, end_date).select("SO2_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    pm25 = ee.ImageCollection("NASA/GEOS-CF/v1/rpl/htf") \
        .filterDate(start_date, end_date) \
        .select("PM25_RH35_GCC") \
        .map(lambda img: img.updateMask(img.gt(0))) \
        .mean()
    
    # O3 Collection from Sentinel-5P
    o3 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_O3") \
        .filterDate(start_date, end_date) \
        .select("O3_column_number_density") \
        .map(lambda img: img.updateMask(img.gt(0))) \
        .mean()

    def compute_stats(feature):
        geom = feature.geometry()
        buffer_radius = 10000  # 10km buffer for province level
        
        return feature.set({
            "ndvi": ndvi.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 250).get("NDVI"),
            "precipitation": precipitation.reduceRegion(ee.Reducer.mean(), geom, 500).get("precipitation"),
            "sentinel": soil_moisture.reduceRegion(ee.Reducer.mean(), geom, 500).get("VV"),
            "no2": no2.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("NO2_column_number_density"),
            "co": co.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("CO_column_number_density"),
            "so2": so2.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("SO2_column_number_density"),
            "pm25": pm25.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("PM25_RH35_GCC"),
            "o3": o3.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("O3_column_number_density"),
        })

    enriched = feature_collection.map(compute_stats)
    enriched_data = enriched.getInfo()

    result = {}
    for feature in enriched_data['features']:
        props = feature['properties']
        result[props['province']] = {
            "ndvi": round((props.get("ndvi", 0) or 0) * 0.0001, 2),
            "precipitation": round(props.get("precipitation", 0) or 0, 1),
            "sentinel": round(props.get("sentinel", 0) or 0, 3),
            "no2": round((props.get("no2", 0) or 0) * 1000000, 3),
            "co": round((props.get("co", 0) or 0) * 1000, 3),
            "so2": round((props.get("so2", 0) or 0) * 1000000, 3),
            "o3": round((props.get("o3", 0) or 0), 3),
            "aod": 0,
            "pm25": round(props.get("pm25", 0), 1)
        }

    return result


def fetch_district_environmental_data():
    """
    Fetches environmental data for all districts using district_coords dictionary.
    """
    features = []

    for district, (lat, lon) in district_coords.items():
        point = ee.Geometry.Point(lon, lat)
        feature = ee.Feature(point, {"district": district})
        features.append(feature)

    feature_collection = ee.FeatureCollection(features)

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=150)).strftime('%Y-%m-%d')

    # Preload all necessary image collections
    ndvi = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterDate(start_date, end_date).select("NDVI").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
        .filterDate(start_date, end_date).mean()
    
    soil_moisture = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select("VV") \
        .mean()

    no2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_NO2") \
        .filterDate(start_date, end_date).select("NO2_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    co = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CO") \
        .filterDate(start_date, end_date).select("CO_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    so2 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_SO2") \
        .filterDate(start_date, end_date).select("SO2_column_number_density").map(lambda img: img.updateMask(img.gt(0))).mean()
    
    pm25 = ee.ImageCollection("NASA/GEOS-CF/v1/rpl/htf") \
        .filterDate(start_date, end_date) \
        .select("PM25_RH35_GCC") \
        .map(lambda img: img.updateMask(img.gt(0))) \
        .mean()
    
    # O3 Collection from Sentinel-5P
    o3 = ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_O3") \
        .filterDate(start_date, end_date) \
        .select("O3_column_number_density") \
        .map(lambda img: img.updateMask(img.gt(0))) \
        .mean()

    def compute_stats(feature):
        geom = feature.geometry()
        buffer_radius = 5000  # 5km buffer for district level (smaller than province)
        
        return feature.set({
            "ndvi": ndvi.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 250).get("NDVI"),
            "precipitation": precipitation.reduceRegion(ee.Reducer.mean(), geom, 500).get("precipitation"),
            "sentinel": soil_moisture.reduceRegion(ee.Reducer.mean(), geom, 500).get("VV"),
            "no2": no2.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("NO2_column_number_density"),
            "co": co.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("CO_column_number_density"),
            "so2": so2.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("SO2_column_number_density"),
            "pm25": pm25.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("PM25_RH35_GCC"),
            "o3": o3.reduceRegion(ee.Reducer.mean(), geom.buffer(buffer_radius), 1000).get("O3_column_number_density"),
        })

    enriched = feature_collection.map(compute_stats)
    enriched_data = enriched.getInfo()

    result = {}
    for feature in enriched_data['features']:
        props = feature['properties']
        result[props['district']] = {
            "ndvi": round((props.get("ndvi", 0) or 0) * 0.0001, 2),
            "precipitation": round(props.get("precipitation", 0) or 0, 1),
            "sentinel": round(props.get("sentinel", 0) or 0, 3),
            "no2": round((props.get("no2", 0) or 0) * 1000000, 3),
            "co": round((props.get("co", 0) or 0) * 1000, 3),
            "so2": round((props.get("so2", 0) or 0) * 1000000, 3),
            "o3": round((props.get("o3", 0) or 0), 3),
            "aod": 0,
            "pm25": round(props.get("pm25", 0), 1)
        }

    return result


def fetch_all_environmental_data():
    """
    Fetches environmental data for all provinces and districts.
    """
    province_data = fetch_province_environmental_data()
    district_data = fetch_district_environmental_data()

    combined_data = {**province_data, **district_data}
    
    
    unique_data = {k: combined_data[k] for k in set(combined_data.keys())}

    return unique_data

def fetch_geospatial_data():
    end_date = ee.Date("2024-01-01")
    start_date = end_date.advance(-60, "day")

    # Fetch and cache the averaged images
    viirs_image = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")\
        .filterDate(start_date, end_date)\
        .select("avg_rad")\
        .mean()

    solar_image = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")\
        .filterDate(start_date, end_date)\
        .select("surface_solar_radiation_downwards_sum")\
        .mean()

    results = {}

    for province, (lat, lon) in province_coords.items():
        try:
            point = ee.Geometry.Point(lon, lat).buffer(5000)
            buffered_point = point.buffer(1000)

            night_lights_result = viirs_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffered_point,
                scale=500,
                bestEffort=True
            ).getInfo()

            solar_result = solar_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffered_point,
                scale=1000,
                bestEffort=True
            ).getInfo()

            night_lights = night_lights_result.get("avg_rad", 0.0) or 0.0
            daylight = solar_result.get("surface_solar_radiation_downwards_sum", 0.0) or 0.0

            results[province] = {
                "night_lights": float(night_lights),
                "daylight": float(daylight)
            }

        except Exception as e:
            print(f"Error fetching data for {province}: {str(e)}")
            results[province] = {
                "night_lights": 0.0,
                "daylight": 0.0
            }

    return results

def predict_poverty_index(province, geospatial_data):
    if poverty_model is None:
        return "Model not available"

    if province not in geospatial_data:
        return "Province data not available"

    try:
        data = geospatial_data[province]
        night_lights = data.get("night_lights", 0.0)
        daylight_duration = data.get("daylight", 0.0)

        features = np.array([[night_lights, daylight_duration]])
        predicted_poverty = poverty_model.predict(features)[0]

        return round(predicted_poverty, 2)

    except Exception as e:
        print(f"Error predicting poverty index for {province}: {str(e)}")
        return 0.0
    
def check_air_quality(co2, so2, no2, precipitation, sentinel, ndvi):
    # Define air quality thresholds (just as an example, adjust these as needed)
    if co2 < 25 and so2 < 35 and no2 < 50 and precipitation > 10 and sentinel > -6.8 and ndvi > 0.5:  # Good air quality
        return "Good"
    elif co2 > 25 and so2 > 35 and no2 > 50 and precipitation < 10 and sentinel < -6.8 and ndvi < 0.5:  # Bad air quality
        return "Bad"
    else:  # Moderate air quality
        return "Moderate"

def get_project(ndvi, co2, so2, no2, precipitation, sentinel, poverty_index):
    air_quality = check_air_quality(co2, so2, no2, precipitation, sentinel, ndvi)  # Check air quality based on pollutants
    
    selected = {}
    
    if (ndvi > 0.5 and air_quality == "Good"):
        selected['green_project'] = random.choice(high_ndvi_air)
    else:
        selected['green_project'] = random.choice(low_ndvi_air)
    if poverty_index < 10:  # High poverty index
        selected['renewable'] = random.choice(renewable_energy_projects_low_poverty)
    else:
        selected['renewable'] = random.choice(renewable_energy_projects_high_poverty)
    
    return selected

def calculate_environmental_score(env_data: Dict) -> float:
    """
    Calculate environmental score based on NDVI, precipitation, and soil moisture.
    
    Parameters:
    env_data (Dict): Dictionary containing environmental metrics
    
    Returns:
    float: Environmental score between 0-100
    """
    if "error" in env_data:
        return 50.0  
    ndvi_score = min(100, max(0, env_data.get("ndvi", 0) * 100))
    
    precip = env_data.get("precipitation", 0)
    if precip < 50:
        precip_score = (precip / 50) * 100
    elif precip > 200:
        precip_score = max(0, 100 - ((precip - 200) / 100) * 50)
    else:
        precip_score = 100
    
    sentinel = env_data.get("sentinel", -10)
    if sentinel < -20:
        soil_score = 0
    elif sentinel > 0:
        soil_score = 100
    else:
        soil_score = ((sentinel + 20) / 20) * 100
    
    weights = {"ndvi": 0.5, "precipitation": 0.3, "soil": 0.2}
    environmental_score = (
        weights["ndvi"] * ndvi_score +
        weights["precipitation"] * precip_score +
        weights["soil"] * soil_score
    )
    
    return round(environmental_score, 1)

def calculate_so2_aqi(so2_ppb):
    breakpoints = [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 804, 301, 400),
        (805, 1004, 401, 500),
    ]
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= so2_ppb <= bp_high:
            return round(((aqi_high - aqi_low) / (bp_high - bp_low)) * (so2_ppb - bp_low) + aqi_low)
    return None  # Out of range

def insight_greenproject(result):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    cityName = result.get("province")
    

    input_text_green_project = f"""Provide a response ONLY in JSON format. DO NOT add explanatory text, introduction, or conclusion before or after the JSON.
    1.⁠ ⁠tentukan keahlian SDM dari {cityName}, berikan 1 jawaban teratas. tanpa penjelasan. 

2.⁠ ⁠⁠tentukan 1 SDA dari {cityName} tanpa penjelasan

3.⁠ ⁠⁠tentukan 1  green project dengan return lama:

Gabungkan dengan data sumber Daya alam ini. dan tentukan Green Project yang sesuai berdasarkan SDA + keahlian SDM diatas. dalam bahasa inggris. 

{result}

buat dalam bentuk json seperti ini
region, top_human_resource_skill, top_natural_resource, green_project : name, justification, short_terms_jobs: [ {"title", "description"}], environmental_impact
"""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": input_text_green_project}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        generated_text = remove_json_wrapper(generated_text)
        generated_text = convert_json_string_to_dict(generated_text)
        return generated_text
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return "An error occurred."


def insight_credit(description, product_name, roi_value, price_value):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    input_text = f"""Create a 30-word investment funding to Green MSME’s, with  insight using these variables:

- Description: {description}
- Products: {product_name}
- ROI: {roi_value}%
- Price per unit: Rp {price_value}

Make it persuasive and clear. Use English language.
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": input_text}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        return generated_text
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return "An error occurred."


def generate_insights(aqi_score, location, carbon_absorbed, project_name):
    api_key = "AIzaSyD31L9QSRDJDhehutVdhmDrsdVidr-uhLQ"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    input_text = f"""Buatkan ringkasan singkat dalam bentuk narasi analisis lingkungan berdasarkan 4 variabel berikut:
- Nilai AQI: {aqi_score}
- Lokasi: {location}
- Penyerapan karbon oleh proyek: {carbon_absorbed} ton/tahun
- Nama proyek: {project_name}

Gunakan gaya bahasa profesional dan meyakinkan, serta akhiri dengan kesimpulan apakah proyek layak didanai dan potensial untuk carbon credit. Panjang output sekitar 50 kata.
GUNAKAN BAHASA INGGRIS
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": input_text}
                ]
            }
        ]   
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        return generated_text
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return "An error occurred."

def calculate_investment_score(env_data: Dict, poverty_index: float, infrastructure: str) -> Dict:
    """
    Calculate AI investment score based on environmental data, poverty index, and infrastructure costs.
    
    Parameters:
    env_data (Dict): Environmental data dictionary
    poverty_index (float): Poverty index value
    infrastructure (str): Type of green infrastructure
    
    Returns:
    Dict: Dictionary containing scores and breakdown
    """
    if isinstance(poverty_index, str):
        poverty_index = 50.0  
    env_score = calculate_environmental_score(env_data)
    
    poverty_score = min(100, max(0, poverty_index))
    
    max_cost = max(green_infra_costs.values())
    infra_cost = green_infra_costs.get(infrastructure, max_cost/2)
    cost_factor = (1 - (infra_cost / max_cost)) * 100
    
    weights = {"environmental": 0.4, "poverty": 0.4, "cost": 0.2}
    
    investment_score = (
        weights["environmental"] * env_score +
        weights["poverty"] * poverty_score +
        weights["cost"] * cost_factor
    )
    
    category = "Very Low"
    if investment_score >= 80:
        category = "Very High"
    elif investment_score >= 65:
        category = "High"
    elif investment_score >= 50:
        category = "Medium"
    elif investment_score >= 35:
        category = "Low"
    
    return round(investment_score, 1)

@app.get("/get-pm25")
def get_pm25():
    try:
        # Hardcoded Jakarta Selatan coordinates
        lat, lon = -6.2667,106.8000
        point = ee.Geometry.Point(lon, lat)

        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=150)).strftime('%Y-%m-%d')

        pm25 = ee.ImageCollection("NASA/GEOS-CF/v1/rpl/htf") \
                .filterDate(start_date, end_date) \
                .select("PM25_RH35_GCC") \
                .map(lambda img: img.updateMask(img.gt(0))) \
                .mean() \
                
        
        pm25_value = pm25.reduceRegion(ee.Reducer.mean(), point.buffer(10000),1000)
        pm25_value = pm25_value.getInfo().get("PM25_RH35_GCC", 0.0)
        
        return {
            "province": "Surabaya",
            "pm25_ug_per_m3": pm25_value,
        }

    except Exception as e:
        return {"error": f"Failed to retrieve PM2.5: {str(e)}"}
    
@app.get("/get-infrastructure-detail")
def get_infrastructure_detail():
    try:
        data_coords = {}
        period = datetime.now().strftime("%Y-%m-%d")
        geospatial_dict = fetch_geospatial_data()
        
        environmental_data = fetch_all_environmental_data()
       
        for province, datas in environmental_data.items():
            poverty_index = predict_poverty_index(province, geospatial_dict)
            

            try:
                ndvi = float(datas.get("ndvi", 0))
            except (ValueError, TypeError):
                ndvi = 0.0
                
            try:
                co = float(datas.get("co", 0))
            except (ValueError, TypeError):
                co = 0.0
                
            try:
                so2 = float(datas.get("so2", 0))
            except (ValueError, TypeError):
                so2 = 0.0
                
            try:
                no2 = float(datas.get("no2", 0))
            except (ValueError, TypeError):
                no2 = 0.0
                
            try:
                precipitation = float(datas.get("precipitation", 0))
            except (ValueError, TypeError):
                precipitation = 0.0
                
            try:
                sentinel = float(datas.get("sentinel", 0))
            except (ValueError, TypeError):
                sentinel = 0.0
                
            try:
                o3 = float(datas.get("o3", 0))
            except (ValueError, TypeError):
                o3 = 0.0
                
            try:
                pm25 = float(datas.get("pm25", 0))
            except (ValueError, TypeError):
                pm25 = 0.0
            
            safe_poverty_index = 9.0
            if poverty_index is not None and not isinstance(poverty_index, str):
                try:
                    safe_poverty_index = float(poverty_index)
                except (ValueError, TypeError):
                    pass  
            projects = get_project(
                ndvi, co, so2, no2, precipitation, sentinel, safe_poverty_index
            )

            infrastructure = projects.get('green_project') or "Not Available"
            renewable_energy = projects.get('renewable') or "Not Available"

           
            investment_score = calculate_investment_score(
                datas, 
                safe_poverty_index,
                infrastructure
            )

            try:
                aqi_values = calculate_aqi_ispu(pm25)
            except Exception:
                aqi_values = 0 
 
 
            data_coords[province] = {
                "province": province,
                "infrastructure": infrastructure,
                "renewable_energy": renewable_energy,
                "poverty_index": safe_poverty_index,
                "ndvi": ndvi,
                "precipitation": precipitation,
                "sentinel": sentinel,
                "no2": no2,
                "co": co,
                "so2": so2,
                "o3": o3,
                "pm25": pm25,
                "ai_investment_score": float(investment_score),
                "period": period,
                "level": 'province',
                "aqi": aqi_values
            }

        conn = get_db_connection()
        cur = conn.cursor()

        data_list = []
        for province, data in data_coords.items():
            data_list.append((
                data["province"],
                data["infrastructure"],
                data["renewable_energy"],
                data["poverty_index"],
                data["ndvi"],
                data["precipitation"],
                data["sentinel"],
                data["no2"],
                data["co"],
                data["so2"],
                data["o3"],
                data["pm25"],
                data["ai_investment_score"],
                data["period"],
                data["level"],
                data["aqi"]
            ))

        # Execute the batch insert function with the list of composite values
        cur.execute("SELECT insert_infrastructure_data_batch(%s::infrastructure_input[])", (data_list,))
        conn.commit()
        
        return {"status": "Success", "data_count": len(data_list)}
        
    except Exception as ex:
        print("Error inserting data into Database:", ex)
        return {"error": "An error occurred while processing the request: " + str(ex)}

@app.get("/get-city-score/{provinceName}")
def get_city_score(provinceName : str = None):
    if provinceName is None:
        return {"error": "Province name is required"}
    provinceName = provinceName.lower()
    list_cities = set()

    for entry in cityprovince_dict:
        if provinceName in entry:
            list_cities = set(entry[provinceName])
            break

    formatted_cities = ', '.join(f"'{city}'" for city in list_cities)
    
    query = f"SELECT * FROM infrastructure WHERE province IN ({formatted_cities})"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()    
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    
    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            row_dict[key] = value
        result.append(row_dict)


    for i in range(len(result)):
        potential_score = PotentialScoreCalculator.generate_potential_score(
            result[i]['pm25'],
            result[i]['aqi'],
            result[i]['so2'],
            result[i]['no2'],
            result[i]['co'],
            result[i]['o3'],
            result[i]['ndvi'],
            result[i]['sentinel'],
            result[i]['poverty_index']
        ) 
        
        result[i]['ai_investment_score'] = potential_score

    return result

@app.get("/green-credit/")
@app.get("/green-credit/{id_greencredit}")
def get_green_credit(id_greencredit: Optional[int] = None):
    query = "SELECT * FROM green_credit WHERE id = %s" if id_greencredit else "SELECT * FROM green_credit"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (id_greencredit,) if id_greencredit else None)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            row_dict[key] = value
        result.append(row_dict)

    if id_greencredit is not None:
        order_query = f"SELECT * FROM order_book_credit WHERE green_credit_id  = %s"
        cursor.execute(order_query, (id_greencredit,))
        periodic_rows = cursor.fetchall()


        result[0]['order_book'] = periodic_rows
        result[0]['insights'] = insight_credit(
            result[0]['description'],
            result[0]['products'],
            result[0]['roi'],
            result[0]['per_unit_price']
        )
    conn.close()
    
    return result

def generate_aqi_insights(province,co,no,so,infrastructure,renewable_energy):
    api_key = "AIzaSyD31L9QSRDJDhehutVdhmDrsdVidr-uhLQ"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    input_text = f"""
    Please make a statment like why is this data CO2 : {co}, NO2: {no}, SO2 : {so}, is good for {infrastructure} and {renewable_energy} project
    in {province}.
    
    Output Format : "Based on satellite data and AI predictions, the air quality in South Tangerang City falls into the "poor" category. Tree planting in Bintaro Park can be a solution to improve air quality, as the presence of trees helps absorb pollutants. Air quality assessments and the Normalized Difference Vegetation Index (NDVI) indicate that this area has strong potential for a tree-planting project.
    
    Please note that you have to follow the format correctly.

"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": input_text}
                ]
            }
        ]   
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return generated_text
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return "An error occurred."


@app.get("/green-bond/")
@app.get("/green-bond/{id_greenbond}")
def get_greenbond(id_greenbond: Optional[int] = None):
    query = f"select*from get_green_bond_details({id_greenbond})"
    if( id_greenbond is None):
        query = "SELECT * FROM get_green_bond_details()"
        
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            row_dict[key] = value
        result.append(row_dict)
    
    if id_greenbond is not None:
        province = result[0]['province']
        periodic_query = f"SELECT period, ndvi FROM infrastructure WHERE province = %s ORDER BY period"
        cursor.execute(periodic_query, (province,))
        periodic_rows = cursor.fetchall()

        ndvi_periodic = {}
        province = result[0]['province']
        periodic_query = """
            SELECT period, ndvi, infrastructure, renewable_energy
            FROM infrastructure
            WHERE province = %s
            ORDER BY period
        """
        cursor.execute(periodic_query, (province,))
        periodic_rows = cursor.fetchall()

        if periodic_rows:
            _, _, infrastructure, renewable_energy = periodic_rows[0]
        else:
            infrastructure = renewable_energy = None

        ndvi_periodic = {}
        for period, ndvi, *_ in periodic_rows:
            ndvi_periodic[str(period)] = ndvi


        result[0]['ndvi'] = ndvi_periodic
        result[0]['insights'] = generate_insights(
            result[0]['aqi'],
            result[0]['location'],
            result[0]['carbonabsorbed'],
            result[0]['name'])
        result[0]['general_insights'] = generate_aqi_insights(
            province,result[0]['aqi']['variable']['co'],
            result[0]['aqi']['variable']['no2'],
            result[0]['aqi']['variable']['so2'],
            infrastructure,renewable_energy
        )
    
    conn.close()
    
    
    return result

@app.get('/get-city-detail')
def get_city_detail(provinceName: str = None):
    query = f"SELECT * FROM infrastructure WHERE level = 'city' AND province = '{provinceName}'"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            row_dict[key] = value
        result.append(row_dict)
    

    for i in range(len(result)):
        potential_score = PotentialScoreCalculator.generate_potential_score(
            result[i]['pm25'],
            result[i]['aqi'],
            result[i]['so2'],
            result[i]['no2'],
            result[i]['co'],
            result[i]['o3'],
            result[i]['ndvi'],
            result[i]['sentinel'],
            result[i]['poverty_index']
        ) 
        
        result[i]['ai_investment_score'] = potential_score
    
    generateInsight = insight_greenproject(result[0])
    
    result[0]['details'] = generateInsight

    return result

@app.get("/get-top-five")
def get_top_five():
    query = "SELECT * FROM infrastructure WHERE level = 'city' order by ai_investment_score desc limit 5"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)    
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            if key != 'period':
                row_dict[key] = value
        result.append(row_dict)
    
    print(result)

    for i in range(len(result)):
        potential_score = PotentialScoreCalculator.generate_potential_score(
            result[i]['pm25'],
            result[i]['aqi'],
            result[i]['so2'],
            result[i]['no2'],
            result[i]['co'],
            result[i]['o3'],
            result[i]['ndvi'],
            result[i]['sentinel'],
            result[i]['poverty_index']
        ) 
        
        result[i]['ai_investment_score'] = potential_score

    
    return result

@app.get("/get-all-infrastructure")
def get_all_infrastructure():
    query = "SELECT * FROM infrastructure"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = {}
            for key, value in zip(columns, row):
                if key != 'period':  # Excluding period field as in your example
                    row_dict[key] = value
            result.append(row_dict)
            
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/get-infrastructure/all-province")
def get_infrastructure_province(province: str = None):
    query = "SELECT * FROM infrastructure WHERE level = 'province'"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (province,))    
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            if key != 'period':
                row_dict[key] = value
        result.append(row_dict)
    
    for i in range(len(result)):
        potential_score = PotentialScoreCalculator.generate_potential_score(
            result[i]['pm25'],
            result[i]['aqi'],
            result[i]['so2'],
            result[i]['no2'],
            result[i]['co'],
            result[i]['o3'],
            result[i]['ndvi'],
            result[i]['sentinel'],
            result[i]['poverty_index']
        ) 
        result[i]['ai_investment_score'] = potential_score


    return result
        
@app.get("/get-infrastructure/all-cities")
def get_infrastructure_province(province: str = None):
    query = "SELECT * FROM infrastructure WHERE level = 'city'"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (province,))    
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            if key != 'period':
                row_dict[key] = value
        result.append(row_dict)
    
    
    for i in range(len(result)):
        potential_score = PotentialScoreCalculator.generate_potential_score(
            result[i]['pm25'],
            result[i]['aqi'],
            result[i]['so2'],
            result[i]['no2'],
            result[i]['co'],
            result[i]['o3'],
            result[i]['ndvi'],
            result[i]['sentinel'],
            result[i]['poverty_index']
        ) 
        
        result[i]['ai_investment_score'] = potential_score

    return result
        
def generate_distribution(min_val, max_val, step=0.8):
    """
    Menghasilkan distribusi interval berdasarkan rentang dan langkah.
    """
    distribution = []
    current = min_val
    while current < max_val:
        upper = min(current + step, max_val)
        distribution.append((round(current, 2), round(upper, 2)))
        current += step
    return distribution

def count_distribution(data, min_val, max_val, step=0.8):
    """
    Menghitung frekuensi data dalam distribusi interval.
    """
    # Generate interval distribusi
    intervals = generate_distribution(min_val, max_val, step)
    
    # Inisialisasi list frekuensi untuk setiap interval
    freq = [0] * len(intervals)
    
    # Memasukkan nilai data ke dalam interval yang sesuai
    for value in data:
        for i, (lower, upper) in enumerate(intervals):
            # Menentukan interval berdasarkan value
            if lower <= value < upper:
                freq[i] += 1
                break
    
    return intervals, freq


@app.get("/get-infrastructure/{province}")
def get_infrastructure(province: str = None):
    query = "SELECT * FROM infrastructure WHERE province = %s"
    province = province.lower()
    if(province is None):
        query = "SELECT * FROM infrastructure"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (province,))    
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    result = []
    for row in rows:
        row_dict = {}
        for key, value in zip(columns, row):
            if key != 'period':
                row_dict[key] = value
        result.append(row_dict)

    return result

@app.get("/insert-infrastructure/")
def insert_all_infrastructure():
    try:
        for province in provinces:
            get_infrastructure_detail()
    except Exception as ex:
        print(f"Error : {ex} ")
        
@app.get("/insert-infrastructure-all")
def get_carbon_offset():
    try:
        get_infrastructure_detail()
        return "Success inserting data to database"
    except Exception as ex:
        print(f"Error : {ex} ")
        return {"error": "An error occurred while processing the request: " + str(ex)}
    
@app.get("/get-carbon-offset")
def get_carbon_offset():
    response = requests.get(carbon_sites, headers=headers)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, 
               ROUND(price_idr, 2), 
               ROUND(open_idr, 2), 
               ROUND(high_idr, 2), 
               ROUND(low_idr, 2), 
               vol, 
               change_percent 
        FROM carbon_market
        ORDER BY date DESC
    """)
    
    rows = cursor.fetchall()
    result = []
    for row in rows:
        formatted_date = row[0].strftime("%b %d, %Y")
        result.append({ 
            "Date": formatted_date,
            "Price (IDR)": row[1],
            "Open (IDR)": row[2],
            "High (IDR)": row[3],
            "Low (IDR)": row[4],
            "Vol": row[5],
            "Change %": row[6]
        })

    cursor.close()
    conn.close()

    return result if result else {"error": "No data found"}



@app.delete("/delete-all-infrastructure")
def delete_all_infrastructure():
    query = "DELETE FROM infrastructure"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        conn.commit()
        deleted_rows = cursor.rowcount
        return {"message": f"Successfully deleted {deleted_rows} rows from infrastructure table"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()
