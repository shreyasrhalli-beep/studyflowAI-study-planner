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
  box-shadow:0 14px 34px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.09);
  backdrop-filter:blur(24px) saturate(145%); -webkit-backdrop-filter:blur(24px) saturate(145%);
  transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
  animation:riseIn .55s ease both;
}
.stat-card:after { content:""; position:absolute; z-index:-1; right:-48px; top:-62px; width:140px; height:140px; border-radius:50%; background:rgba(173,112,255,.16); filter:blur(4px); }
.stat-card:hover { transform:translateY(-5px); border-color:rgba(197,153,255,.72); box-shadow:0 18px 42px rgba(144,76,255,.18),inset 0 1px 0 rgba(255,255,255,.13); }
.stat-label { color:#C0ACDD; font-size:10px; font-weight:800; letter-spacing:1.5px; }
.stat-value { font-family:'Space Grotesk',sans-serif; color:#F4FBFF; font-size:34px; font-weight:700; margin:10px 0 4px; }
.stat-sub { color:#92AFC4; font-size:12px; }

[data-testid="stVerticalBlockBorderWrapper"] > div {
  border:1px solid rgba(180,139,255,.22) !important; border-radius:19px !important;
  background:linear-gradient(145deg,rgba(43,28,70,.76),rgba(15,10,30,.86)) !important;
  box-shadow:0 13px 32px rgba(0,0,0,.24),inset 0 1px 0 rgba(255,255,255,.055);
  backdrop-filter:blur(23px) saturate(140%); -webkit-backdrop-filter:blur(23px) saturate(140%);
}
[data-testid="stMetric"] { background:rgba(42,26,68,.72); border:1px solid rgba(178,137,255,.22); border-radius:15px; padding:15px; }
[data-testid="stMetricLabel"] { color:#C0ACDD !important; }
[data-testid="stMetricValue"] { color:#F4FBFF !important; font-family:'Space Grotesk',sans-serif; }
div[data-testid="stForm"] { background:rgba(32,18,55,.80); border:1px solid rgba(130,203,232,.24); border-radius:18px; padding:18px; backdrop-filter:blur(20px); }
.task-row { background:rgba(48,30,78,.64); border:1px solid rgba(130,203,232,.20); border-radius:13px; padding:14px 17px; margin:8px 0; }
div.stButton > button { border-radius:10px; border:1px solid rgba(183,132,255,.38); font-weight:700; min-height:41px; transition:all .18s ease; }
div.stButton > button:hover { transform:translateY(-2px); border-color:#D0AEFF; box-shadow:0 0 18px rgba(166,92,255,.22); }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#A65CFF,#8C6BFF,#D0A5FF); }
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input {
  background:rgba(16,9,32,.90); color:#F5F1FF; border:1px solid rgba(180,139,255,.28); border-radius:10px;
}
[data-baseweb="select"] > div { background:rgba(16,9,32,.92); border-color:rgba(180,139,255,.28); border-radius:10px; }
.stChatMessage { background:rgba(38,24,64,.76); border:1px solid rgba(130,203,232,.22); border-radius:16px; backdrop-filter:blur(18px); }
hr { border-color:rgba(180,139,255,.15); }

/* Futuristic startup loader + branded activity indicator */
.startup-loader {
  position:fixed; inset:0; z-index:999999; display:flex; align-items:center;
  justify-content:center; flex-direction:column; gap:17px;
  background:radial-gradient(circle at 50% 45%,rgba(164,91,255,.16),transparent 28%),
  radial-gradient(circle at 50% 55%,rgba(183,107,255,.15),transparent 38%),rgba(5,11,21,.97);
  backdrop-filter:blur(18px); animation:loaderFadeOut .8s ease 2.4s forwards;
  pointer-events:none;
}
.loader-core { position:relative; width:94px; height:94px; display:grid; place-items:center; }
.loader-ring,.loader-core:before,.loader-core:after {
  content:""; position:absolute; border-radius:50%; border:2px solid transparent;
}
.loader-ring { inset:0; border-top-color:#B98AFF; border-right-color:rgba(185,138,255,.38);
  box-shadow:0 0 20px rgba(166,92,255,.22); animation:loaderSpin 1.35s linear infinite; }
.loader-core:before { inset:11px; border-bottom-color:#D0A5FF; border-left-color:rgba(208,165,255,.42);
  box-shadow:0 0 18px rgba(208,165,255,.20); animation:loaderSpinReverse 1.05s linear infinite; }
.loader-core:after { inset:25px; border:1px solid rgba(198,159,255,.60);
  background:radial-gradient(circle,rgba(181,126,255,.25),rgba(126,75,230,.08));
  box-shadow:0 0 28px rgba(166,92,255,.24),inset 0 0 15px rgba(166,92,255,.20);
  animation:loaderPulse 1.4s ease-in-out infinite; }
.loader-star { position:relative; z-index:2; color:#FBF7FF; font-size:22px;
  text-shadow:0 0 14px #C69AFF; animation:loaderPulse 1.4s ease-in-out infinite; }
.loader-title { font-family:'Space Grotesk',sans-serif; color:#F1FAFF; font-size:16px;
  font-weight:700; letter-spacing:3px; }
.loader-subtitle { color:#8EABC2; font-size:9px; font-weight:700; letter-spacing:2.2px; }
.loader-track { width:145px; height:2px; overflow:hidden; border-radius:5px; background:rgba(180,139,255,.18); }
.loader-track:after { content:""; display:block; height:100%; width:42%;
  background:linear-gradient(90deg,transparent,#B98AFF,#D0A5FF,transparent);
  box-shadow:0 0 12px #C69AFF; animation:loaderProgress 1.15s ease-in-out infinite; }
[data-testid="stSpinner"] > div > div {
  border-top-color:#B98AFF !important; border-right-color:rgba(208,165,255,.70) !important;
}
@keyframes loaderSpin { to { transform:rotate(360deg); } }
@keyframes loaderSpinReverse { to { transform:rotate(-360deg); } }
@keyframes loaderPulse { 0%,100% { transform:scale(.94); opacity:.78; } 50% { transform:scale(1.06); opacity:1; } }
@keyframes loaderProgress { 0% { transform:translateX(-120%); } 100% { transform:translateX(360%); } }
@keyframes loaderFadeOut { to { opacity:0; visibility:hidden; } }
@media(prefers-reduced-motion:reduce) {
  .startup-loader,.loader-ring,.loader-core:before,.loader-core:after,.loader-star,.loader-track:after { animation:none !important; }
  .startup-loader { display:none; }
}

@keyframes riseIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
@media(prefers-reduced-motion:reduce) { *,*:before,*:after { animation:none !important; transition:none !important; } }

.page-heading { margin: 4px 0 22px; animation:riseIn .45s ease both; }
.page-heading h1 { font-family:'Space Grotesk',sans-serif; font-size:30px; letter-spacing:-.8px; margin:5px 0 2px; }
.page-heading p { margin:0; font-size:13px; }

/* Refined AI planner: polished input panel and readable timetable timeline. */
.planner-hero {
  position: relative; overflow: hidden; isolation: isolate;
  padding: 27px 30px; margin: 2px 0 20px; border-radius: 22px;
  border: 1px solid rgba(194,155,255,.36);
  background: linear-gradient(115deg, rgba(62,32,112,.86), rgba(24,16,52,.88) 58%, rgba(80,39,125,.76));
  box-shadow: 0 18px 48px rgba(0,0,0,.27), 0 0 35px rgba(150,82,255,.12), inset 0 1px 0 rgba(255,255,255,.13);
  animation: riseIn .55s ease both;
}
.planner-hero:after { content:""; position:absolute; width:210px; height:210px; right:6%; top:-135px; border-radius:50%; background:rgba(190,139,255,.17); filter:blur(8px); z-index:-1; }
.planner-hero-kicker,.plan-kicker { color:#D0B1FF; font-size:10px; letter-spacing:2px; font-weight:800; }
.planner-hero-title { color:#fff; font:700 30px 'Space Grotesk',sans-serif; letter-spacing:-.8px; margin:8px 0 6px; }
.planner-hero-copy { color:#D4C7E9; font-size:13px; max-width:760px; line-height:1.7; }
.plan-result-head { padding:22px 24px; margin:14px 0 18px; border-radius:19px; border:1px solid rgba(190,145,255,.34); background:linear-gradient(110deg,rgba(83,43,141,.56),rgba(30,20,61,.72)); box-shadow:0 12px 32px rgba(0,0,0,.18); }
.plan-result-title { color:#fff; font:700 25px 'Space Grotesk',sans-serif; margin:5px 0; }
.plan-result-copy { color:#D3C5E8; font-size:13px; line-height:1.65; }
.plan-source { display:inline-block; color:#E1CFFF; font-size:10px; letter-spacing:1px; text-transform:uppercase; margin-top:12px; padding:5px 9px; border:1px solid rgba(199,164,255,.28); border-radius:20px; background:rgba(146,91,220,.14); }
.schedule-list { display:flex; flex-direction:column; gap:11px; margin:12px 0 20px; }
.schedule-row { display:grid; grid-template-columns:105px 42px minmax(0,1fr) auto; gap:14px; align-items:center; padding:16px 18px; border-radius:16px; border:1px solid rgba(180,139,255,.22); background:linear-gradient(105deg,rgba(41,27,68,.80),rgba(18,12,34,.88)); box-shadow:0 8px 24px rgba(0,0,0,.16); transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease; }
.schedule-row:hover { transform:translateY(-2px); border-color:rgba(200,164,255,.50); box-shadow:0 12px 28px rgba(119,65,210,.14); }
.schedule-break { background:linear-gradient(105deg,rgba(39,42,73,.72),rgba(18,14,38,.84)); border-color:rgba(145,155,255,.20); }
.schedule-time { display:flex; flex-direction:column; gap:3px; color:#F0E7FF; font-size:13px; }
.schedule-time span { color:#AFA0CB; font-size:11px; }
.schedule-icon { width:38px; height:38px; display:grid; place-items:center; border-radius:12px; color:#E8D5FF; font-size:16px; background:rgba(151,91,236,.18); border:1px solid rgba(190,145,255,.24); }
.schedule-break .schedule-icon { background:rgba(111,130,225,.15); border-color:rgba(145,155,255,.23); }
.schedule-title { color:#F6F0FF; font-size:14px; font-weight:700; }
.schedule-subject { color:#C5A9F4; font-size:11px; margin-top:3px; }
.schedule-description { color:#B8ADC9; font-size:12px; line-height:1.55; margin-top:6px; }
.schedule-tag { color:#D4B9FF; font-size:9px; font-weight:800; letter-spacing:1px; padding:5px 11px; border-radius:20px; border:1px solid rgba(185,139,255,.24); background:rgba(142,81,224,.12); white-space:nowrap; }
.schedule-break .schedule-tag { color:#BFCBFF; border-color:rgba(143,155,255,.22); background:rgba(105,120,210,.12); }
@media(max-width:700px) { .schedule-row { grid-template-columns:76px 34px minmax(0,1fr); gap:8px; padding:12px; } .schedule-tag { display:none; } .planner-hero-title { font-size:24px; } }
"""

# Light theme styles, injected only when the in-app toggle is on.
LIGHT_CSS = """
/* STUDYFLOW LIGHT THEME — clean white surfaces + soft lavender accents */
.stApp {
  color: #2D2440 !important;
  background:
    radial-gradient(ellipse at 10% 3%, rgba(190,158,255,.22), transparent 34%),
    radial-gradient(ellipse at 91% 9%, rgba(220,202,255,.27), transparent 32%),
    radial-gradient(ellipse at 52% 100%, rgba(235,224,255,.30), transparent 38%),
    linear-gradient(135deg, #FCFAFF, #F5F0FC 54%, #FFFFFF) !important;
  background-attachment: fixed !important;
}
[data-testid="stHeader"] {
  background: rgba(252,250,255,.84) !important;
  border-bottom: 1px solid rgba(151,119,197,.14) !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(165deg, rgba(253,250,255,.99), rgba(240,233,251,.98)) !important;
  border-right: 1px solid rgba(151,119,197,.22) !important;
  box-shadow: 10px 0 35px rgba(75,52,110,.07) !important;
}
[data-testid="stSidebar"] * { color: #352849 !important; }

h1, h2, h3, h4, p, label,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p {
  color: #302542;
}
.muted { color: #766987 !important; }
.eyebrow { color: #8058B5 !important; }

.glass-hero {
  background: linear-gradient(112deg,
    rgba(255,255,255,.97),
    rgba(239,230,255,.96) 55%,
    rgba(248,239,255,.97)) !important;
  border: 1px solid rgba(157,125,207,.34) !important;
  box-shadow: 0 16px 38px rgba(77,53,113,.10),
              0 0 26px rgba(165,125,232,.08),
              inset 0 1px 0 rgba(255,255,255,.98) !important;
}
.hero-label { color: #8158B7 !important; }
.hero-heading { color: #2C1F43 !important; }
.hero-caption { color: #6D607C !important; }
.hero-status {
  color: #69449B !important;
  background: rgba(159,119,220,.12) !important;
  border-color: rgba(151,112,208,.30) !important;
}
.glass-hero:before { background: rgba(183,145,240,.18) !important; }
.glass-hero:after {
  border-color: rgba(157,125,207,.24) !important;
  box-shadow: 0 0 0 18px rgba(157,125,207,.035),
              0 0 0 38px rgba(157,125,207,.022) !important;
}

.stat-card {
  background: linear-gradient(145deg, rgba(255,255,255,.97), rgba(246,241,253,.96)) !important;
  border: 1px solid rgba(165,137,207,.25) !important;
  border-top-color: rgba(255,255,255,.99) !important;
  box-shadow: 0 10px 28px rgba(65,46,97,.075),
              inset 0 1px 0 rgba(255,255,255,.98) !important;
}
.stat-card:hover {
  border-color: rgba(151,108,213,.48) !important;
  box-shadow: 0 16px 34px rgba(121,83,177,.13) !important;
}
.stat-label { color: #786A8B !important; }
.stat-value { color: #38294F !important; }
.stat-sub { color: #877A98 !important; }

[data-testid="stVerticalBlockBorderWrapper"] > div {
  background: linear-gradient(145deg, rgba(255,255,255,.96), rgba(247,243,252,.97)) !important;
  border: 1px solid rgba(164,139,202,.25) !important;
  box-shadow: 0 10px 28px rgba(63,45,92,.065),
              inset 0 1px 0 rgba(255,255,255,.98) !important;
}
[data-testid="stMetric"] {
  background: rgba(255,255,255,.88) !important;
  border-color: rgba(164,139,202,.25) !important;
}
[data-testid="stMetricLabel"] { color: #786A8B !important; }
[data-testid="stMetricValue"] { color: #38294F !important; }

div[data-testid="stForm"] {
  background: rgba(255,255,255,.91) !important;
  border-color: rgba(164,139,202,.27) !important;
  box-shadow: 0 8px 24px rgba(63,45,92,.055) !important;
}
.task-row {
  background: rgba(255,255,255,.90) !important;
  border-color: rgba(164,139,202,.24) !important;
  color: #38294F !important;
}

div.stButton > button {
  color: #4B3867 !important;
  background: linear-gradient(135deg, rgba(255,255,255,.98), rgba(247,242,254,.96)) !important;
  border: 1px solid rgba(157,125,207,.30) !important;
}
div.stButton > button:hover {
  color: #7149A6 !important;
  border-color: #B99AE5 !important;
  box-shadow: 0 6px 18px rgba(128,88,181,.13) !important;
}
div.stButton > button[kind="primary"] {
  color: #FFFFFF !important;
  background: linear-gradient(105deg, #8053C6, #A17AE0 58%, #B18CE9) !important;
  border: 1px solid rgba(133,91,190,.25) !important;
  box-shadow: 0 7px 20px rgba(123,82,180,.19) !important;
}

.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
  color: #352849 !important;
  background: rgba(255,255,255,.97) !important;
  border: 1px solid rgba(157,125,207,.32) !important;
}
[data-baseweb="select"] > div {
  color: #352849 !important;
  background: rgba(255,255,255,.97) !important;
  border-color: rgba(157,125,207,.32) !important;
}
[data-baseweb="select"] * { color: #352849 !important; }
.stChatMessage {
  background: rgba(255,255,255,.93) !important;
  border-color: rgba(164,139,202,.25) !important;
}

.startup-loader {
  background:
    radial-gradient(circle at 50% 45%, rgba(178,139,239,.16), transparent 28%),
    radial-gradient(circle at 50% 55%, rgba(210,188,255,.18), transparent 38%),
    rgba(250,247,255,.98) !important;
}
.loader-title { color: #38264F !important; }
.loader-subtitle { color: #7B6A91 !important; }
.loader-star { color: #8053C6 !important; text-shadow: 0 0 14px rgba(174,137,235,.65) !important; }
hr { border-color: rgba(151,119,197,.18) !important; }

/* AI planner hero and timetable cards */
.planner-hero {
  background: linear-gradient(115deg, rgba(255,255,255,.98),
    rgba(239,230,255,.98) 58%, rgba(249,240,255,.97)) !important;
  border-color: rgba(151,112,205,.29) !important;
}
.planner-hero-title { color: #302044 !important; }
.planner-hero-kicker, .plan-kicker { color: #7950AC !important; }
.planner-hero-copy, .plan-result-copy { color: #6F6281 !important; }
.plan-result-head {
  background: linear-gradient(110deg, rgba(249,245,255,.98), rgba(240,233,252,.98)) !important;
  border-color: rgba(151,112,205,.25) !important;
}
.plan-result-title { color: #302044 !important; }
.plan-source {
  color: #7049A3 !important;
  background: rgba(159,119,220,.11) !important;
  border-color: rgba(151,112,205,.25) !important;
}
.schedule-row {
  background: linear-gradient(105deg, rgba(255,255,255,.98), rgba(245,239,254,.98)) !important;
  border: 1px solid rgba(157,125,207,.32) !important;
  box-shadow: 0 8px 24px rgba(77,53,113,.08), inset 0 1px 0 rgba(255,255,255,.98) !important;
}
.schedule-row:hover {
  border-color: rgba(139,95,199,.60) !important;
  box-shadow: 0 12px 28px rgba(128,88,181,.14), inset 0 1px 0 rgba(255,255,255,.98) !important;
}
.schedule-icon {
  color: #7950AC !important;
  background: linear-gradient(145deg, rgba(244,236,255,.98), rgba(233,221,252,.95)) !important;
  border: 1px solid rgba(157,125,207,.36) !important;
  box-shadow: 0 4px 12px rgba(128,88,181,.10) !important;
}
.schedule-break .schedule-icon {
  color: #5C6BC0 !important;
  background: linear-gradient(145deg, rgba(238,242,255,.98), rgba(226,232,253,.95)) !important;
  border: 1px solid rgba(130,145,220,.34) !important;
}
.schedule-title, .schedule-time, .schedule-time strong { color: #2C1F43 !important; }
.schedule-time span, .schedule-description { color: #6E6080 !important; }
.schedule-subject { color: #8057B4 !important; }
.schedule-tag {
  color: #6E45A3 !important;
  background: rgba(146,103,203,.12) !important;
  border: 1px solid rgba(151,112,205,.32) !important;
}
.schedule-break {
  background: linear-gradient(105deg, rgba(248,247,255,.98), rgba(238,240,253,.98)) !important;
  border: 1px solid rgba(145,155,225,.28) !important;
}
.schedule-break .schedule-tag {
  color: #4F5EB3 !important;
  background: rgba(111,130,225,.12) !important;
  border: 1px solid rgba(130,145,220,.30) !important;
}

/* Native Streamlit labels, alerts, expanders, and tables */
body, .stApp, [data-testid="stAppViewContainer"] { color-scheme: light !important; }
[data-testid="stMain"], [data-testid="stMainBlockContainer"] { color: #302542 !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stWidgetLabel"] p,
.stSelectbox label, .stTextInput label, .stTextArea label,
.stNumberInput label, .stDateInput label, .stMultiSelect label {
  color: #514363 !important;
}
[data-testid="stExpander"], [data-testid="stPopover"],
[data-testid="stDataFrame"], [data-testid="stTable"],
[data-testid="stAlert"] { color: #352849 !important; }

"""

PURPLE_CSS = """
.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(139,72,255,.20), transparent 34%),
    radial-gradient(ellipse at 88% 14%, rgba(92,49,190,.19), transparent 32%),
    radial-gradient(ellipse at 52% 100%, rgba(178,91,255,.10), transparent 38%),
    #090611 !important;
  background-attachment: fixed !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(165deg, rgba(25,13,48,.98), rgba(10,7,24,.99)) !important;
  border-right: 1px solid rgba(184,137,255,.25) !important;
}
.glass-hero {
  border-color: rgba(190,151,255,.42) !important;
  background: linear-gradient(112deg, rgba(65,31,112,.80), rgba(31,20,72,.82) 55%, rgba(77,34,125,.76)) !important;
  box-shadow: 0 20px 58px rgba(0,0,0,.36), 0 0 36px rgba(145,78,255,.16), inset 0 1px 0 rgba(255,255,255,.18) !important;
}
.stat-card, [data-testid="stVerticalBlockBorderWrapper"] > div {
  border-color: rgba(184,145,255,.25) !important;
  background: linear-gradient(145deg, rgba(45,29,75,.76), rgba(15,10,30,.86)) !important;
}
.stat-card:hover {
  border-color: rgba(203,164,255,.72) !important;
  box-shadow: 0 18px 42px rgba(132,68,255,.18), inset 0 1px 0 rgba(255,255,255,.13) !important;
}
div.stButton > button {
  border-color: rgba(184,137,255,.34) !important;
  background: linear-gradient(135deg, rgba(56,32,91,.82), rgba(28,17,52,.90)) !important;
  color: #F5EEFF !important;
}
div.stButton > button:hover {
  border-color: #C9A4FF !important;
  box-shadow: 0 0 20px rgba(166,92,255,.25) !important;
}
div.stButton > button[kind="primary"] {
  background: linear-gradient(110deg, #7436D9, #A34EFF 58%, #7545E8) !important;
  border: 1px solid rgba(224,199,255,.38) !important;
  box-shadow: 0 7px 24px rgba(133,65,230,.25), inset 0 1px 0 rgba(255,255,255,.22) !important;
}
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, #8B45F5, #B56BFF, #D0A5FF) !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input,
[data-baseweb="select"] > div {
  border-color: rgba(184,137,255,.30) !important;
}
.task-row {
  border-color: rgba(184,137,255,.25) !important;
  background: rgba(43,27,70,.66) !important;
}
@keyframes violetFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
.glass-hero { animation: riseIn .65s ease both, violetFloat 8s ease-in-out 1s infinite; }
@media (prefers-reduced-motion: reduce) {
  .glass-hero { animation: none !important; }
}



"""


OCEAN_CSS = """
.stApp {
  background:
    radial-gradient(ellipse at 10% 2%, rgba(83,177,226,.20), transparent 34%),
    radial-gradient(ellipse at 92% 10%, rgba(102,154,218,.17), transparent 32%),
    linear-gradient(135deg,#F7FCFF,#EDF6FC 56%,#FFFFFF) !important;
}
[data-testid="stHeader"] { background:rgba(248,252,255,.88) !important; border-color:rgba(94,151,192,.18) !important; }
[data-testid="stSidebar"] { background:linear-gradient(165deg,#FBFDFF,#EAF4FA) !important; border-color:rgba(94,151,192,.24) !important; }
[data-testid="stSidebar"] * { color:#233E53 !important; }
.eyebrow,.hero-label,.planner-hero-kicker,.plan-kicker { color:#287CA5 !important; }
.glass-hero,.planner-hero {
  background:linear-gradient(112deg,rgba(255,255,255,.98),rgba(223,241,251,.97) 55%,rgba(234,243,255,.97)) !important;
  border-color:rgba(93,158,197,.36) !important;
  box-shadow:0 16px 38px rgba(44,91,121,.10),inset 0 1px 0 #fff !important;
}
.hero-heading,.planner-hero-title,.plan-result-title { color:#1E3D55 !important; }
.hero-caption,.planner-hero-copy,.plan-result-copy { color:#58758A !important; }
.hero-status,.plan-source,.schedule-tag { color:#226F93 !important; background:rgba(75,158,201,.11) !important; border-color:rgba(75,158,201,.27) !important; }
.stat-card,[data-testid="stVerticalBlockBorderWrapper"] > div,.plan-result-head {
  background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(234,245,251,.97)) !important;
  border-color:rgba(103,158,190,.25) !important;
  box-shadow:0 10px 28px rgba(38,79,105,.07),inset 0 1px 0 #fff !important;
}
.stat-label,.stat-sub,.muted { color:#658094 !important; }
.stat-value,.schedule-title,.schedule-time { color:#23445B !important; }
.schedule-subject { color:#347FA2 !important; }
.schedule-description,.schedule-time span { color:#617D91 !important; }
.schedule-row,.task-row {
  background:linear-gradient(105deg,rgba(255,255,255,.98),rgba(236,246,252,.98)) !important;
  border:1px solid rgba(93,158,197,.32) !important;
  box-shadow:0 8px 24px rgba(35,77,105,.08),inset 0 1px 0 #fff !important;
}
.schedule-row:hover { border-color:rgba(40,124,165,.58) !important; box-shadow:0 12px 28px rgba(40,124,165,.14) !important; }
.schedule-icon { color:#226F93 !important; background:linear-gradient(145deg,#F2FAFE,#E0F2FB) !important; border:1px solid rgba(93,158,197,.36) !important; }
.schedule-break { background:linear-gradient(105deg,#F7FBFF,#EBF3FA) !important; border:1px solid rgba(115,155,205,.28) !important; }
.schedule-break .schedule-icon { color:#3B6FA5 !important; background:#E8F1FB !important; border-color:rgba(115,155,205,.34) !important; }
.schedule-break .schedule-tag { color:#34679C !important; background:rgba(82,135,195,.12) !important; border-color:rgba(115,155,205,.30) !important; }
.schedule-time strong { color:#1E3D55 !important; }
div.stButton > button { color:#28516A !important; background:linear-gradient(135deg,#fff,#EFF7FC) !important; border-color:rgba(94,151,192,.30) !important; }
div.stButton > button[kind="primary"] { color:#fff !important; background:linear-gradient(105deg,#287CA5,#4D9EC2 58%,#6B9FD0) !important; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#3C9FC5,#69B6D2,#8AADE1) !important; }
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,[data-baseweb="select"] > div { border-color:rgba(94,151,192,.32) !important; }
.startup-loader { background:radial-gradient(circle at 50% 45%,rgba(83,177,226,.15),transparent 28%),rgba(245,251,255,.98) !important; }
.loader-title { color:#23445B !important; }
.loader-subtitle { color:#658094 !important; }
.loader-star { color:#287CA5 !important; }
hr { border-color:rgba(94,151,192,.18) !important; }
"""

ROSE_CSS = """
.stApp {
  background:
    radial-gradient(ellipse at 10% 2%, rgba(235,154,185,.19), transparent 34%),
    radial-gradient(ellipse at 92% 10%, rgba(221,166,207,.17), transparent 32%),
    linear-gradient(135deg,#FFFAFC,#FDF0F5 56%,#FFFFFF) !important;
}
[data-testid="stHeader"] { background:rgba(255,250,252,.88) !important; border-color:rgba(197,127,157,.18) !important; }
[data-testid="stSidebar"] { background:linear-gradient(165deg,#FFFCFD,#F8EAF0) !important; border-color:rgba(197,127,157,.24) !important; }
[data-testid="stSidebar"] * { color:#553447 !important; }
.eyebrow,.hero-label,.planner-hero-kicker,.plan-kicker { color:#A65379 !important; }
.glass-hero,.planner-hero {
  background:linear-gradient(112deg,rgba(255,255,255,.98),rgba(255,229,239,.97) 55%,rgba(251,235,247,.97)) !important;
  border-color:rgba(204,133,163,.36) !important;
  box-shadow:0 16px 38px rgba(112,60,83,.09),inset 0 1px 0 #fff !important;
}
.hero-heading,.planner-hero-title,.plan-result-title { color:#4D2D3D !important; }
.hero-caption,.planner-hero-copy,.plan-result-copy { color:#806071 !important; }
.hero-status,.plan-source,.schedule-tag { color:#995171 !important; background:rgba(207,128,163,.11) !important; border-color:rgba(197,127,157,.27) !important; }
.stat-card,[data-testid="stVerticalBlockBorderWrapper"] > div,.plan-result-head {
  background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(252,238,244,.97)) !important;
  border-color:rgba(197,137,160,.25) !important;
  box-shadow:0 10px 28px rgba(94,49,67,.065),inset 0 1px 0 #fff !important;
}
.stat-label,.stat-sub,.muted { color:#896D7C !important; }
.stat-value,.schedule-title,.schedule-time { color:#583748 !important; }
.schedule-subject { color:#A65379 !important; }
.schedule-description,.schedule-time span { color:#866A79 !important; }
.schedule-row,.task-row {
  background:linear-gradient(105deg,rgba(255,255,255,.98),rgba(253,239,245,.98)) !important;
  border:1px solid rgba(204,133,163,.32) !important;
  box-shadow:0 8px 24px rgba(94,49,67,.075),inset 0 1px 0 #fff !important;
}
.schedule-row:hover { border-color:rgba(166,83,121,.58) !important; box-shadow:0 12px 28px rgba(166,83,121,.13) !important; }
.schedule-icon { color:#995171 !important; background:linear-gradient(145deg,#FFF5F9,#FCE5EF) !important; border:1px solid rgba(204,133,163,.36) !important; }
.schedule-break { background:linear-gradient(105deg,#FFF8FB,#F6EAF4) !important; border:1px solid rgba(185,135,180,.28) !important; }
.schedule-break .schedule-icon { color:#885284 !important; background:#F4E5F2 !important; border-color:rgba(185,135,180,.34) !important; }
.schedule-break .schedule-tag { color:#7E4A7A !important; background:rgba(165,110,160,.12) !important; border-color:rgba(185,135,180,.30) !important; }
.schedule-time strong { color:#4D2D3D !important; }
div.stButton > button { color:#70465A !important; background:linear-gradient(135deg,#fff,#FCF0F5) !important; border-color:rgba(197,127,157,.30) !important; }
div.stButton > button[kind="primary"] { color:#fff !important; background:linear-gradient(105deg,#A65379,#C4779A 58%,#D18BAA) !important; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#B65E85,#D181A2,#E4A8C2) !important; }
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,[data-baseweb="select"] > div { border-color:rgba(197,127,157,.32) !important; }
.startup-loader { background:radial-gradient(circle at 50% 45%,rgba(235,154,185,.15),transparent 28%),rgba(255,247,250,.98) !important; }
.loader-title { color:#583748 !important; }
.loader-subtitle { color:#896D7C !important; }
.loader-star { color:#A65379 !important; }
hr { border-color:rgba(197,127,157,.18) !important; }
"""

# Detect the OS/browser system theme on initial loadout via query param / JS bridge
_qp_sys = st.query_params.get("sys_theme", "")
if "app_theme" not in st.session_state:
    if _qp_sys == "dark":
        st.session_state.app_theme = "Midnight Purple"
    elif _qp_sys == "light":
        st.session_state.app_theme = "Lavender & White"
    else:
        st.session_state.app_theme = "Midnight Purple"

if "_theme_synced" not in st.session_state:
    st.session_state._theme_synced = True
    st.markdown(
        """<script>
        (function() {
            const url = new URL(window.parent.location.href);
            if (!url.searchParams.has('sys_theme')) {
                const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                url.searchParams.set('sys_theme', isDark ? 'dark' : 'light');
                window.parent.location.replace(url.toString());
            }
        })();
        </script>""",
        unsafe_allow_html=True,
    )

THEME_STYLES = {
    "Lavender & White": BASE_CSS + LIGHT_CSS,
    "Midnight Purple": BASE_CSS + PURPLE_CSS,
    "Ocean Blue": BASE_CSS + LIGHT_CSS + OCEAN_CSS,
    "Rose": BASE_CSS + LIGHT_CSS + ROSE_CSS,
}
ACTIVE_CSS = THEME_STYLES.get(st.session_state.app_theme, THEME_STYLES["Lavender & White"])
st.markdown(
    f"<style>{ACTIVE_CSS}</style>",
    unsafe_allow_html=True,
)

# Final theme layer: align Streamlit-native controls with the selected StudyFlow palette.
FRAMEWORK_THEME_PALETTES = {
    "Lavender & White": {
        "scheme": "light",
        "bg": "#FCFAFF",
        "surface": "#FFFFFF",
        "surface_alt": "#F2ECFB",
        "text": "#302542",
        "muted": "#766987",
        "border": "#D9CBEA",
        "accent": "#8B5FC7",
        "accent_dark": "#7043AC",
        "input": "#FFFFFF",
        "header": "rgba(252,250,255,.94)",
        "hover": "#EEE5F8",
        "selection": "#E9DDF7",
        "glow": "rgba(139,95,199,.18)",
        "glow_strong": "rgba(139,95,199,.34)",
    },
    "Midnight Purple": {
        "scheme": "dark",
        "bg": "#090611",
        "surface": "#21172F",
        "surface_alt": "#1A1128",
        "text": "#F5F1FF",
        "muted": "#C0ACDD",
        "border": "#59436F",
        "accent": "#A65CFF",
        "accent_dark": "#7436D9",
        "input": "#160D25",
        "header": "rgba(9,6,17,.96)",
        "hover": "#352249",
        "selection": "#432B61",
        "glow": "rgba(166,92,255,.22)",
        "glow_strong": "rgba(166,92,255,.42)",
    },
    "Ocean Blue": {
        "scheme": "light",
        "bg": "#F7FCFF",
        "surface": "#FFFFFF",
        "surface_alt": "#EAF4FA",
        "text": "#233E53",
        "muted": "#658094",
        "border": "#C8DDEB",
        "accent": "#287CA5",
        "accent_dark": "#206486",
        "input": "#FFFFFF",
        "header": "rgba(248,252,255,.96)",
        "hover": "#E1F0F8",
        "selection": "#D7EAF5",
        "glow": "rgba(40,124,165,.17)",
        "glow_strong": "rgba(40,124,165,.32)",
    },
    "Rose": {
        "scheme": "light",
        "bg": "#FFFAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#FCEFF4",
        "text": "#553447",
        "muted": "#896D7C",
        "border": "#E8C6D3",
        "accent": "#A65379",
        "accent_dark": "#85405F",
        "input": "#FFFFFF",
        "header": "rgba(255,250,252,.96)",
        "hover": "#F8E4EC",
        "selection": "#F4DCE6",
        "glow": "rgba(166,83,121,.18)",
        "glow_strong": "rgba(166,83,121,.34)",
    },
}


def build_framework_theme_css(theme_name: str) -> str:
    palette = FRAMEWORK_THEME_PALETTES.get(
        theme_name, FRAMEWORK_THEME_PALETTES["Lavender & White"]
    )
    css = r"""
/* StudyFlow theme palette applied to Streamlit's native framework widgets. */
:root, .stApp, [data-testid="stAppViewContainer"] {
  color-scheme: @SCHEME@ !important;
  --primary-color: @ACCENT@ !important;
  --background-color: @BG@ !important;
  --secondary-background-color: @SURFACE_ALT@ !important;
  --text-color: @TEXT@ !important;
  --st-color-primary: @ACCENT@ !important;
  --st-color-background: @BG@ !important;
  --st-color-secondary-background: @SURFACE_ALT@ !important;
  --st-color-text: @TEXT@ !important;
}
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
  background-color: @BG@ !important;
  color: @TEXT@ !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] {
  background: @HEADER@ !important;
  color: @TEXT@ !important;
}
[data-testid="stHeader"] button, [data-testid="stToolbar"] button,
[data-testid="stToolbar"] svg {
  color: @MUTED@ !important;
  fill: currentColor !important;
}
[data-testid="stSidebar"] {
  background: @SURFACE_ALT@ !important;
  border-right: 1px solid @BORDER@ !important;
  color: @TEXT@ !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] label {
  color: @TEXT@ !important;
}
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: @TEXT@ !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: @MUTED@ !important;
}

/* Text inputs, password inputs, number inputs, text areas and date fields. */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stDateInput input, .stTimeInput input, [data-baseweb="input"] input,
[data-baseweb="textarea"] textarea, [data-testid="stChatInput"] textarea {
  color: @TEXT@ !important;
  background: @INPUT@ !important;
  -webkit-text-fill-color: @TEXT@ !important;
  border-color: @BORDER@ !important;
  caret-color: @ACCENT@ !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
  color: @MUTED@ !important;
  opacity: .85 !important;
}
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
  background: @INPUT@ !important;
  border-color: @BORDER@ !important;
}

/* Select boxes and the dropdown menu rendered in a portal (covers Streamlit v1.67+ Emotion/BaseWeb). */
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  color: @TEXT@ !important;
  background-color: @INPUT@ !important;
  background: @INPUT@ !important;
  border-color: @BORDER@ !important;
}
[data-baseweb="select"] *,
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] svg,
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-baseweb="select"] * {
  color: @TEXT@ !important;
  fill: @TEXT@ !important;
  -webkit-text-fill-color: @TEXT@ !important;
}
[data-baseweb="popover"], [data-baseweb="menu"],
[role="listbox"], ul[role="listbox"] {
  color: @TEXT@ !important;
  background: @SURFACE@ !important;
  border: 1px solid @BORDER@ !important;
}
[role="option"], [data-baseweb="menu"] li {
  color: @TEXT@ !important;
  background: @SURFACE@ !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover {
  color: @TEXT@ !important;
  background: @HOVER@ !important;
}

/* Buttons: primary, secondary, form-submit and download. */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stBaseButton-secondary"] {
  color: @TEXT@ !important;
  background: @SURFACE@ !important;
  border: 1px solid @BORDER@ !important;
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  color: @ACCENT_DARK@ !important;
  border-color: @ACCENT@ !important;
  background: @HOVER@ !important;
}
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
  color: #FFFFFF !important;
  background: linear-gradient(110deg, @ACCENT_DARK@, @ACCENT@) !important;
  border: 1px solid @ACCENT@ !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
  color: #FFFFFF !important;
  filter: brightness(1.07);
}

/* Checkboxes, radio buttons, toggles and sliders. */
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label,
[data-testid="stToggle"] label, [data-testid="stSlider"] label {
  color: @TEXT@ !important;
}
[data-testid="stCheckbox"] svg, [data-testid="stRadio"] svg {
  color: @ACCENT@ !important;
}
[data-testid="stSlider"] [role="slider"] {
  background: @ACCENT@ !important;
  border-color: @ACCENT@ !important;
}
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, @ACCENT_DARK@, @ACCENT@) !important;
}

/* Forms, bordered containers, metrics and expanders. */
[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stForm"], [data-testid="stMetric"],
[data-testid="stExpander"] details, [data-testid="stPopover"] {
  color: @TEXT@ !important;
  border-color: @BORDER@ !important;
}
div[data-testid="stForm"], [data-testid="stExpander"] details,
[data-testid="stPopover"] {
  background: @SURFACE@ !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] svg {
  color: @TEXT@ !important;
}
[data-testid="stMetric"] {
  background: @SURFACE_ALT@ !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
  color: @MUTED@ !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
  color: @TEXT@ !important;
}

/* Alerts (st.info / st.success / st.warning), chat messages, chat input, tables and dataframe wrappers. */
[data-testid="stAlert"],
[data-testid="stAlert"] > div,
[data-testid="stNotification"],
[data-testid="stSidebar"] [data-testid="stAlert"],
[data-testid="stSidebar"] [data-testid="stAlert"] > div {
  color: @TEXT@ !important;
  background-color: @SURFACE_ALT@ !important;
  background: @SURFACE_ALT@ !important;
  border: 1px solid @BORDER@ !important;
}
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] strong,
[data-testid="stAlert"] svg,
[data-testid="stSidebar"] [data-testid="stAlert"] * {
  color: @TEXT@ !important;
  fill: @ACCENT@ !important;
}
[data-testid="stChatMessage"] {
  color: @TEXT@ !important;
  background: @SURFACE_ALT@ !important;
  border: 1px solid @BORDER@ !important;
}
[data-testid="stChatInput"] {
  background: @SURFACE@ !important;
  border: 1px solid @BORDER@ !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
  color: @TEXT@ !important;
  border-color: @BORDER@ !important;
}
hr { border-color: @BORDER@ !important; }
::selection { color: @TEXT@ !important; background: @SELECTION@ !important; }
"""
    replacements = {
        "@SCHEME@": palette["scheme"],
        "@BG@": palette["bg"],
        "@SURFACE@": palette["surface"],
        "@SURFACE_ALT@": palette["surface_alt"],
        "@TEXT@": palette["text"],
        "@MUTED@": palette["muted"],
        "@BORDER@": palette["border"],
        "@ACCENT@": palette["accent"],
        "@ACCENT_DARK@": palette["accent_dark"],
        "@INPUT@": palette["input"],
        "@HEADER@": palette["header"],
        "@HOVER@": palette["hover"],
        "@SELECTION@": palette["selection"],
    }
    for token, value in replacements.items():
        css = css.replace(token, value)

    # Light palettes get the same polished neon interaction feedback as Dark mode.
    # The glow hue follows the currently selected theme.
    if palette["scheme"] == "light":
        css += f"""
/* Soft neon button glow for light themes */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {{
  box-shadow: 0 4px 15px {palette["glow"]},
              0 0 0 1px rgba(255,255,255,.72) inset !important;
  transition: transform .18s ease, box-shadow .18s ease,
              border-color .18s ease, filter .18s ease !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 0 0 1px {palette["accent"]},
              0 7px 22px {palette["glow_strong"]},
              0 0 16px {palette["glow"]} !important;
}}
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {{
  box-shadow: 0 5px 18px {palette["glow_strong"]},
              0 0 13px {palette["glow"]},
              0 1px 0 rgba(255,255,255,.30) inset !important;
}}
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {{
  box-shadow: 0 0 0 1px {palette["accent"]},
              0 8px 25px {palette["glow_strong"]},
              0 0 20px {palette["glow_strong"]} !important;
}}
"""
    return css


st.markdown(
    f"<style>{build_framework_theme_css(st.session_state.app_theme)}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="startup-loader">
      <div class="loader-core">
        <div class="loader-ring"></div>
        <div class="loader-star">✦</div>
      </div>
      <div class="loader-title">STUDYFLOW AI</div>
      <div class="loader-subtitle">INITIALIZING YOUR WORKSPACE</div>
      <div class="loader-track"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- DATA ----------------
def load_data():
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return data.get("tasks", [])
        except (OSError, json.JSONDecodeError):
            return []
    return []

def save_data():
    try:
        DATA_FILE.write_text(
            json.dumps({"tasks": st.session_state.tasks}, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as error:
        st.error(f"Could not save tasks: {error}")

if "tasks" not in st.session_state:
    st.session_state.tasks = load_data()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_study_plan" not in st.session_state:
    st.session_state.last_study_plan = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
def get_configured_api_key() -> str:
    """Read the Gemini key from Streamlit secrets or an environment variable."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key

    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        # No local secrets.toml or cloud secret has been configured.
        return ""


def get_api_key() -> str:
    """Prefer a saved secret; use the sidebar input only as a temporary fallback."""
    return get_configured_api_key() or str(st.session_state.get("api_key", "")).strip()

def get_model() -> str:
    return str(st.session_state.get("model", DEFAULT_MODEL)).strip() or DEFAULT_MODEL

if "model" not in st.session_state:
    st.session_state.model = DEFAULT_MODEL

# ---------------- AI ----------------
def ask_ai(prompt: str, json_mode: bool = False) -> str:
    key = get_api_key()
    if not key:
        return "Add your Gemini API key in the sidebar under AI Settings to use the AI features."
    model = get_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    generation_config = {"temperature": 0.55 if json_mode else 0.7, "maxOutputTokens": 3500}
    if json_mode:
        # Gemini's JSON response mode makes the planner output easier to validate.
        generation_config["responseMimeType"] = "application/json"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        return f"Gemini API error ({error.code}):\n\n{details[:1500]}"
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as error:
        return f"Something went wrong while contacting Gemini: {error}"

def get_stats():
    tasks = st.session_state.tasks
    total = len(tasks)
    completed = sum(1 for task in tasks if task.get("done", False))
    pending = total - completed
    minutes = sum(int(task.get("minutes", 0)) for task in tasks if task.get("done", False))
    percentage = round(completed / total * 100) if total else 0
    return total, completed, pending, minutes, percentage

def page_header(title, subtitle):
    st.markdown(
        f"<div class='page-heading'><div class='eyebrow'>STUDYFLOW WORKSPACE</div><h1>{escape(title)}</h1><p class='muted'>{escape(subtitle)}</p></div>",
        unsafe_allow_html=True,
    )

def stat_card(label, value, subtitle, color):
    st.markdown(
        f"""<div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color:{color}">{value}</div>
        <div class="stat-sub">{subtitle}</div></div>""",
        unsafe_allow_html=True,
    )

def split_user_items(value: str) -> list[str]:
    """Split comma/semicolon/newline separated subjects or weak topics."""
    return [part.strip() for part in re.split(r"[,;\n]+", value or "") if part.strip()]


def make_local_timetable(subjects_text: str, weak_topics_text: str, available_hours: float,
                         start_time, grade: str, exam_date: date) -> dict:
    """Always build a complete timetable locally, even when Gemini is unavailable."""
    subjects = split_user_items(subjects_text) or ["General study"]
    weak_topics = split_user_items(weak_topics_text)
    total_minutes = max(30, int(round(float(available_hours) * 60)))
    block_count = max(1, math.ceil(total_minutes / 45))
    break_count = block_count - 1
    focus_minutes = total_minutes - (break_count * 5)
    base, extra = divmod(focus_minutes, block_count)
    durations = [base + (1 if index < extra else 0) for index in range(block_count)]

    activities = [
        ("Concept learning", "Understand the key ideas, then write a short explanation in your own words."),
        ("Practice questions", "Solve questions without looking at the answers; mark anything you need to revisit."),
        ("Active recall", "Close your notes and recall the main points, formulas, or definitions from memory."),
        ("Revision & error check", "Review mistakes, correct them, and finish with a quick self-test."),
    ]

    sessions = []
    for index, duration in enumerate(durations):
        subject = subjects[index % len(subjects)]
        if weak_topics and index < len(weak_topics):
            topic = weak_topics[index]
            activity = "Weak-topic focus"
            description = (
                f"Focus on {topic} in {subject}. Review one worked example, explain the method "
                "in your own words, then answer a few practice questions."
            )
        else:
            activity, description = activities[index % len(activities)]
            if weak_topics and index == len(weak_topics):
                description += f" Revisit your earlier weak topic: {weak_topics[0]}."
        sessions.append({
            "type": "study",
            "duration_minutes": int(duration),
            "activity": activity,
            "subject": subject,
            "description": description,
        })
        if index < len(durations) - 1:
            sessions.append({
                "type": "break",
                "duration_minutes": 5,
                "activity": "Screen-free break",
                "subject": "Recharge",
                "description": "Stand up, stretch, drink some water, and rest your eyes before the next block.",
            })

    days_left = max(0, (exam_date - date.today()).days)
    checklist = [
        "Complete the planned study blocks on most days this week.",
        "Do one mixed practice session and review every mistake.",
        "Use active recall instead of only rereading notes.",
        "Revisit weak topics and update the topics that need more practice.",
    ]
    if days_left <= 7:
        checklist.append("Use the final days for light revision, practice, and enough rest.")
    else:
        checklist.append("At the weekend, check progress and adjust next week's priorities.")

    return {
        "overview": f"A {total_minutes}-minute daily routine for Grade {grade}, with extra attention to your priority topics.",
        "sessions": sessions,
        "weekly_checklist": checklist,
        "tips": [
            "Keep your phone away during focus blocks.",
            "After each study block, try to explain what you learned without looking at your notes.",
        ],
        "source": "Personalised timetable",
        "grade": grade,
        "subjects": subjects,
        "exam_date": exam_date.isoformat(),
        "available_minutes": total_minutes,
        "start_time": start_time.strftime("%H:%M"),
    }


def parse_ai_timetable(raw_text: str, total_minutes: int) -> dict | None:
    """Validate Gemini's JSON. Return None if the timetable is incomplete or malformed."""
    if not raw_text or raw_text.startswith(("Gemini API error", "Something went wrong", "Add your Gemini")):
        return None
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first < 0 or last <= first:
        return None
    try:
        data = json.loads(cleaned[first:last + 1])
    except json.JSONDecodeError:
        return None

    raw_sessions = data.get("sessions") if isinstance(data, dict) else None
    if not isinstance(raw_sessions, list) or not raw_sessions or len(raw_sessions) > 40:
        return None

    sessions = []
    for item in raw_sessions:
        if not isinstance(item, dict):
            return None
        try:
            duration = int(item.get("duration_minutes", 0))
        except (TypeError, ValueError):
            return None
        kind = str(item.get("type", "study")).strip().lower()
        activity = str(item.get("activity", "")).strip()
        subject = str(item.get("subject", "General study")).strip()
        description = str(item.get("description", "")).strip()
        if duration < 1 or duration > 90 or not activity or not description:
            return None
        if kind not in {"study", "break"}:
            kind = "study"
        sessions.append({
            "type": kind,
            "duration_minutes": duration,
            "activity": activity,
            "subject": subject or "General study",
            "description": description,
        })

    scheduled_minutes = sum(item["duration_minutes"] for item in sessions)
    if abs(scheduled_minutes - total_minutes) > 2:
        return None
    if total_minutes > 60 and not any(item["type"] == "break" for item in sessions):
        return None
    if not any(item["type"] == "study" for item in sessions):
        return None

    checklist = data.get("weekly_checklist", [])
    tips = data.get("tips", [])
    if not isinstance(checklist, list):
        checklist = []
    if not isinstance(tips, list):
        tips = []
    return {
        "overview": str(data.get("overview", "Your personalised study routine is ready.")),
        "sessions": sessions,
        "weekly_checklist": [str(item) for item in checklist[:8] if str(item).strip()],
        "tips": [str(item) for item in tips[:5] if str(item).strip()],
        "source": "Gemini AI timetable",
    }


def add_clock_times(sessions: list[dict], start_time) -> list[dict]:
    """Assign trustworthy clock times locally instead of relying on AI time strings."""
    cursor = datetime.combine(date.today(), start_time)
    timed_sessions = []
    for session in sessions:
        duration = int(session["duration_minutes"])
        end = cursor + timedelta(minutes=duration)
        item = dict(session)
        item["start"] = cursor.strftime("%I:%M %p").lstrip("0")
        item["end"] = end.strftime("%I:%M %p").lstrip("0")
        timed_sessions.append(item)
        cursor = end
    return timed_sessions


def render_study_plan(plan: dict) -> None:
    """Render the plan as visual timetable cards rather than fragile Markdown tables."""
    sessions = plan["sessions"]
    total_minutes = sum(int(item["duration_minutes"]) for item in sessions)
    study_minutes = sum(int(item["duration_minutes"]) for item in sessions if item["type"] != "break")
    break_count = sum(1 for item in sessions if item["type"] == "break")
    st.markdown(
        f"""<div class="plan-result-head">
          <div class="plan-kicker">✦ YOUR STUDY ROUTINE</div>
          <div class="plan-result-title">Your timetable is ready.</div>
          <div class="plan-result-copy">{escape(plan.get('overview', 'A balanced routine built around your goals.'))}</div>
          <div class="plan-source">{escape(plan.get('source', 'Personalised timetable'))}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Total time", f"{total_minutes // 60}h {total_minutes % 60}m")
    with metric_cols[1]:
        st.metric("Focused study", f"{study_minutes // 60}h {study_minutes % 60}m")
    with metric_cols[2]:
        st.metric("Breaks", str(break_count))

    st.markdown("### Daily timetable")
    st.caption("Follow the order, and adjust the start time to match your day.")
    row_html = []
    for index, item in enumerate(sessions):
        is_break = item.get("type") == "break"
        kind_class = "schedule-break" if is_break else "schedule-focus"
        icon = "☕" if is_break else ("✦" if index == 0 else "◈")
        row_html.append(
            f"""<div class="schedule-row {kind_class}">
              <div class="schedule-time"><strong>{escape(item.get('start', ''))}</strong><span>{escape(item.get('end', ''))}</span></div>
              <div class="schedule-icon">{icon}</div>
              <div class="schedule-details"><div class="schedule-title">{escape(item.get('activity', 'Study session'))}</div>
                <div class="schedule-subject">{escape(item.get('subject', 'General study'))} · {int(item.get('duration_minutes', 0))} min</div>
                <div class="schedule-description">{escape(item.get('description', ''))}</div>
              </div>
              <div class="schedule-tag">{'BREAK' if is_break else 'FOCUS'}</div>
            </div>"""
        )
    st.markdown('<div class="schedule-list">' + ''.join(row_html) + '</div>', unsafe_allow_html=True)

    checklist = plan.get("weekly_checklist", [])
    if checklist:
        with st.container(border=True):
            st.markdown("### Weekly progress checklist")
            st.caption("Tick these off as you work through the week.")
            for index, item in enumerate(checklist):
                st.checkbox(item, key=f"weekly_plan_check_{index}")
    tips = plan.get("tips", [])
    if tips:
        with st.container(border=True):
            st.markdown("### Study smarter")
            for tip in tips:
                st.markdown(f"- {escape(str(tip))}")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("＋ Add study blocks to My Tasks", type="primary", use_container_width=True):
            existing = {
                (task.get("name"), task.get("subject"), int(task.get("minutes", 0)))
                for task in st.session_state.tasks
            }
            added = 0
            for item in sessions:
                if item.get("type") == "break":
                    continue
                task_key = (item["activity"], item["subject"], int(item["duration_minutes"]))
                if task_key in existing:
                    continue
                st.session_state.tasks.append({
                    "name": item["activity"],
                    "subject": item["subject"],
                    "minutes": int(item["duration_minutes"]),
                    "priority": "High" if "weak" in item["activity"].lower() else "Medium",
                    "deadline": plan.get("exam_date", "Not set"),
                    "done": False,
                    "created": date.today().isoformat(),
                })
                existing.add(task_key)
                added += 1
            save_data()
            st.success(f"Added {added} study block(s) to My Tasks.")
    with col_b:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Start", "End", "Activity", "Subject", "Duration (minutes)", "Description"])
        for item in sessions:
            writer.writerow([item.get("start"), item.get("end"), item.get("activity"),
                             item.get("subject"), item.get("duration_minutes"), item.get("description")])
        st.download_button(
            "↓ Download timetable CSV",
            data=buffer.getvalue(),
            file_name="studyflow_timetable.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<div class='brand'>✦ StudyFlow</div>", unsafe_allow_html=True)
    st.caption("YOUR PERSONAL STUDY WORKSPACE")
    st.markdown("---")
    st.markdown("<div class='eyebrow'>WORKSPACE</div>", unsafe_allow_html=True)

    pages = ["Dashboard", "My Tasks", "AI Planner", "AI Tutor"]
    for page in pages:
        if st.button(
            ("▣  " if page == st.session_state.page else "›  ") + page,
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if page == st.session_state.page else "secondary",
        ):
            st.session_state.page = page
            st.rerun()

    st.markdown("---")
    st.markdown("<div class='eyebrow'>APPEARANCE</div>", unsafe_allow_html=True)
    st.selectbox(
        "Workspace theme",
        ["Lavender & White", "Midnight Purple", "Ocean Blue", "Rose"],
        key="app_theme",
        help="Changes the StudyFlow colours for your current session.",
    )
    if st.session_state.app_theme == "Midnight Purple":
        st.info(
            "Synced with Dark mode. If native popups look bright, open the top-right ⋮ menu → Settings → Theme and select **Dark** (or **System**)."
        )
    else:
        st.info(
            "Synced with Light mode. If native popups look dark, open the top-right ⋮ menu → Settings → Theme and select **Light** (or **System**)."
        )

    st.markdown("---")
    st.markdown("<div class='eyebrow'>AI SETTINGS</div>", unsafe_allow_html=True)
    if get_configured_api_key():
        st.success("Gemini API key loaded securely from app secrets.")
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        st.text_input(
            "Gemini API Key",
            type="password",
            key="api_key",
            placeholder="Paste your Gemini API key",
            help="Temporary fallback only. For automatic loading, configure GEMINI_API_KEY in Streamlit Secrets."
        )
        st.caption("Set GEMINI_API_KEY in Streamlit app Secrets so you do not need to enter it every session.")
    st.selectbox(
        "AI Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        key="model"
    )

    st.markdown("---")
    st.markdown("<div class='eyebrow'>YOUR ACCOUNT</div>", unsafe_allow_html=True)
    st.markdown("**Student**")
    st.caption("Personal workspace")
    st.markdown("<div class='eyebrow'>POWERED BY GEMINI</div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if st.session_state.page == "Dashboard":
    st.markdown(
        """<div class="glass-hero">
        <div class="hero-label">STUDYFLOW // PERSONAL LEARNING SYSTEM</div>
        <div class="hero-heading">Your focus. Your future.</div>
        <div class="hero-caption">Your study command centre is ready. Track progress, organise tasks, and keep moving forward.</div>
        <div class="hero-status">● SYSTEM ONLINE &nbsp; | &nbsp; READY TO LEARN</div>
        </div>""",
        unsafe_allow_html=True,
    )
    total, completed, pending, minutes, percentage = get_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("TOTAL TASKS", total, "All your study goals", BLUE)
    with c2:
        stat_card("COMPLETED", completed, "Tasks finished", GREEN)
    with c3:
        stat_card("PENDING", pending, "Still to complete", ORANGE)
    with c4:
        stat_card("STUDY TIME", f"{minutes // 60}h {minutes % 60}m", "Time from completed tasks", PURPLE)

    st.write("")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("### Study Progress")
            st.caption("Your overall completion rate")
            st.markdown(f"<div style='font-size:42px;font-weight:800;color:{GREEN}'>{percentage}%</div>", unsafe_allow_html=True)
            st.progress(percentage / 100 if percentage else 0)
            st.caption(f"{completed} of {total} tasks completed")
    with right:
        with st.container(border=True):
            st.markdown("### Upcoming Tasks")
            st.caption("Your next study goals")
            upcoming = [task for task in st.session_state.tasks if not task.get("done", False)][:5]
            if not upcoming:
                st.success("You're all caught up! Add a task to get started.")
            else:
                for task in upcoming:
                    st.markdown(f"**○ {task['name']}**")
                    st.caption(f"{task.get('subject', 'General')} · {task.get('minutes', 0)} min · {task.get('deadline', 'Not set')}")

    if st.button("+ Add a task", type="primary"):
        st.session_state.page = "My Tasks"
        st.rerun()

# ---------------- TASKS ----------------
elif st.session_state.page == "My Tasks":
    page_header("My Tasks", "Keep track of everything you need to study.")
    tasks = st.session_state.tasks
    st.caption(f"{len(tasks)} tasks in total")

    with st.expander("+ New Task", expanded=not tasks):
        with st.form("new_task_form", clear_on_submit=True):
            task_name = st.text_input("Task name")
            subject = st.text_input("Subject")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=30)
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            deadline = st.date_input("Deadline (optional)", value=None)
            submitted = st.form_submit_button("Create Task", type="primary", use_container_width=True)
            if submitted:
                if not task_name.strip() or not subject.strip():
                    st.warning("Enter a task name and subject.")
                else:
                    due = deadline.isoformat() if deadline else "Not set"
                    st.session_state.tasks.append({
                        "name": task_name.strip(),
                        "subject": subject.strip(),
                        "minutes": int(duration),
                        "priority": priority,
                        "deadline": due,
                        "done": False,
                        "created": date.today().isoformat(),
                    })
                    save_data()
                    st.success("Task created!")
                    st.rerun()

    if not tasks:
        st.info("No tasks yet. Create your first study task above.")
    else:
        for index, task in enumerate(tasks):
            with st.container(border=True):
                col1, col2, col3 = st.columns([6, 2, 2])
                with col1:
                    mark = "✅" if task.get("done") else "◯"
                    st.markdown(f"**{mark} {task['name']}**")
                    st.caption(
                        f"{task.get('subject', 'General')} · {task.get('minutes', 0)} min · "
                        f"{task.get('priority', 'Medium')} priority · Due: {task.get('deadline', 'Not set')}"
                    )
                with col2:
                    st.caption("Completed" if task.get("done") else "Pending")
                    if st.button("Toggle status", key=f"toggle_{index}", use_container_width=True):
                        st.session_state.tasks[index]["done"] = not task.get("done", False)
                        save_data()
                        st.rerun()
                with col3:
                    st.caption(" ")
                    if st.button("Delete", key=f"delete_{index}", use_container_width=True):
                        st.session_state.tasks.pop(index)
                        save_data()
                        st.rerun()

# ---------------- AI PLANNER ----------------
elif st.session_state.page == "AI Planner":
    st.markdown(
        """<div class="planner-hero">
          <div class="planner-hero-kicker">STUDYFLOW AI  /  PERSONAL PLANNING</div>
          <div class="planner-hero-title">Build a study routine that works.</div>
          <div class="planner-hero-copy">Tell us what you are studying, where you need extra practice, and how much time you have. StudyFlow turns it into a timed routine with focus blocks, breaks, and a weekly checklist.</div>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("### ✦ Set up your study plan")
        st.caption("Only your grade and subjects are required. Weak topics help the planner personalise your sessions.")
        with st.form("planner_form", clear_on_submit=False):
            first_row = st.columns(2)
            with first_row[0]:
                grade = st.text_input("Grade / year", placeholder="e.g. 8")
                subjects = st.text_input("Subjects", placeholder="Maths, Science, English, Kannada...")
            with first_row[1]:
                available_hours = st.number_input(
                    "Daily study time (hours)", min_value=0.5, max_value=16.0,
                    value=3.0, step=0.5,
                )
                start_time = st.time_input(
                    "When do you want to start?",
                    value=datetime.strptime("16:00", "%H:%M").time(),
                )
            weak_topics = st.text_area(
                "Topics you want to improve (optional)",
                placeholder="For example: Algebra, Logarithms, Soil types",
                height=85,
            )
            exam_date = st.date_input("Next exam date", value=date.today())
            generate_plan = st.form_submit_button(
                "✦ Generate my timetable", type="primary", use_container_width=True
            )

    if generate_plan:
        if not grade.strip() or not subjects.strip():
            st.warning("Please enter your grade and at least one subject.")
        else:
            total_minutes = int(round(float(available_hours) * 60))
            local_plan = make_local_timetable(
                subjects, weak_topics, available_hours, start_time, grade.strip(), exam_date
            )
            plan = None
            if get_api_key():
                prompt = f"""You are StudyFlow AI, a careful school study-planning assistant.
Create a realistic daily study timetable using the student's details below.

STUDENT DETAILS
Grade: {grade.strip()}
Subjects: {subjects}
Weak topics to prioritise: {weak_topics.strip() or "No specific weak topics listed"}
Total time available: exactly {total_minutes} minutes (breaks count inside this time)
Preferred start time: {start_time.strftime("%I:%M %p")}
Exam date: {exam_date.isoformat()}
Existing tasks: {json.dumps(st.session_state.tasks, ensure_ascii=False)}

OUTPUT RULES
- Return ONLY valid JSON. Do not use Markdown, code fences, or a Markdown table.
- Use exactly these top-level keys: overview, sessions, weekly_checklist, tips.
- sessions must be a list of objects with exactly these fields: type, duration_minutes, activity, subject, description.
- type must be either "study" or "break".
- The sum of every session's duration_minutes MUST equal exactly {total_minutes}.
- Add a 5-minute break between focus blocks for plans longer than 60 minutes.
- Keep study blocks at 45 minutes or less.
- Put weak topics early in the schedule and spend extra attention on them.
- Include concept learning, practice questions, active recall, and revision where time allows.
- Make every description specific: say what to read, solve, write, recall, or review.
- weekly_checklist must contain 4 to 6 short actionable items.
- tips must contain 2 or 3 concise study tips.

JSON SHAPE EXAMPLE
{{
  "overview": "A balanced routine for today's study goals.",
  "sessions": [
    {{"type":"study","duration_minutes":35,"activity":"Algebra focus","subject":"Maths","description":"Review the method, solve examples, and check each answer."}},
    {{"type":"break","duration_minutes":5,"activity":"Short break","subject":"Recharge","description":"Stretch, drink water, and rest your eyes."}}
  ],
  "weekly_checklist": ["Practise weak topics", "Review mistakes"],
  "tips": ["Keep your phone away", "Use active recall"]
}}
The example is only a shape. Create enough sessions for the full {total_minutes} minutes."""
                with st.spinner("✦ Gemini is building your personalised timetable..."):
                    ai_text = ask_ai(prompt, json_mode=True)
                plan = parse_ai_timetable(ai_text, total_minutes)
                if plan is None:
                    st.info("Gemini did not return a complete timetable this time, so StudyFlow built one from your inputs instead.")
            else:
                st.info("Your timetable will work without an API key. Add a Gemini key in AI Settings for AI-personalised session ideas.")
                plan = local_plan

            if plan is None:
                plan = local_plan
            plan["sessions"] = add_clock_times(plan["sessions"], start_time)
            plan["grade"] = grade.strip()
            plan["subjects"] = split_user_items(subjects)
            plan["exam_date"] = exam_date.isoformat()
            plan["available_minutes"] = total_minutes
            plan["start_time"] = start_time.strftime("%H:%M")
            st.session_state.last_study_plan = plan

    saved_plan = st.session_state.get("last_study_plan")
    if saved_plan:
        render_study_plan(saved_plan)
    else:
        with st.container(border=True):
            st.markdown("### Your timetable will appear here")
            st.markdown("<p class='muted'>Fill in your subjects and available time, then select <b>Generate my timetable</b>. You will get timed study blocks, short breaks, and a weekly checklist.</p>", unsafe_allow_html=True)

# ---------------- AI TUTOR ----------------
elif st.session_state.page == "AI Tutor":
    page_header("AI Tutor", "Your personal AI learning assistant.")
    st.markdown(
        f"<div class='panel'><b>✦ StudyFlow AI</b><span style='float:right;color:{GREEN}'>Gemini powered</span><br><span class='muted'>Ask me to explain a topic, solve a practice question or organise your revision.</span></div>",
        unsafe_allow_html=True,
    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask StudyFlow AI a question...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        history = "\n".join(
            f"{'YOU' if item['role'] == 'user' else 'STUDYFLOW AI'}: {item['content']}"
            for item in st.session_state.chat_history[-12:]
        )
        prompt = f"""
You are StudyFlow AI, a friendly school tutor.
Help students understand concepts, solve academic questions,
prepare for exams and improve study habits.
Explain difficult concepts step by step.
Use simple language and examples.
Do not just give answers; explain the reasoning.
Be accurate and encouraging.

Conversation:
{history}

Answer the latest question.
"""
        with st.chat_message("assistant"):
            with st.spinner("StudyFlow AI is thinking..."):
                answer = ask_ai(prompt)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.caption("AI can make mistakes. Check important academic information.")
