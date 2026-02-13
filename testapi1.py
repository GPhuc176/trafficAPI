import requests
import pandas as pd
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import os

# =====================
# CONFIG
# =====================

API_KEY = os.getenv("API_KEY")
SLEEP_TIME = 0.2
OUTPUT_FILE = "traffic_hourly.csv"

# =====================
# 25 REPRESENTATIVE POINTS – HANOI
# =====================

REPRESENTATIVE_POINTS = [

    ("Hoan_Kiem", 21.0285, 105.8542),
    ("Ba_Dinh", 21.0359, 105.8342),
    ("Dong_Da", 21.0170, 105.8290),
    ("Hai_Ba_Trung", 21.0102, 105.8500),

    ("Cau_Giay", 21.0362, 105.7906),
    ("Thanh_Xuan", 20.9965, 105.8080),
    ("Hoang_Mai", 20.9740, 105.8460),
    ("Long_Bien", 21.0476, 105.8970),
    ("Ha_Dong", 20.9714, 105.7788),
    ("Nam_Tu_Liem", 21.0122, 105.7658),
    ("Bac_Tu_Liem", 21.0715, 105.7740),
    ("Tay_Ho", 21.0702, 105.8188),

    ("Gia_Lam", 21.0400, 105.9400),
    ("Dong_Anh", 21.1360, 105.8440),

    ("Soc_Son", 21.2600, 105.8000),
    ("Me_Linh", 21.1800, 105.7300),

    ("Ba_Vi", 21.2000, 105.4000),
    ("Thach_That", 21.0600, 105.5800),
    ("Quoc_Oai", 21.0300, 105.5700),
    ("Chuong_My", 20.9500, 105.6500),

    ("Thanh_Oai", 20.8600, 105.7600),
    ("Ung_Hoa", 20.7100, 105.8000),
    ("My_Duc", 20.7000, 105.6000),
    ("Phu_Xuyen", 20.7200, 105.9000),
    ("Thuong_Tin", 20.8500, 105.8700),
]

# =====================
# GET TRAFFIC DATA
# =====================

def get_traffic(name, lat, lon):

    if not API_KEY:
        print("API_KEY not found!")
        return None

    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/"
        f"relative0/10/json?key={API_KEY}&point={lat},{lon}"
    )

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print(f"API error at {name}")
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

        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))

        return {
            "date": now.strftime("%Y-%m-%d"),
            "hour": f"{now.hour:02d}:00",
            "location_name": name,
            "lat": lat,
            "lon": lon,
            "currentSpeed": current,
            "freeFlowSpeed": free,
            "congestion_ratio": congestion_ratio,
            "traffic_density": traffic_density
        }

    except Exception as e:
        print("Error:", e)
        return None


# =====================
# MAIN
# =====================

def main():

    print("Collecting hourly traffic data for Hanoi...")
    print("Total representative points:", len(REPRESENTATIVE_POINTS))

    results = []

    for i, (name, lat, lon) in enumerate(REPRESENTATIVE_POINTS, 1):

        print(f"{i}/25 -> {name} ({lat}, {lon})")

        traffic = get_traffic(name, lat, lon)

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

