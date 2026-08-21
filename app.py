import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium


'''
# 🚕 TaxiFareModel Fares
'''

st.markdown('''
###   Helping you estimate your taxi fare in NYC 🍎
''')

geolocator = Nominatim(user_agent="nyc_taxi_fare_frontend")

st.subheader("1. Trip Parameters")

col1, col2 = st.columns(2)

with col1:
    pickup_date = st.date_input("Pickup Date", datetime.today())
    pickup_time = st.time_input("Pickup Time", datetime.now().time())
    passenger_count = st.number_input("Passenger Count", min_value=1, max_value=8, value=1)

with col2:
    pickup_address = st.text_input("Pickup Address", value="Empire State Building, New York")
    dropoff_address = st.text_input("Dropoff Address", value="Central Park, New York")
# 1. Combine date and time variables FIRST
pickup_datetime = f"{pickup_date} {pickup_time}"

pickup_latitude = 40.7128
pickup_longitude = -74.0060
dropoff_latitude = 40.7128
dropoff_longitude = -74.0060

# Convert addresses into precise coordinates under the hood
if pickup_address:
    try:
        pickup_loc = geolocator.geocode(pickup_address)
        if pickup_loc:
            pickup_latitude = pickup_loc.latitude
            pickup_longitude = pickup_loc.longitude
    except Exception:
        print('Invalid Pickup Address')

if dropoff_address:
    try:
        dropoff_loc = geolocator.geocode(dropoff_address)
        if dropoff_loc:
            dropoff_latitude = dropoff_loc.latitude
            dropoff_longitude = dropoff_loc.longitude
    except Exception:
        print('Invalid Dropoff Address')

# Optional: Visual confirmation so the user can verify what coordinates were fetched
st.info(f"📍 **Coordinates Pickup:** {pickup_latitude:.4f}, {pickup_longitude:.4f} | **Dropoff:** {dropoff_latitude:.4f}, {dropoff_longitude:.4f}")

# 3. Build your query parameter dictionary
formatted_time = pickup_time.strftime("%H:%M:%S")
pickup_datetime = f"{pickup_date} {formatted_time}"

url = "https://taxifare-1087886990522.europe-west1.run.app/predict"

# Variables are cleanly cast to float, int, and str to match your strict types
params = {
    "pickup_datetime": str(pickup_datetime),
    "pickup_longitude": float(pickup_longitude),
    "pickup_latitude": float(pickup_latitude),
    "dropoff_longitude": float(dropoff_longitude),
    "dropoff_latitude": float(dropoff_latitude),
    "passenger_count": int(passenger_count)
}

st.subheader("2. Predict Fare 💵 ")

# 3. Request Action Button
if st.button("🔮 Calculate Estimated Fare"):
    with st.spinner("Calling API for a prediction..."):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Trigger error for bad status codes

            data = response.json()
            # Adjust the key dictionary based on your API's JSON output structure (e.g., 'fare' or 'prediction')
            prediction = data.get("fare", data.get("prediction", "N/A"))

            if isinstance(prediction, (int, float)):
                st.success(f"### Estimated Fare: ${prediction:.2f}")
            else:
                st.success(f"### Prediction Response: {prediction}")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the API. Error details: {e}")

st.subheader("3. Trip Map 🗺️")

# 1. Prepare your raw coordinates data
map_data = {
    "lat": [pickup_latitude, dropoff_latitude],
    "lon": [pickup_longitude, dropoff_longitude],
    "type": ["Pickup", "Dropoff"],
}

# 2. Convert to a proper Pandas DataFrame
df = pd.DataFrame(map_data)

# 3. Create a color column mapped to hex codes or basic color names
# Here, Pickups will be blue and Dropoffs will be red
df["point_color"] = df["type"].map({"Pickup": "#0000FF", "Dropoff": "#FF0000"})

# 4. Render the map safely using your new color column
st.map(
    data=df,
    latitude="lat",
    longitude="lon",
    color="point_color"
)
