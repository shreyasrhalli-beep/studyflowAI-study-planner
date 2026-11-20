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

"""

# Light theme styles, injected only when the in-app toggle is on.
LIGHT_CSS = """
.stApp {
  color:#18263A !important;
  background:
    radial-gradient(ellipse at 10% 4%,rgba(68,180,230,.15),transparent 32%),
    radial-gradient(ellipse at 92% 10%,rgba(151,126,238,.13),transparent 30%),
    linear-gradient(135deg,#F4F8FC,#EAF1F8 55%,#F7F9FD) !important;
  background-attachment:fixed !important;
}
[data-testid="stHeader"] {
  background:rgba(245,249,253,.78) !important;
  border-bottom:1px solid rgba(80,115,150,.10);
}
[data-testid="stSidebar"] {
  background:linear-gradient(165deg,rgba(239,247,252,.97),rgba(226,237,247,.98)) !important;
  border-right:1px solid rgba(89,133,165,.20) !important;
  box-shadow:10px 0 35px rgba(35,65,95,.08) !important;
}
[data-testid="stSidebar"] * { color:#20364D !important; }
h1,h2,h3,h4,p,label,[data-testid="stMarkdownContainer"] { color:#1B2D42; }
.muted { color:#62758A !important; }
.eyebrow { color:#167C9D !important; }
.glass-hero {
  background:linear-gradient(112deg,rgba(220,245,252,.94),rgba(226,232,255,.94) 55%,rgba(239,229,255,.94)) !important;
  border:1px solid rgba(90,151,184,.30) !important;
  box-shadow:0 16px 38px rgba(49,91,125,.12),inset 0 1px 0 rgba(255,255,255,.95) !important;
}
.hero-label { color:#167C9D !important; }
.hero-heading { color:#172E46 !important; }
.hero-caption { color:#526B80 !important; }
.hero-status {
  color:#147D69 !important; background:rgba(36,178,145,.10) !important;
  border-color:rgba(36,150,125,.28) !important;
}
.glass-hero:before { background:rgba(65,190,220,.13) !important; }
.glass-hero:after {
  border-color:rgba(73,151,185,.22) !important;
  box-shadow:0 0 0 18px rgba(73,151,185,.025),0 0 0 38px rgba(73,151,185,.018) !important;
}
.stat-card {
  background:linear-gradient(145deg,rgba(255,255,255,.91),rgba(232,242,250,.91)) !important;
  border:1px solid rgba(106,145,173,.24) !important;
  border-top-color:rgba(255,255,255,.98) !important;
  box-shadow:0 10px 28px rgba(42,75,105,.09),inset 0 1px 0 #fff !important;
}
.stat-card:hover {
  border-color:rgba(47,155,190,.50) !important;
  box-shadow:0 16px 34px rgba(42,116,150,.13) !important;
}
.stat-label { color:#627A8F !important; }
.stat-value { color:#1B344D !important; }
.stat-sub { color:#6D8193 !important; }
[data-testid="stVerticalBlockBorderWrapper"] > div {
  background:linear-gradient(145deg,rgba(255,255,255,.88),rgba(239,245,250,.92)) !important;
  border:1px solid rgba(112,147,173,.23) !important;
  box-shadow:0 10px 28px rgba(40,70,100,.08),inset 0 1px 0 #fff !important;
}
[data-testid="stMetric"] {
  background:rgba(255,255,255,.78) !important;
  border-color:rgba(112,147,173,.22) !important;
}
[data-testid="stMetricLabel"] { color:#63798D !important; }
[data-testid="stMetricValue"] { color:#1B344D !important; }
div[data-testid="stForm"] {
  background:rgba(255,255,255,.80) !important;
  border-color:rgba(112,147,173,.25) !important;
  box-shadow:0 8px 24px rgba(40,70,100,.06);
}
.task-row {
  background:rgba(255,255,255,.78) !important;
  border-color:rgba(112,147,173,.22) !important;
  color:#263D53 !important;
}
div.stButton > button {
  color:#25435D !important;
  background:rgba(255,255,255,.76) !important;
  border:1px solid rgba(98,143,174,.30) !important;
}
div.stButton > button:hover {
  color:#126D8B !important; border-color:#48A9C8 !important;
  box-shadow:0 6px 18px rgba(45,143,176,.14) !important;
}
div.stButton > button[kind="primary"] {
  color:#FFFFFF !important;
  background:linear-gradient(105deg,#247FA5,#586EC4) !important;
  border-color:transparent !important;
}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input {
  color:#20364D !important; background:rgba(255,255,255,.92) !important;
  border:1px solid rgba(101,140,169,.32) !important;
}
[data-baseweb="select"] > div {
  color:#20364D !important; background:rgba(255,255,255,.94) !important;
  border-color:rgba(101,140,169,.32) !important;
}
[data-baseweb="select"] * { color:#20364D !important; }
.stChatMessage {
  background:rgba(255,255,255,.82) !important;
  border-color:rgba(112,147,173,.23) !important;
}
.startup-loader {
  background:radial-gradient(circle at 50% 45%,rgba(0,197,255,.12),transparent 28%),
  radial-gradient(circle at 50% 55%,rgba(126,91,255,.10),transparent 38%),rgba(238,246,252,.97) !important;
}
.loader-title { color:#18364F !important; }
.loader-subtitle { color:#5F7D93 !important; }
.loader-star { color:#2B6C8F !important; text-shadow:0 0 14px rgba(84,223,255,.6) !important; }
hr { border-color:rgba(83,120,150,.18) !important; }

.planner-hero { background:linear-gradient(115deg,rgba(235,224,255,.98),rgba(225,232,255,.98) 58%,rgba(245,228,255,.96)) !important; border-color:rgba(139,103,195,.25) !important; }
.planner-hero-title { color:#2B1B47 !important; }
.planner-hero-kicker,.plan-kicker { color:#6940A3 !important; }
.planner-hero-copy,.plan-result-copy { color:#625477 !important; }
.plan-result-head { background:linear-gradient(110deg,rgba(244,237,255,.96),rgba(235,231,255,.96)) !important; border-color:rgba(139,103,195,.24) !important; }
.plan-result-title { color:#291A43 !important; }
.plan-source { color:#63428D !important; background:rgba(154,114,207,.10) !important; border-color:rgba(139,103,195,.24) !important; }
.schedule-row { background:linear-gradient(105deg,rgba(255,255,255,.94),rgba(241,237,250,.96)) !important; border-color:rgba(133,108,168,.22) !important; box-shadow:0 7px 19px rgba(48,33,72,.06) !important; }
.schedule-title,.schedule-time { color:#2B2140 !important; }
.schedule-time span,.schedule-description { color:#706582 !important; }
.schedule-subject { color:#7450A5 !important; }
.schedule-tag { color:#68439C !important; background:rgba(146,103,203,.08) !important; }
.schedule-break { background:linear-gradient(105deg,rgba(240,242,255,.96),rgba(235,237,250,.96)) !important; }

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
.schedule-list { display:flex; flex-direction:column; gap:9px; margin:12px 0 20px; }
.schedule-row { display:grid; grid-template-columns:105px 42px minmax(0,1fr) auto; gap:13px; align-items:center; padding:15px 17px; border-radius:15px; border:1px solid rgba(180,139,255,.22); background:linear-gradient(105deg,rgba(41,27,68,.80),rgba(18,12,34,.88)); box-shadow:0 8px 24px rgba(0,0,0,.16); transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease; }
.schedule-row:hover { transform:translateY(-2px); border-color:rgba(200,164,255,.50); box-shadow:0 12px 28px rgba(119,65,210,.14); }
.schedule-break { background:linear-gradient(105deg,rgba(39,42,73,.72),rgba(18,14,38,.84)); border-color:rgba(145,155,255,.20); }
.schedule-time { display:flex; flex-direction:column; gap:3px; color:#F0E7FF; font-size:13px; }
.schedule-time span { color:#AFA0CB; font-size:11px; }
.schedule-icon { width:36px; height:36px; display:grid; place-items:center; border-radius:12px; color:#E8D5FF; font-size:17px; background:rgba(151,91,236,.18); border:1px solid rgba(190,145,255,.24); }
.schedule-break .schedule-icon { background:rgba(111,130,225,.15); border-color:rgba(145,155,255,.23); }
.schedule-title { color:#F6F0FF; font-size:14px; font-weight:700; }
.schedule-subject { color:#C5A9F4; font-size:11px; margin-top:3px; }
.schedule-description { color:#B8ADC9; font-size:12px; line-height:1.55; margin-top:6px; }
.schedule-tag { color:#D4B9FF; font-size:9px; font-weight:800; letter-spacing:1px; padding:5px 8px; border-radius:20px; border:1px solid rgba(185,139,255,.24); background:rgba(142,81,224,.12); }
.schedule-break .schedule-tag { color:#BFCBFF; border-color:rgba(143,155,255,.22); background:rgba(105,120,210,.12); }
@media(max-width:700px) { .schedule-row { grid-template-columns:76px 34px minmax(0,1fr); gap:8px; padding:12px; } .schedule-tag { display:none; } .planner-hero-title { font-size:24px; } }

"""

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Inject exactly ONE style element. Streamlit may display CSS as page text
# if adjacent <style> blocks are passed in the same Markdown payload.
ACTIVE_CSS = BASE_CSS + (LIGHT_CSS if st.session_state.theme_mode == "Light" else PURPLE_CSS)
st.markdown(
    f"<style>{ACTIVE_CSS}</style>",
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

    def _on_theme_change():
        st.session_state.theme_mode = "Light" if st.session_state.theme_toggle else "Dark"
        st.rerun()

    st.toggle(
        "Light background",
        key="theme_toggle",
        value=st.session_state.theme_mode == "Light",
        on_change=_on_theme_change,
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
