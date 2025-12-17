"""
Advanced Weather Analytics System
--------------------------------
Features:
- OOPS-based modular architecture
- Robust error handling
- Algorithmic analysis (DSA-oriented)
- API-driven real-world data
- CLI-style configuration
- Time & Space complexity awareness

Author: Devyansh Faye
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# -----------------------------
# Configuration
# -----------------------------
MAX_DAYS = 7
GEO_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"


# -----------------------------
# Custom Exceptions
# -----------------------------
class CityNotFoundError(Exception):
    pass


class WeatherAPIError(Exception):
    pass


# -----------------------------
# Data Fetching Layer
# -----------------------------
class WeatherFetcher:
    """Responsible for fetching location and weather data."""

    def get_coordinates(self, city: str) -> tuple:
        response = requests.get(GEO_API, params={"name": city})
        data = response.json()

        if "results" not in data:
            raise CityNotFoundError(f"City '{city}' not found.")

        result = data["results"][0]
        return result["latitude"], result["longitude"]

    def fetch_weather(self, lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
        response = requests.get(
            WEATHER_API,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min",
                "timezone": "auto",
                "start_date": start,
                "end_date": end,
            },
        )

        if response.status_code != 200:
            raise WeatherAPIError("Failed to fetch weather data")

        data = response.json()["daily"]
        df = pd.DataFrame({
            "Date": data["time"],
            "MaxTemp": data["temperature_2m_max"],
            "MinTemp": data["temperature_2m_min"],
        })
        return df


# -----------------------------
# Analysis Layer (DSA)
# -----------------------------
class WeatherAnalyzer:
    """Performs algorithmic analysis on weather data."""

    def compute_average(self, df: pd.DataFrame) -> pd.DataFrame:
        df["AvgTemp"] = (df["MaxTemp"] + df["MinTemp"]) / 2
        return df

    def get_temperature_by_date(self, df: pd.DataFrame, date: str) -> dict:
        """Returns temperature details for a specific date. O(n)."""
        result = df[df["Date"] == date]
        if result.empty:
            raise ValueError("Data not available for the given date")
        row = result.iloc[0]
        return {
            "Date": row["Date"],
            "MaxTemp": row["MaxTemp"],
            "MinTemp": row["MinTemp"],
            "AvgTemp": row.get("AvgTemp", None),
        }

    def longest_warming_streak(self, temps: list) -> int:
        max_streak = curr = 1
        for i in range(1, len(temps)):
            if temps[i] > temps[i - 1]:
                curr += 1
            else:
                curr = 1
            max_streak = max(max_streak, curr)
        return max_streak

    def top_k_hottest_days(self, df: pd.DataFrame, k: int = 3) -> pd.DataFrame:
        return df.sort_values(by="MaxTemp", ascending=False).head(k)

    def detect_anomalies(self, temps: list, threshold: float = 2.5) -> list:
        mean = sum(temps) / len(temps)
        return [t for t in temps if abs(t - mean) > threshold]


# -----------------------------
# Visualization Layer
# -----------------------------
class WeatherVisualizer:
    """Handles plotting and visualization."""

    def plot(self, df: pd.DataFrame, city: str):
        plt.figure(figsize=(10, 5))
        plt.plot(df["Date"], df["MaxTemp"], marker="o", label="Max Temp")
        plt.plot(df["Date"], df["MinTemp"], marker="o", label="Min Temp")
        plt.plot(df["Date"], df["AvgTemp"], marker="o", label="Avg Temp")
        plt.title(f"Weather Trends for {city.title()}")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.grid(True)
        plt.show()


# -----------------------------
# Application Layer
# -----------------------------
class WeatherApp:
    """Main application orchestrator."""

    def __init__(self, city: str, days: int):
        if days <= 0 or days > MAX_DAYS:
            raise ValueError("Days must be between 1 and 7")

        self.city = city
        self.days = days
        self.fetcher = WeatherFetcher()
        self.analyzer = WeatherAnalyzer()
        self.visualizer = WeatherVisualizer()

    def run(self):
        end = datetime.now().date()
        start = (datetime.now() - timedelta(days=self.days)).date()

        lat, lon = self.fetcher.get_coordinates(self.city)
        df = self.fetcher.fetch_weather(lat, lon, str(start), str(end))
        df = self.analyzer.compute_average(df)

        print("\nWeather Data:\n", df)
        print("\nStatistics:")
        print("Average Temperature:", round(df["AvgTemp"].mean(), 2))
        print("Max Temperature:", df["MaxTemp"].max())
        print("Min Temperature:", df["MinTemp"].min())

        streak = self.analyzer.longest_warming_streak(df["AvgTemp"].tolist())
        print("Longest Warming Streak:", streak, "days")

        print("\nTop 3 Hottest Days:\n", self.analyzer.top_k_hottest_days(df))

        self.visualizer.plot(df, self.city)



# Entry Point

if __name__ == "__main__":
    try:
        city = input("Enter city name: ")
        days = int(input("Enter number of past days (1-7): "))
        app = WeatherApp(city, days)
        app.run()
    except Exception as e:
        print("Error:", e)
  
