# mood_tracker.py
import os, json, math, datetime
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt

# ----------  CONFIG  ----------
IMG_PATH = "assets/mood_chart.jpg"          # your first picture
CSV_PATH = "assets/moods.csv"               # data persistence
POINT_SIZE = 12                      # dot radius on canvas preview
# --------------------------------

st.set_page_config(page_title="Mood Tracker", layout="wide")

# ----------  LOAD IMAGE ----------
img = Image.open(IMG_PATH)
w, h = img.size                       # native pixel size
st.title("🗺️  Quick Mood Tracker")
st.caption("Click anywhere on the meter to log how you feel right now.")

# ----------  DRAWABLE CANVAS ----------
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",      # transparent fill
    stroke_width=POINT_SIZE,
    background_image=img,
    height=h, width=w,
    drawing_mode="point",
    key="canvas",
    update_streamlit=True,
)

# ----------  SAVE THE MOST-RECENT CLICK ----------
if canvas_result.json_data and len(canvas_result.json_data["objects"]):
    obj = canvas_result.json_data["objects"][-1]         # newest click
    x, y = obj["left"], obj["top"]

    pleasant = (x / w) * 2 - 1           # [-1, +1]  left → right
    energy   = 1 - (y / h) * 2           # [-1, +1]  bottom → top

    row = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "x_px": x, "y_px": y,
        "pleasant": pleasant,
        "energy": energy,
    }

    # append to CSV (create if absent)
    pd.DataFrame([row]).to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)

    st.toast("Mood saved!", icon="✅")

# ----------  LOAD HISTORY ----------
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

    # --------  LINE CHARTS  --------
    st.header("📈  Trends")
    p_chart = st.line_chart(df.set_index("timestamp")[["pleasant"]], height=150)
    e_chart = st.line_chart(df.set_index("timestamp")[["energy"]],   height=150)

    # --------  SCATTER PREVIEW  --------
    st.header("🖼️  Heat-map of previous moods")
    fig, ax = plt.subplots(figsize=(5,5))
    ax.imshow(img)
    age = (df["timestamp"].max() - df["timestamp"]).dt.total_seconds()
    age_norm = (age - age.min()) / (age.max() - age.min() + 1e-6)   # 0=newest
    colors = [(0,0,0, 0.15 + 0.85*a) for a in age_norm]             # fade to dark
    ax.scatter(df["x_px"], df["y_px"], s=40, c=colors)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    st.pyplot(fig)

else:
    st.info("No data yet – click the meter above to add a point!")

st.write("---")
st.caption("Everything is saved locally in *moods.csv*.  Delete the file any time to reset.")
