import json
import os
import re
import math
import csv
import io
from html import escape
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
import urllib.request
import urllib.error

# ---------------- CONFIGURATION ----------------
APP_NAME = "StudyFlow AI"
DEFAULT_MODEL = "gemini-2.5-flash"
DATA_FILE = Path("studyflow_data.json")

BG = "#0B1020"
SIDEBAR = "#10182B"
PANEL = "#151F35"
CARD = "#1B2942"
BLUE = "#718CFF"
PURPLE = "#A78BFA"
GREEN = "#42D6A4"
ORANGE = "#FFB86B"
RED = "#FF7185"
WHITE = "#F3F5FF"
MUTED = "#93A1BC"
BORDER = "#293753"

# ---------------- PAGE + STYLING ----------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp {
  color: #F5F1FF;
  background:
    linear-gradient(rgba(142,91,255,.075) 1px, transparent 1px),
    linear-gradient(90deg, rgba(142,91,255,.075) 1px, transparent 1px),
    radial-gradient(ellipse at 12% 5%, rgba(151,83,255,.19), transparent 32%),
    radial-gradient(ellipse at 88% 18%, rgba(112,62,220,.22), transparent 30%),
    radial-gradient(ellipse at 55% 100%, rgba(190,115,255,.09), transparent 35%),
    #090611;
  background-size: 42px 42px, 42px 42px, auto, auto, auto, auto;
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(9,5,20,.76); }
[data-testid="stSidebar"] {
  background: linear-gradient(165deg, rgba(25,13,48,.97), rgba(10,7,24,.98));
  border-right: 1px solid rgba(173,125,255,.24);
  box-shadow: 12px 0 45px rgba(0,0,0,.22);
}
[data-testid="stSidebar"] * { color: #EAF5FF; }
h1,h2,h3,h4,p,label { color: #F5F1FF; }
.brand { font-family: 'Space Grotesk',sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.8px; }
.muted { color: #9EB5CC; }
.eyebrow { color: #C7A6FF; font-size: 10px; font-weight: 800; letter-spacing: 2px; }

.glass-hero {
  position: relative; overflow: hidden; isolation: isolate;
  padding: 31px 34px; margin: 2px 0 25px; border-radius: 23px;
  border: 1px solid rgba(185,137,255,.42);
  background: linear-gradient(112deg, rgba(67,31,116,.78), rgba(35,24,83,.76) 54%, rgba(77,34,125,.74));
  box-shadow: 0 18px 55px rgba(0,0,0,.34), 0 0 34px rgba(160,83,255,.16), inset 0 1px 0 rgba(255,255,255,.17);
  backdrop-filter: blur(28px) saturate(150%); -webkit-backdrop-filter: blur(28px) saturate(150%);
  animation: riseIn .6s ease both;
}
.glass-hero:before {
  content:""; position:absolute; z-index:-1; width:260px; height:260px; right:7%; top:-175px;
  border-radius:50%; background:rgba(185,130,255,.22); filter:blur(5px);
}
.glass-hero:after {
  content:""; position:absolute; right:-30px; bottom:-85px; width:250px; height:180px;
  border:1px solid rgba(188,139,255,.30); border-radius:50%;
  box-shadow:0 0 0 18px rgba(188,139,255,.04), 0 0 0 38px rgba(188,139,255,.025);
  transform:rotate(-18deg); z-index:-1;
}
.hero-label { color:#D1B7FF; font-size:10px; font-weight:800; letter-spacing:2.4px; }
.hero-heading { font-family:'Space Grotesk',sans-serif; color:#FFFFFF; font-size:32px; font-weight:700; letter-spacing:-1.2px; margin:8px 0 5px; }
.hero-caption { color:#D2C5EA; font-size:13px; }
.hero-status { display:inline-block; margin-top:16px; padding:6px 11px; border-radius:30px; border:1px solid rgba(191,137,255,.35); background:rgba(145,77,220,.14); color:#D7B8FF; font-size:10px; letter-spacing:1px; font-weight:700; }

.stat-card {
  position:relative; overflow:hidden; isolation:isolate; min-height:146px; padding:21px;
  border-radius:18px; border:1px solid rgba(183,145,255,.25); border-top-color:rgba(239,222,255,.38);
  background:linear-gradient(145deg, rgba(58,35,91,.76), rgba(18,12,35,.86));
