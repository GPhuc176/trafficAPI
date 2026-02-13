import requests
import pandas as pd
import time
from datetime import datetime
import os

# =====================
# CONFIG
# =====================
API_KEY = "AWNhSg6SiAQecnYzkTNl2jQSNZyQdmda"

# Khu vực Hà Nội (ước lượng)
MIN_LAT = 20.95
MAX_LAT = 21.09
MIN_LON = 105.75
MAX_LON = 105.89

GRID_STEP = 0.02
SLEEP_TIME = 0.2

OUTPUT_FILE = "traffic_hourly.csv"

# =====================
# CREATE GRID POINTS
# =====================
def generate_grid(min_lat, max_lat, min_lon, max_lon, step):
    points = []
    lat = min_lat
    while lat <= max_lat:
        lon = min_lon
        while lon <= max_lon:
            points.append((round(lat, 5), round(lon, 5)))
            lon += step
        lat += step
    return points

# =====================
# GET TRAFFIC DATA
# =====================
def get_traffic(lat, lon):
    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/"
        f"relative0/10/json?key={API_KEY}&point={lat},{lon}"
    )

    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json().get("flowSegmentData")
    if not data:
        return None

    current = data.get("currentSpeed")
    free = data.get("freeFlowSpeed")

    if not current or not free or free == 0:
        return None

    congestion_ratio = round(current / free, 2)
    traffic_density = round(1 - congestion_ratio, 2)

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "hour": f"{now.hour:02d}:00",
        "lat": lat,
        "lon": lon,
        "currentSpeed": current,
        "freeFlowSpeed": free,
        "congestion_ratio": congestion_ratio,
        "traffic_density": traffic_density
    }

# =====================
# MAIN
# =====================
def main():
    print("Collecting hourly traffic data...")

    points = generate_grid(
        MIN_LAT, MAX_LAT,
        MIN_LON, MAX_LON,
        GRID_STEP
    )

    print("Total points:", len(points))

    results = []

    for i, (lat, lon) in enumerate(points, 1):
        print(f"{i}/{len(points)} -> {lat}, {lon}")

        traffic = get_traffic(lat, lon)
        if traffic:
            results.append(traffic)

        time.sleep(SLEEP_TIME)

    if not results:
        print("No data collected.")
        return

    df = pd.DataFrame(results)

    if os.path.exists(OUTPUT_FILE):
        df.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(OUTPUT_FILE, index=False)

    print("Done. Saved to", OUTPUT_FILE)

if __name__ == "__main__":
    main()