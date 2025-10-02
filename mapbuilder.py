import requests
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os
import random

DATA_FILE = "iss_positions.csv"
HTML_FILE = "iss_map.html"

def fetch_iss_location():
    """Fetch current ISS latitude/longitude + timestamp"""
    url = "http://api.open-notify.org/iss-now.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    lat = float(data["iss_position"]["latitude"])
    lon = float(data["iss_position"]["longitude"])
    ts = datetime.fromtimestamp(data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    return lat, lon, ts

def load_positions():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["lat", "lon", "ts"])

def save_positions(df):
    df.to_csv(DATA_FILE, index=False)

def build_space_globe(df):
    # Background stars
    star_x = [random.uniform(-180, 180) for _ in range(200)]
    star_y = [random.uniform(-90, 90) for _ in range(200)]

    fig = go.Figure()

    # Stars background
    fig.add_trace(go.Scattergeo(
        lon=star_x, lat=star_y,
        mode="markers",
        marker=dict(size=2, color="white", opacity=0.6),
        hoverinfo="skip",
        showlegend=False
    ))

    # Orbit trail (all past points, no hover)
    fig.add_trace(go.Scattergeo(
        lon=df["lon"], lat=df["lat"],
        mode="lines+markers",
        line=dict(color="cyan", width=1),
        marker=dict(size=5, color="cyan", opacity=0.5),
        hoverinfo="skip",
        showlegend=False
    ))

    # Every 20th point → invisible marker carrying hover text
    step_points = df.iloc[::20]
    fig.add_trace(go.Scattergeo(
        lon=step_points["lon"], lat=step_points["lat"],
        mode="markers",
        marker=dict(size=8, color="rgba(0,0,0,0)"),  # invisible marker
        text=step_points["ts"],
        hoverinfo="text",
        name="Timestamps (hover only)"
    ))

    # Current ISS position (big red star, hover shows timestamp)
    latest = df.iloc[-1]
    fig.add_trace(go.Scattergeo(
        lon=[latest["lon"]], lat=[latest["lat"]],
        mode="markers",
        marker=dict(size=14, color="red", symbol="star"),
        text=[f"ISS 🛰️<br>{latest['ts']}"],
        hoverinfo="text",
        name="Current ISS"
    ))

    fig.update_layout(
        geo=dict(
            projection_type="orthographic",
            showland=True, landcolor="rgb(20,20,20)",
            showocean=True, oceancolor="rgb(0,0,40)",
            showcountries=True, countrycolor="rgb(60,60,60)",
            showlakes=False,
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        margin=dict(l=0, r=0, t=30, b=0),
        title=dict(
            text="🛰️ International Space Station - Orbit Trail",
            x=0.5,
            font=dict(color="white")
        )
    )
    return fig

def main():
    lat, lon, ts = fetch_iss_location()

    # Load + update
    df = load_positions()
    new_row = pd.DataFrame([[lat, lon, ts]], columns=["lat", "lon", "ts"])
    df = pd.concat([df, new_row], ignore_index=True)
    save_positions(df)

    # Build & save map
    fig = build_space_globe(df)
    fig.write_html(HTML_FILE, auto_open=False)
    print(f"🌌 Map updated with {len(df)} points, latest at {ts}")

if __name__ == "__main__":
    main()
