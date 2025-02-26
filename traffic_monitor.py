import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
import io
import base64
import threading
import time
import matplotlib.dates as mdates

app = Flask(__name__, static_url_path='/static')

API_KEY = "eqNlTGMo0TDbaGDLJezgMF7kBE177FpC"
BASE_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

LOCATIONS = [
    (-6.1745, 106.8295),
    (-6.1762, 106.8250),
    (-6.1775, 106.8282),
    (-6.1735, 106.8279)
]

LOCATION_LABELS = {
    (-6.1745, 106.8295): "Medan Merdeka Timur",
    (-6.1762, 106.8250): "Medan Merdeka Barat",
    (-6.1775, 106.8282): "Medan Merdeka Selatan",
    (-6.1735, 106.8279): "Medan Merdeka Utara"
}

K_JAM = 150
V_CRITICAL = 30
ALPHA = 0.1

traffic_data = pd.DataFrame(columns=["Time", "Location", "Traffic Volume"])
sleep_duration = 900  # Default to 15 minutes

def fetch_traffic_data():
    global traffic_data, sleep_duration
    while True:
        current_time = datetime.datetime.now() + datetime.timedelta(hours=7)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        new_data = []
        for lat, lon in LOCATIONS:
            params = {"key": API_KEY, "point": f"{lat},{lon}", "unit": "KMPH"}
            response = requests.get(BASE_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                if 'flowSegmentData' not in data:
                    continue

                current_speed = data['flowSegmentData']['currentSpeed']
                location_label = LOCATION_LABELS.get((lat, lon), f"({lat}, {lon})")
                density = K_JAM / (1 + np.exp(ALPHA * (current_speed - V_CRITICAL)))
                volume = density * current_speed
                new_data.append({"Time": formatted_time, "Location": location_label, "Traffic Volume": volume})

        if new_data:
            new_df = pd.DataFrame(new_data)
            traffic_data = pd.concat([traffic_data, new_df], ignore_index=True)
            traffic_data.to_csv("monas_traffic_volume.csv", index=False)

        time.sleep(sleep_duration)

@app.route('/', methods=['GET', 'POST'])
def index():
    global sleep_duration
    if request.method == 'POST':
        new_duration = int(request.form.get('sleep_duration', 900))
        sleep_duration = max(60, min(new_duration, 3600))
    return render_template("index.html", sleep_duration=sleep_duration)

@app.route('/update_sleep', methods=['POST'])
def update_sleep():
    global sleep_duration
    new_duration = int(request.form.get('sleep_duration', 900))
    sleep_duration = max(60, min(new_duration, 3600))
    return jsonify({"sleep_duration": sleep_duration})

threading.Thread(target=fetch_traffic_data, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
