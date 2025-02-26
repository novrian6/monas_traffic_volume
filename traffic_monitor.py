import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, jsonify
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

app = Flask(__name__, static_url_path='/static')

API_KEY = "eqNlTGMo0TDbaGDLJezgMF7kBE177FpC" ##KEy 2: eqNlTGMo0TDbaGDLJezgMF7kBE177FpC Key3: DZoGAkP2sIlAAqfeEltC1WfA2t441WZX
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

def fetch_traffic_data():
    """Fetches traffic data every minute."""
    global traffic_data

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

        time.sleep(60)

def plot_current_traffic():
    """Generates bar chart for current traffic volume."""
    if traffic_data.empty:
        return None

    traffic_data["Time"] = traffic_data["Time"].astype(str)
    latest_time = traffic_data["Time"].max()
    latest_data = traffic_data[traffic_data["Time"] == latest_time]

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x="Location", y="Traffic Volume", data=latest_data, palette="coolwarm")

    for bar, row in zip(ax.patches, latest_data.itertuples(index=False)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height * 0.5,
            f"{row._2:.0f}",
            ha='center', va='center', color='white', fontsize=12, fontweight='bold'
        )

    plt.title(f"Current Traffic Volume ({latest_time})")
    plt.xlabel("Location")
    plt.ylabel("Traffic Volume (vehicles/hour)")
    plt.xticks(rotation=30, ha="right")
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

def plot_historical_traffic():
    """Generates line chart for traffic over time with formatted X-axis."""
    if traffic_data.empty:
        return None

    traffic_data["Time"] = pd.to_datetime(traffic_data["Time"])

    plt.figure(figsize=(12, 6))

    try:
        pivot_data = traffic_data.pivot(index="Time", columns="Location", values="Traffic Volume")
        pivot_data.plot(marker='o', linestyle='-')

        plt.title("Traffic Volume Over Time")
        plt.xlabel("Time (Jakarta WIB)")
        plt.ylabel("Traffic Volume (vehicles/hour)")
        plt.xticks(rotation=45, ha="right", fontsize=10)

        # Format X-axis labels as dd:MMM:yy hh:mm
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d:%b:%y %H:%M'))

        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
    except ValueError:
        return None

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

def simulate_traffic_logistic_model():
    """Simulates traffic volume using the logistic model."""
    speeds = np.linspace(0, 100, 100)  # Speed from 0 to 100 km/h
    densities = K_JAM / (1 + np.exp(ALPHA * (speeds - V_CRITICAL)))  # Density using logistic model
    volumes = densities * speeds  # Traffic volume (flow)

    plt.figure(figsize=(10, 5))
    plt.plot(speeds, volumes, label="Traffic Volume", color="b")
    plt.axvline(V_CRITICAL, linestyle="--", color="r", label=f"Critical Speed ({V_CRITICAL} km/h)")
    plt.xlabel("Speed (km/h)")
    plt.ylabel("Traffic Volume (vehicles/hour)")
    plt.title("Traffic Volume vs Speed using Logistic Model")
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/')
def index():
    """Displays the dashboard with updated traffic charts."""
    current_plot = plot_current_traffic()
    historical_plot = plot_historical_traffic()
    simulation_plot = simulate_traffic_logistic_model()
    return render_template("index.html", current_plot=current_plot, historical_plot=historical_plot, simulation_plot=simulation_plot)

@app.route('/data')
def get_data():
    """Returns traffic data in JSON format."""
    return jsonify(traffic_data.to_dict(orient="records"))

threading.Thread(target=fetch_traffic_data, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)