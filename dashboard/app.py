from pathlib import Path

import sqlite3



import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

import streamlit as st

# st.html was added in newer Streamlit releases. Upgrade Streamlit if missing.
if not hasattr(st, "html"):
    st.error("This dashboard needs a newer Streamlit version for st.html(). Run: python -m pip install --upgrade streamlit")
    st.stop()



# =====================================================

# 1. PAGE CONFIGURATION

# =====================================================

st.set_page_config(

    page_title="IPL Bowling Intelligence",

    page_icon="🏏",

    layout="wide",

    initial_sidebar_state="expanded",

)



# =====================================================

# 2. INTERACTIVE DESIGN SYSTEM

# =====================================================

with st.sidebar:

    st.markdown("### 🎨 Dashboard Design Lab")

    visual_theme = st.selectbox(

        "Visual identity",

        ["Neon Arena", "Broadcast Gold", "Cyber Violet", "Arctic Blue", "Classic Stadium"],

        index=0,

        help="Switch the dashboard's visual style.",

    )

    motion_mode = st.select_slider(

        "Animation intensity",

        options=["Calm", "Balanced", "Full motion"],

        value="Full motion",

        help="Reduce movement if you prefer a calmer interface.",

    )

    chart_motion = st.toggle("Animated chart transitions", value=True)

    st.caption("Your data and calculations stay the same when you change styles.")



THEMES = {

    "Neon Arena": {"accent": "#00f5a0", "secondary": "#35d9ff", "glow": "#00f5a044", "hero": "#102a36,#124239,#10233a"},

    "Broadcast Gold": {"accent": "#ffd166", "secondary": "#ff8c42", "glow": "#ffd16644", "hero": "#32251a,#5b3d1c,#1c2938"},

    "Cyber Violet": {"accent": "#c4a1ff", "secondary": "#ff70d6", "glow": "#c4a1ff44", "hero": "#211735,#3b2050,#14253c"},

    "Arctic Blue": {"accent": "#7dd3fc", "secondary": "#a5f3fc", "glow": "#7dd3fc44", "hero": "#10283c,#16465a,#15243c"},

    "Classic Stadium": {"accent": "#8de969", "secondary": "#f4f1de", "glow": "#8de96933", "hero": "#18352b,#234a35,#172c35"},

}

THEME = THEMES[visual_theme]

MOTION_CSS = {

    "Full motion": "",

    "Balanced": "@keyframes calmFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}} .ipl-particle{animation-duration:8s!important}.ipl-stadium:before{animation-duration:30s!important}.ipl-ball,.ipl-bounce-ball{animation-duration:5s!important}.score-ticker-track{animation-duration:38s!important}",

    "Calm": "*,*::before,*::after{animation-duration:0.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:0.01ms!important}.ipl-particle{display:none!important}.ipl-stadium:before,.ipl-hero:after{display:none!important}",

}[motion_mode]



# =====================================================

# 3. PREMIUM ANIMATED UI

# =====================================================

st.markdown(r"""

<style>

:root{--bg:#07111b;--panel:#101e2a;--green:#00f5a0;--cyan:#35d9ff;--orange:#ffad55;--muted:#a6bbc9}

.stApp{background:radial-gradient(ellipse at 8% 0%,#123b37 0%,transparent 33%),radial-gradient(ellipse at 95% 20%,#13294a 0%,transparent 35%),linear-gradient(145deg,#07111b,#0a1420 60%,#101b28);color:#f4f8fb}

[data-testid="stHeader"]{background:transparent}

.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1550px}

h1,h2,h3{color:#f4f8fb!important}

p,label{color:var(--muted)}

@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}

@keyframes gradientFlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

@keyframes ballRoll{0%{transform:translateX(0) rotate(0deg)}50%{transform:translateX(35px) rotate(180deg)}100%{transform:translateX(0) rotate(360deg)}}

@keyframes glowPulse{0%,100%{box-shadow:0 0 10px #00f5a010}50%{box-shadow:0 0 23px #00f5a02b}}

@keyframes lightSweep{0%{background-position:-200% 0}100%{background-position:200% 0}}

@keyframes liveDot{0%,100%{opacity:1}50%{opacity:.35}}

@keyframes stadiumRotate{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

@keyframes particleFloat{0%,100%{transform:translateY(0) scale(.7);opacity:.3}50%{transform:translateY(-24px) scale(1.3);opacity:1}}

@keyframes ballBounce{0%,100%{transform:translateY(0) rotate(0)}45%{transform:translateY(-28px) rotate(160deg)}60%{transform:translateY(-30px) rotate(200deg)}}

@keyframes scoreShimmer{0%,15%{background-position:150% 0}75%,100%{background-position:-150% 0}}

@keyframes tickerMove{from{transform:translateX(0)}to{transform:translateX(-50%)}}

@keyframes underlineFlow{from{background-position:100% 0}to{background-position:-100% 0}}

.ipl-hero{position:relative;overflow:hidden;padding:30px;margin-bottom:20px;border-radius:23px;background:linear-gradient(115deg,#102a36,#124239,#10233a,#102a36);background-size:300% 300%;animation:gradientFlow 12s ease infinite;border:1px solid #00f5a044;box-shadow:0 12px 38px #00000032}

.ipl-hero:after{content:"";position:absolute;top:0;left:-100%;width:55%;height:100%;background:linear-gradient(110deg,transparent,#ffffff08,transparent);animation:lightSweep 7s ease-in-out infinite;pointer-events:none}

.ipl-kicker{display:inline-flex;align-items:center;gap:8px;color:var(--green);font-size:11px;font-weight:850;letter-spacing:3px}

.ipl-live-dot{width:8px;height:8px;display:inline-block;border-radius:50%;background:var(--green);animation:liveDot 1.6s ease-in-out infinite}

.ipl-hero h1{margin:12px 0 8px;font-size:clamp(27px,4vw,43px);font-weight:850;letter-spacing:-1.3px;color:white!important}

.ipl-hero p{margin:0;color:#bed3dc;font-size:15px}

.ipl-ball{display:inline-block;font-size:48px;animation:ballRoll 4s ease-in-out infinite;filter:drop-shadow(0 0 12px #00f5a044)}

.ipl-stadium{position:relative;overflow:hidden;min-height:155px;padding:22px;margin:12px 0 24px;border-radius:20px;border:1px solid #00f5a055;background:radial-gradient(ellipse at 50% 130%,#12684b 0%,transparent 50%),linear-gradient(180deg,#081522,#102b37);isolation:isolate}

.ipl-stadium:before{content:"";position:absolute;inset:-80% -30%;z-index:-1;background:conic-gradient(from 0deg at 50% 50%,transparent 0deg,#00f5a012 35deg,transparent 75deg,#35d9ff12 130deg,transparent 180deg,#00f5a012 235deg,transparent 300deg);animation:stadiumRotate 18s linear infinite}

.ipl-particle{position:absolute;width:5px;height:5px;border-radius:50%;background:#00f5a0;box-shadow:0 0 12px #00f5a0;animation:particleFloat 5s ease-in-out infinite}

.p1{left:12%;top:25%;animation-delay:0s}.p2{left:28%;top:70%;animation-delay:1s}.p3{left:68%;top:30%;animation-delay:2s}.p4{left:86%;top:65%;animation-delay:1.5s}.p5{left:51%;top:18%;animation-delay:.5s}

.ipl-bounce-ball{display:inline-block;font-size:42px;transform-origin:bottom center;animation:ballBounce 1.15s ease-in-out infinite;filter:drop-shadow(0 0 9px #ff765b77)}

.neon-label{color:#00f5a0;font-weight:850;letter-spacing:2px;text-shadow:0 0 12px #00f5a044}

.animated-underline{width:100%;height:2px;border-radius:3px;background:linear-gradient(90deg,transparent,#00f5a0,#35d9ff,transparent);background-size:200% 100%;animation:underlineFlow 3s linear infinite}

.score-ticker{overflow:hidden;white-space:nowrap;padding:13px 0;margin:12px 0 22px;border-top:1px solid #00f5a033;border-bottom:1px solid #00f5a033;background:#0c1924aa}

.score-ticker-track{display:inline-block;min-width:max-content;animation:tickerMove 26s linear infinite;color:#c4d9e4;font-size:12px;font-weight:750;letter-spacing:2px}

.score-ticker-track span{margin-right:55px}.score-ticker:hover .score-ticker-track{animation-play-state:paused}

div[data-testid="stMetric"]{position:relative;overflow:hidden;background:linear-gradient(145deg,#142735,#0c1924);border:1px solid #34506066;border-radius:18px;padding:18px 20px;min-height:105px;animation:fadeUp .65s ease both,glowPulse 4s ease-in-out infinite;transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease}

div[data-testid="stMetric"]:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(110deg,transparent 25%,#ffffff08 45%,#00f5a015 50%,transparent 70%);background-size:250% 100%;animation:scoreShimmer 6s ease-in-out infinite}

div[data-testid="stMetric"]:hover{transform:translateY(-5px);border-color:#00f5a0aa;box-shadow:0 12px 28px #00f5a015}

div[data-testid="stMetricLabel"]{color:#a9c0cc!important;font-size:13px}

div[data-testid="stMetricValue"]{color:var(--green)!important;font-weight:850;letter-spacing:-.5px}

h2{padding-bottom:10px;border-bottom:1px solid #00f5a028}

h3{color:#dcebf2!important}

/* Original dashboard details: glass panels, clean controls, and section markers */

[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;background:#0a1721;padding:8px;border:1px solid #29404d;border-radius:15px}

[data-testid="stTabs"] [data-baseweb="tab"]{height:44px;padding:0 18px;border-radius:10px;transition:all .25s ease}

[data-testid="stTabs"] [data-baseweb="tab"]:hover{background:#17313c;color:#fff}

[data-testid="stTabs"] [aria-selected="true"]{background:linear-gradient(110deg,#123b37,#142f40);box-shadow:inset 0 0 0 1px #00f5a055}

div[data-testid="stExpander"]{background:#0e1d28;border:1px solid #29404d;border-radius:14px}

div[data-testid="stDataFrame"],div[data-testid="stTable"]{border:1px solid #29404d;border-radius:14px;overflow:hidden}

.eyebrow{color:#00f5a0;font-size:11px;font-weight:850;letter-spacing:2.5px;text-transform:uppercase}

.st-key-analytics_refresh button{border:1px solid #00f5a088}

@keyframes chartIntro{from{opacity:0;transform:translateY(12px) scale(.99)}to{opacity:1;transform:translateY(0) scale(1)}}

div[data-testid="stPlotlyChart"]{background:linear-gradient(145deg,#101f2b,#0d1924);border:1px solid #31475688;border-radius:17px;padding:7px;animation:fadeUp .7s ease both;transition:border-color .25s ease,box-shadow .25s ease,transform .25s ease}

div[data-testid="stPlotlyChart"]:hover{border-color:#00f5a0;box-shadow:0 0 7px #00f5a033,0 0 24px #00f5a018;transform:translateY(-2px)}

section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a1620,#101f2b);border-right:1px solid #29404d}

div[data-testid="stSelectbox"] label,div[data-testid="stNumberInput"] label{color:#c7d9e3!important;font-weight:600}

div[data-baseweb="select"]>div{background:#122330;border-color:#36505f;border-radius:10px}

button[data-baseweb="tab"]{color:#a6bbc9;font-weight:700}button[data-baseweb="tab"][aria-selected="true"]{color:var(--green)!important}div[data-baseweb="tab-highlight"]{background-color:var(--green)}

.stButton>button{background:linear-gradient(100deg,#00f5a0,#35d9ff);color:#06151b;border:none;border-radius:11px;font-weight:800;transition:transform .2s ease,box-shadow .2s ease}.stButton>button:hover{transform:translateY(-2px);box-shadow:0 7px 22px #00f5a033;color:#06151b}

hr{border-color:#29404d}[data-testid="stCaptionContainer"]{color:#8da7b7}

@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}


/* Cinematic cricket field: subtle motion behind the dashboard content */
.ipl-motion-layer{position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:0;isolation:isolate;opacity:.72}
.ipl-motion-layer:before{content:"";position:absolute;inset:0;background:
 radial-gradient(ellipse at 50% 115%,rgba(0,170,95,.13),transparent 47%),
 repeating-linear-gradient(112deg,transparent 0 115px,rgba(110,220,170,.025) 116px 118px,transparent 119px 230px);
}
.main .block-container{position:relative;z-index:1}
.ipl-bg-ball{position:absolute;width:19px;height:19px;border-radius:50%;background:radial-gradient(circle at 30% 25%,#ffb2a3 0,#d83b3b 32%,#7d111b 78%);box-shadow:0 0 12px #ff34342b,inset -3px -3px 5px #33000b88;opacity:.36}
.ipl-bg-ball:after{content:"";position:absolute;left:7px;top:1px;width:5px;height:17px;border-left:1px dashed #ffe0d9b0;border-right:1px dashed #ffe0d970;border-radius:50%;transform:rotate(28deg)}
.ipl-bg-ball.b1{top:12%;left:-5%;animation:ballFlightA 19s linear infinite}
.ipl-bg-ball.b2{top:31%;left:-8%;width:12px;height:12px;animation:ballFlightB 23s linear 2s infinite}
.ipl-bg-ball.b3{top:70%;left:-6%;animation:ballFlightC 21s linear 5s infinite}
.ipl-bg-ball.b4{top:88%;left:-4%;width:14px;height:14px;animation:ballFlightA 25s linear 8s infinite}
.ipl-bg-ball.b5{top:47%;left:-7%;width:10px;height:10px;animation:ballFlightB 17s linear 4s infinite}
.ipl-bg-ball.b6{top:5%;left:-7%;width:13px;height:13px;animation:ballFlightC 27s linear 1s infinite}
.ipl-bg-ball.b7{top:58%;left:-4%;animation:ballFlightA 22s linear 11s infinite}
.ipl-bg-ball.b8{top:22%;left:-5%;width:11px;height:11px;animation:ballFlightC 20s linear 7s infinite}
.ipl-bg-ball.b9{top:78%;left:-6%;width:16px;height:16px;animation:ballFlightB 26s linear 9s infinite}
.ipl-bg-ball.b10{top:39%;left:-5%;animation:ballFlightA 24s linear 3s infinite}
.ipl-bg-ball.b11{top:95%;left:-8%;width:10px;height:10px;animation:ballFlightC 18s linear 6s infinite}
.ipl-bg-ball.b12{top:63%;left:-6%;width:13px;height:13px;animation:ballFlightB 21s linear 12s infinite}
.ipl-bg-bat{position:absolute;width:13px;height:100px;border-radius:7px 7px 4px 4px;background:linear-gradient(90deg,#5c351a,#c58b4b 28%,#f0c17a 52%,#98602c 85%,#4b2b17);box-shadow:0 0 16px #e7ad5b20;opacity:.12;transform-origin:50% 85%}
.ipl-bg-bat:before{content:"";position:absolute;width:8px;height:33px;left:2.5px;bottom:-27px;border-radius:3px;background:repeating-linear-gradient(0deg,#18222a 0 4px,#c8d2d6 5px 7px)}
.ipl-bg-bat.bat1{left:12%;top:12%;animation:batSwingA 12s ease-in-out infinite}
.ipl-bg-bat.bat2{right:13%;top:53%;animation:batSwingB 15s ease-in-out 2s infinite}
.ipl-bg-bat.bat3{left:78%;top:8%;transform:rotate(45deg);animation:batSwingA 17s ease-in-out 4s infinite}
.ipl-bg-bat.bat4{left:37%;top:78%;animation:batSwingB 14s ease-in-out 1s infinite}
@keyframes ballFlightA{0%{transform:translate3d(-5vw,0,0) rotate(0)}30%{transform:translate3d(35vw,-12vh,0) rotate(420deg)}65%{transform:translate3d(75vw,8vh,0) rotate(900deg)}100%{transform:translate3d(115vw,-4vh,0) rotate(1440deg)}}
@keyframes ballFlightB{0%{transform:translate3d(-5vw,0,0) rotate(0)}35%{transform:translate3d(38vw,14vh,0) rotate(540deg)}70%{transform:translate3d(78vw,-9vh,0) rotate(1080deg)}100%{transform:translate3d(115vw,3vh,0) rotate(1620deg)}}
@keyframes ballFlightC{0%{transform:translate3d(-5vw,0,0) rotate(0)}25%{transform:translate3d(28vw,8vh,0) rotate(360deg)}60%{transform:translate3d(72vw,-14vh,0) rotate(900deg)}100%{transform:translate3d(115vw,7vh,0) rotate(1620deg)}}
@keyframes batSwingA{0%,100%{rotate:-18deg}45%{rotate:20deg}55%{rotate:3deg}}
@keyframes batSwingB{0%,100%{rotate:15deg}40%{rotate:-24deg}58%{rotate:5deg}}
@media(max-width:700px){.ipl-bg-bat{opacity:.07;scale:.72}.ipl-bg-ball{opacity:.24}}
@media(prefers-reduced-motion:reduce){.ipl-motion-layer *{animation:none!important}}


/* Extra cinematic match-night effects */
.ipl-motion-layer{opacity:.82}
.ipl-motion-layer:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(115deg,transparent 0 35%,rgba(52,217,255,.035) 48%,transparent 60%),radial-gradient(ellipse at 50% -20%,rgba(255,255,255,.09),transparent 45%);background-size:220% 100%,100% 100%;animation:stadiumSweep 15s linear infinite}
@keyframes stadiumSweep{0%{background-position:-120% 0,0 0}100%{background-position:220% 0,0 0}}
/* Stumps glow softly in the distance */
.ipl-bg-stumps{position:absolute;left:50%;top:50%;width:44px;height:78px;transform:translate(-50%,-50%);opacity:.10;filter:drop-shadow(0 0 12px #ffd166);animation:stumpsPulse 5s ease-in-out infinite}
.ipl-bg-stumps:before{content:"";position:absolute;left:2px;right:2px;top:0;height:6px;border-radius:3px;background:#ffe2a6;box-shadow:0 0 8px #ffd166}
.ipl-bg-stumps:after{content:"";position:absolute;left:5px;top:5px;width:5px;height:65px;border-radius:3px;background:linear-gradient(90deg,#8a5b2b,#ffe0a0,#9c6b35);box-shadow:14px 0 0 #c89752,28px 0 0 #9c6b35}
@keyframes stumpsPulse{0%,100%{opacity:.055;scale:.92}50%{opacity:.15;scale:1.08}}
/* Fast little stadium light streaks */
.ipl-light-streak{position:absolute;height:2px;width:110px;border-radius:5px;background:linear-gradient(90deg,transparent,#35d9ff,transparent);opacity:0;filter:drop-shadow(0 0 5px #35d9ff);animation:streakAcross 9s linear infinite}
.ipl-light-streak.s1{top:18%;left:-15%;animation-delay:0s}.ipl-light-streak.s2{top:48%;left:-15%;animation-delay:3s}.ipl-light-streak.s3{top:76%;left:-15%;animation-delay:6s}
@keyframes streakAcross{0%{transform:translateX(0) rotate(-8deg);opacity:0}8%{opacity:.48}35%{opacity:.22}55%,100%{transform:translateX(125vw) rotate(-8deg);opacity:0}}
/* Extra balls move on curved paths, at varied sizes and speeds */
.ipl-bg-ball.b13{top:15%;left:-5%;width:8px;height:8px;animation:ballFlightB 14s linear 1s infinite}
.ipl-bg-ball.b14{top:53%;left:-5%;width:22px;height:22px;opacity:.22;animation:ballFlightC 29s linear 8s infinite}
.ipl-bg-ball.b15{top:83%;left:-5%;width:9px;height:9px;animation:ballFlightA 16s linear 5s infinite}
.ipl-bg-ball.b16{top:35%;left:-5%;width:15px;height:15px;animation:ballFlightB 18s linear 10s infinite}
@media(max-width:700px){.ipl-bg-stumps,.ipl-light-streak{display:none}.ipl-motion-layer{opacity:.48}}
@media(prefers-reduced-motion:reduce){.ipl-motion-layer:after,.ipl-bg-stumps,.ipl-light-streak{animation:none!important}}

</style>

""", unsafe_allow_html=True)




st.html("""
<div class="ipl-motion-layer" aria-hidden="true">
  <span class="ipl-bg-ball b1"></span><span class="ipl-bg-ball b2"></span>
  <span class="ipl-bg-ball b3"></span><span class="ipl-bg-ball b4"></span>
  <span class="ipl-bg-ball b5"></span><span class="ipl-bg-ball b6"></span>
  <span class="ipl-bg-ball b7"></span><span class="ipl-bg-ball b8"></span>
  <span class="ipl-bg-ball b9"></span><span class="ipl-bg-ball b10"></span>
  <span class="ipl-bg-ball b11"></span><span class="ipl-bg-ball b12"></span>
  <span class="ipl-bg-bat bat1"></span><span class="ipl-bg-bat bat2"></span>
  <span class="ipl-bg-bat bat3"></span><span class="ipl-bg-bat bat4"></span>
</div>
""")

# Runtime theme skin: lets the dashboard switch visual identity without touching data.

st.markdown(f"""

<style>

:root{{--green:{THEME['accent']};--cyan:{THEME['secondary']};--theme-glow:{THEME['glow']}}}

.ipl-hero{{background:linear-gradient(115deg,{THEME['hero']});background-size:300% 300%;}}

.ipl-kicker,.neon-label,.eyebrow,div[data-testid="stMetricValue"]{{color:{THEME['accent']}!important}}

.ipl-live-dot{{background:{THEME['accent']};box-shadow:0 0 13px {THEME['glow']}}}

.animated-underline{{background-image:linear-gradient(90deg,transparent,{THEME['accent']},{THEME['secondary']},transparent)}}

.ipl-stadium{{border-color:{THEME['glow']}}}

[data-testid="stTabs"] [aria-selected="true"]{{box-shadow:inset 0 0 0 1px {THEME['glow']}}}

.stButton>button{{background:linear-gradient(100deg,{THEME['accent']},{THEME['secondary']})}}

div[data-testid="stMetric"]:hover{{border-color:{THEME['accent']};box-shadow:0 12px 28px {THEME['glow']}}}

div[data-testid="stPlotlyChart"]:hover{{border-color:{THEME['accent']};box-shadow:0 0 24px {THEME['glow']}}}

{MOTION_CSS}

</style>

""", unsafe_allow_html=True)



# Extra motion and visual polish for the main Streamlit dashboard
st.markdown("""
<style>
:root{--accent:#00f5a0;--secondary:#35d9ff;--glow:#00f5a044}
.stApp{background-size:180% 180%;animation:appAurora 24s ease-in-out infinite}
@keyframes appAurora{0%,100%{background-position:0% 30%}50%{background-position:100% 70%}}
.block-container{animation:contentReveal .75s cubic-bezier(.2,.7,.2,1) both}
@keyframes contentReveal{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
div[data-testid="stMetric"]{position:relative;overflow:hidden;border:1px solid #ffffff12;border-radius:18px;padding:18px 18px 14px;background:linear-gradient(145deg,#102331dd,#0b1925ee);box-shadow:0 8px 25px #00000020;transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease;animation:cardRise .65s both}
div[data-testid="stMetric"]:before{content:"";position:absolute;inset:0 auto 0 -120%;width:70%;background:linear-gradient(100deg,transparent,#ffffff12,transparent);transform:skewX(-18deg);animation:cardShine 8s ease-in-out infinite;pointer-events:none}
div[data-testid="stMetric"]:hover{transform:translateY(-5px);border-color:var(--accent);box-shadow:0 15px 35px var(--glow)}
div[data-testid="stMetric"] label{font-weight:700;letter-spacing:.3px}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-weight:900;letter-spacing:-.7px}
@keyframes cardRise{from{opacity:0;transform:translateY(14px) scale(.985)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes cardShine{0%,65%{left:-120%}85%,100%{left:160%}}
div[data-testid="stPlotlyChart"]{border:1px solid #ffffff10;border-radius:18px;padding:7px;background:linear-gradient(145deg,#0d1c28aa,#10233155);transition:transform .3s ease,border-color .3s ease,box-shadow .3s ease}
div[data-testid="stPlotlyChart"]:hover{transform:translateY(-2px);border-color:var(--accent);box-shadow:0 10px 30px var(--glow)}
.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid #ffffff18}
.stTabs [data-baseweb="tab"]{border-radius:12px 12px 0 0;padding:10px 15px;transition:background .25s ease,color .25s ease,transform .25s ease}
.stTabs [data-baseweb="tab"]:hover{background:#ffffff0b;transform:translateY(-2px)}
.stTabs [aria-selected="true"]{background:linear-gradient(120deg,#00f5a018,#35d9ff0d);border-bottom:2px solid var(--accent)}
.stButton>button{border:1px solid #ffffff20;border-radius:12px;font-weight:800;transition:transform .2s ease,box-shadow .2s ease}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 22px var(--glow)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#091621,#0c1c29 55%,#101d2b);border-right:1px solid #ffffff10}
@media(prefers-reduced-motion:reduce){.stApp,.block-container,div[data-testid="stMetric"],div[data-testid="stMetric"]:before,div[data-testid="stPlotlyChart"]{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

# Render the hero in an isolated HTML component so Streamlit never treats tags as code.
import streamlit.components.v1 as components

components.html("""
<!doctype html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box} body{margin:0;background:transparent;font-family:Arial,sans-serif;color:#fff}
.ipl-hero,.ipl-stadium{position:relative;isolation:isolate;overflow:hidden;margin:12px 0 18px;padding:28px;border:1px solid #087f70;border-radius:22px;background:linear-gradient(120deg,#071827,#064e43,#101b32);box-shadow:0 0 24px #00f5a018}
.ipl-hero{background-size:250% 250%;animation:arena 12s ease infinite;min-height:185px}
/* Sport animation layer lives inside the headline iframe, so it appears behind the text */
.sport-motion{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:-1;opacity:.78}
.sport-motion:before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 120%,#00f5a020,transparent 58%),repeating-linear-gradient(110deg,transparent 0 70px,#ffffff05 72px 74px,transparent 76px 145px);animation:fieldDrift 16s linear infinite}
.fly-ball{position:absolute;left:-8%;top:20%;font-size:23px;filter:drop-shadow(0 0 8px #ff3b3b88);animation:headingBall 9s linear infinite}
.fly-ball.ball-two{top:68%;font-size:17px;animation-duration:12s;animation-delay:-4s}
.fly-ball.ball-three{top:38%;font-size:13px;animation-duration:7s;animation-delay:-2s}
.swing-bat{position:absolute;width:14px;height:104px;right:12%;top:10%;border-radius:8px 8px 4px 4px;transform-origin:50% 85%;background:linear-gradient(90deg,#67401f,#b77b3e 24%,#f3d19a 50%,#a56a32 80%,#59351b);box-shadow:0 0 15px #ffcf7a40;opacity:.24;animation:headingBatSwing 4.8s ease-in-out infinite}
.swing-bat:after{content:"";position:absolute;width:8px;height:29px;left:3px;bottom:-24px;border-radius:3px;background:repeating-linear-gradient(0deg,#18232d 0 4px,#e2e8ec 5px 7px)}
.swing-bat.bat-two{right:34%;top:35%;height:75px;opacity:.14;animation-duration:6.5s;animation-delay:-2s}
@keyframes headingBall{0%{transform:translate(-5vw,25px) rotate(0);opacity:0}8%{opacity:.8}45%{transform:translate(48vw,-35px) rotate(540deg);opacity:.65}90%{opacity:.4}100%{transform:translate(110vw,20px) rotate(1200deg);opacity:0}}
@keyframes headingBatSwing{0%,100%{rotate:-24deg}35%{rotate:20deg}52%{rotate:42deg}72%{rotate:-5deg}}
@keyframes fieldDrift{0%,100%{background-position:0 0,0 0}50%{background-position:100% 0,100px 0}}
.ipl-hero .row,.ipl-stadium .row,.ipl-stadium .animated-underline{position:relative;z-index:1}
.ipl-hero h1{text-shadow:0 2px 22px #00f5a01b}
.ipl-stadium{min-height:170px}
.ipl-kicker,.neon-label{font-size:11px;font-weight:800;letter-spacing:2px;color:#00f5a0}
.ipl-live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;background:#00f5a0;box-shadow:0 0 12px #00f5a0;animation:pulse 1.5s infinite}
h1{font-size:clamp(26px,4vw,42px);margin:15px 0;font-weight:900;color:#fff} p,.subtitle{color:#a6bbc9;line-height:1.6}
.ipl-ball,.ipl-bounce-ball{font-size:38px;display:inline-block;animation:float 3s ease-in-out infinite}
.ipl-stadium{background:linear-gradient(120deg,#061522,#073e39,#0b1b2d)}
.row{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;position:relative;z-index:3}
.title{color:white;font-size:clamp(22px,3vw,32px);font-weight:900;margin-top:10px}.subtitle{margin-top:7px}
/* Mini animated cricket action: bowler delivers, batter swings, ball is hit */
.cricket-action{height:126px;position:relative;overflow:hidden;margin:-5px 0 12px;border-radius:14px;background:linear-gradient(180deg,#071b2a99,#062b2780);border:1px solid #ffffff12;isolation:isolate}
.cricket-action:before{content:"";position:absolute;left:0;right:0;bottom:14px;height:28px;background:linear-gradient(180deg,#0d5c4388,#073b32aa);border-top:1px solid #38f7bd33;transform:perspective(150px) rotateX(8deg)}
.pitch-line{position:absolute;left:13%;right:12%;bottom:28px;border-top:2px dashed #c9e8d55c}
.action-label{position:absolute;left:12px;top:9px;font-size:9px;letter-spacing:2px;color:#80b6c1;font-weight:800}
.bowler-figure{position:absolute;left:8%;bottom:24px;font-size:43px;z-index:2;transform-origin:50% 100%;animation:bowlerRun 3.8s ease-in-out infinite}
.batter-figure{position:absolute;right:12%;bottom:23px;font-size:47px;z-index:2;transform-origin:60% 90%;animation:batterWait 3.8s ease-in-out infinite}
.action-bat{position:absolute;right:17%;bottom:45px;width:7px;height:56px;border-radius:4px;background:linear-gradient(90deg,#75471f,#f2d09a,#94602b);transform-origin:50% 90%;z-index:3;animation:batHit 3.8s ease-in-out infinite;box-shadow:0 0 8px #ffce7a44}
.action-ball{position:absolute;left:17%;bottom:55px;width:13px;height:13px;border-radius:50%;background:radial-gradient(circle at 30% 28%,#ffb3a4,#e6283c 55%,#781323);box-shadow:0 0 12px #ff344caa;z-index:4;animation:ballDeliveryHit 3.8s linear infinite}
.action-ball:after{content:"";position:absolute;left:5px;top:1px;height:10px;border-left:1px solid #fff4;transform:rotate(35deg)}
.action-stumps{position:absolute;right:8%;bottom:25px;display:flex;gap:3px;height:35px;z-index:1}
.action-stumps i{display:block;width:4px;border-radius:2px;background:linear-gradient(90deg,#e4d7ad,#fff5cf,#a99b71);box-shadow:0 0 6px #fff5a044}
.hit-flash{position:absolute;right:20%;bottom:63px;width:28px;height:28px;border-radius:50%;background:#fff8b8;filter:blur(7px);opacity:0;z-index:4;animation:hitFlash 3.8s ease infinite}
@keyframes bowlerRun{0%,12%{left:8%;transform:translateY(0) rotate(0)}22%{left:12%;transform:translateY(-5px) rotate(-15deg)}32%{left:16%;transform:translateY(0) rotate(12deg)}42%,100%{left:16%;transform:translateY(0) rotate(0)}}
@keyframes ballDeliveryHit{0%,25%{left:17%;bottom:55px;transform:scale(.65);opacity:0}30%{opacity:1}45%{left:62%;bottom:46px;transform:scale(1) rotate(400deg)}50%{left:70%;bottom:63px;transform:scale(1.05) rotate(540deg)}75%,100%{left:112%;bottom:105px;transform:scale(.65) rotate(1100deg);opacity:0}}
@keyframes batterWait{0%,42%,100%{transform:rotate(0)}47%{transform:rotate(-8deg)}52%{transform:rotate(8deg)}58%{transform:rotate(-3deg)}}
@keyframes batHit{0%,40%,100%{transform:rotate(-28deg)}46%{transform:rotate(-48deg)}51%{transform:rotate(58deg)}58%{transform:rotate(15deg)}}
@keyframes hitFlash{0%,46%,100%{opacity:0;transform:scale(.2)}50%{opacity:.95;transform:scale(1.7)}56%{opacity:0;transform:scale(2.5)}}
.animated-underline{height:3px;margin-top:20px;background:linear-gradient(90deg,transparent,#00f5a0,#35d9ff,transparent);background-size:200% 100%;animation:sweep 3s linear infinite}
.score-ticker{overflow:hidden;border-top:1px solid #087f70;border-bottom:1px solid #087f70;padding:13px 0;color:#b7ccd5;font-size:11px;font-weight:bold;letter-spacing:1.5px;white-space:nowrap}
.score-ticker-track{display:flex;gap:32px;width:max-content;animation:marquee 28s linear infinite}
@keyframes pulse{50%{opacity:.35}} @keyframes float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-12px) rotate(15deg)}}
@keyframes arena{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}} @keyframes sweep{to{background-position:200% 0}}
@keyframes marquee{to{transform:translateX(-50%)}}
@media(max-width:600px){.cricket-action{height:105px}.bowler-figure{font-size:34px}.batter-figure{font-size:38px}.action-bat{height:43px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body>
<div class="ipl-hero">
  <div class="sport-motion" aria-hidden="true"><span class="fly-ball">🏏</span><span class="fly-ball ball-two">🔴</span><span class="fly-ball ball-three">🔴</span><span class="swing-bat"></span><span class="swing-bat bat-two"></span></div>
  <div class="cricket-action" aria-label="Animated cricket delivery: bowler bowls, batter swings and hits the ball">
    <div class="action-label">LIVE ACTION • BOWLER TO BATTER</div><div class="pitch-line"></div>
    <div class="bowler-figure">🏃🏻‍♂️</div><div class="action-ball"></div><div class="hit-flash"></div>
    <div class="batter-figure">🧍🏻‍♂️</div><div class="action-bat"></div><div class="action-stumps"><i></i><i></i><i></i></div>
  </div>
  <div class="row"><div><div class="ipl-kicker"><span class="ipl-live-dot"></span> IPL PERFORMANCE LAB</div><h1>🏏 Bowling Intelligence Center</h1><p>Analyze bowling economy, wickets, dot balls, seasons and matchups.</p></div><div class="ipl-ball">🏏</div></div>
</div>
<div class="ipl-stadium">
  <div class="sport-motion" aria-hidden="true"><span class="fly-ball">🔴</span><span class="fly-ball ball-two">🏏</span><span class="fly-ball ball-three">🔴</span><span class="swing-bat"></span><span class="swing-bat bat-two"></span></div>
  <div class="row"><div><div class="neon-label">THE GAME • THE NUMBERS • THE STRATEGY</div><div class="title">Feel Every Delivery.</div><div class="subtitle">Discover the science behind every wicket.</div></div><div class="ipl-bounce-ball">🏏</div></div><div class="animated-underline"></div>
</div>
<div class="score-ticker"><div class="score-ticker-track"><span>🏏 IPL BOWLING INTELLIGENCE</span><span>⚡ ECONOMY ANALYSIS</span><span>🎯 WICKET TRACKER</span><span>🔥 DEATH OVER SPECIALISTS</span><span>📊 SEASON TRENDS</span><span>🏏 IPL BOWLING INTELLIGENCE</span><span>⚡ ECONOMY ANALYSIS</span><span>🎯 WICKET TRACKER</span><span>🔥 DEATH OVER SPECIALISTS</span><span>📊 SEASON TRENDS</span></div></div>
</body></html>
""", height=570, scrolling=False)



# =====================================================

# 3. AUTOMATIC DATABASE DETECTION

# =====================================================

ROOT = Path(__file__).resolve().parent.parent

DB_CANDIDATES = [

    ROOT / "data" / "raw" / "ipl.db",

    ROOT / "notebooks" / "ipl.db",

    ROOT / "ipl.db",

    ROOT / "data" / "processed" / "ipl.db",

]





def find_database():

    for path in DB_CANDIDATES:

        if not path.is_file() or path.stat().st_size == 0:

            continue

        try:

            with sqlite3.connect(path) as conn:

                tables = conn.execute("""

                    SELECT name FROM sqlite_master

                    WHERE type IN ('table', 'view')

                    ORDER BY CASE

                        WHEN lower(name)='deliveries' THEN 0

                        WHEN lower(name)='v_ball' THEN 1 ELSE 2 END

                """).fetchall()

                for (table,) in tables:

                    safe = table.replace('"', '""')

                    columns = conn.execute(f'PRAGMA table_info("{safe}")').fetchall()

                    names = {str(c[1]).lower().strip() for c in columns}

                    if "bowler" in names:

                        return path, table

        except sqlite3.Error:

            continue

    return None, None





DB_PATH, SOURCE_TABLE = find_database()

if DB_PATH is None:

    st.error("IPL database not found, or no table contains a bowler column.")

    st.write("Locations checked:")

    for path in DB_CANDIDATES:

        st.code(str(path))

    st.stop()





@st.cache_data(show_spinner="Loading IPL data...")

def load_data(db_path, table_name):

    safe = table_name.replace('"', '""')

    with sqlite3.connect(db_path) as conn:

        return pd.read_sql_query(f'SELECT * FROM "{safe}"', conn)





raw = load_data(str(DB_PATH), SOURCE_TABLE)

if raw.empty:

    st.error("The selected database table is empty.")

    st.stop()

with st.expander("Database information"):

    st.write(f"**Database:** `{DB_PATH.name}`")

    st.write(f"**Source table:** `{SOURCE_TABLE}`")

    st.write(f"**Source rows:** {len(raw):,}")



# =====================================================

# 4. DETECT DATABASE COLUMN NAMES

# =====================================================

original_columns = {str(c).lower().strip(): c for c in raw.columns}





def find_column(*names):

    for name in names:

        key = name.lower().strip()

        if key in original_columns:

            return original_columns[key]

    return None





ALIASES = {

    "bowler": ("bowler",),

    "season": ("season_id", "season_year", "season"),

    "runs": ("total_runs", "total_run", "runs_conceded"),

    "legal": ("is_legal", "legal_ball", "is_legal_ball"),

    "wide": ("is_wide_ball", "is_wide", "wide"),

    "no_ball": ("is_no_ball", "no_ball", "is_noball"),

    "wicket": ("is_wicket", "wicket"),

    "kind": ("wicket_kind", "dismissal_kind", "kind"),

    "style": ("bowler_type", "bowling_style", "style"),

    "over": ("over_number", "over", "over_id"),

    "phase": ("phase", "innings_phase"),

    "team": ("batting_team", "opponent"),

    "match": ("match_id", "match_number"),

    "venue": ("venue", "venue_clean", "ground", "stadium"),

}

COL = {name: find_column(*aliases) for name, aliases in ALIASES.items()}

if COL["bowler"] is None or COL["runs"] is None:

    st.error("Required bowler or runs column is missing.")

    st.write("Available columns:", list(raw.columns))

    st.stop()



# =====================================================

# 5. NORMALIZE DATA

# =====================================================

df = pd.DataFrame(index=raw.index)

df["bowler"] = raw[COL["bowler"]].astype("string").str.strip()

df["runs"] = pd.to_numeric(raw[COL["runs"]], errors="coerce").fillna(0)





def numeric_column(name, default=0):

    col = COL[name]

    if col is None:

        return pd.Series(default, index=raw.index, dtype=float)

    return pd.to_numeric(raw[col], errors="coerce").fillna(default)





df["wide"] = numeric_column("wide").clip(0, 1)

df["no_ball"] = numeric_column("no_ball").clip(0, 1)

df["wicket_flag"] = numeric_column("wicket")

df["over"] = numeric_column("over", -1)

if COL["legal"] is not None:

    df["legal"] = numeric_column("legal").clip(0, 1)

else:

    df["legal"] = (1 - df["wide"] - df["no_ball"]).clip(0, 1)



for name in ["season", "style", "kind", "team", "venue"]:

    col = COL[name]

    target = {"team": "opponent", "kind": "kind"}.get(name, name)

    if col is not None:

        df[target] = raw[col].astype("string").fillna("Unknown").str.strip()

    else:

        df[target] = "Unknown"



df["match"] = raw[COL["match"]] if COL["match"] else None

if COL["phase"] is not None:

    df["phase"] = raw[COL["phase"]].astype("string").fillna("Unknown")

    phase_map = {

        "power play": "Powerplay", "powerplay": "Powerplay",

        "middle overs": "Middle", "middle": "Middle",

        "death overs": "Death", "death": "Death",

    }

    df["phase"] = df["phase"].map(lambda x: phase_map.get(str(x).lower().strip(), x))

else:

    df["phase"] = pd.cut(

        df["over"], bins=[-1, 5, 14, float("inf")],

        labels=["Powerplay", "Middle", "Death"],

    ).astype("string")

df["phase"] = df["phase"].fillna("Unknown")



not_credited = {"run out", "retired hurt", "retired out", "obstructing the field"}

df["credited_wicket"] = (

    (df["wicket_flag"] == 1) & ~df["kind"].str.lower().isin(not_credited)

).astype(int)

df["dot_ball"] = ((df["legal"] == 1) & (df["runs"] == 0)).astype(int)

df = df[df["bowler"].notna() & (df["bowler"] != "")].copy()

if df.empty:

    st.error("No valid bowler records were found.")

    st.stop()



# =====================================================

# 6. FILTERS AND HELPERS

# =====================================================

ALL = "All"

PHASES = ["Powerplay", "Middle", "Death"]

SEASONS = sorted(df["season"].astype(str).unique().tolist())

STYLES = sorted(s for s in df["style"].astype(str).unique() if s and s.lower() != "unknown")

CHART_COLORS = ["#00f5a0", "#35d9ff", "#ffad55", "#a78bfa", "#ff6685", "#f7e967"]





def independent_filters(chart_name, allow_phase=True):

    st.markdown(f"**Filters — {chart_name.replace('_', ' ').title()}**")

    a, b, c = st.columns(3)

    with a:

        season = st.selectbox("Season", [ALL] + SEASONS, key=f"{chart_name}_season")

    with b:

        style = st.selectbox("Bowling style", [ALL] + STYLES, key=f"{chart_name}_style")

    with c:

        options = [ALL] + PHASES if allow_phase else [ALL]

        phase = st.selectbox("Innings phase", options, key=f"{chart_name}_phase")

    data = df

    if season != ALL:

        data = data[data["season"].astype(str) == season]

    if style != ALL:

        data = data[data["style"].astype(str) == style]

    if phase != ALL:

        data = data[data["phase"] == phase]

    return data.copy()





def aggregate_bowlers(data):

    result = data.groupby("bowler", as_index=False).agg(

        runs=("runs", "sum"), balls=("legal", "sum"),

        wickets=("credited_wicket", "sum"), dots=("dot_ball", "sum"),

    )

    balls = result["balls"].where(result["balls"] > 0)

    result["economy"] = 6 * result["runs"] / balls

    result["dot_share"] = 100 * result["dots"] / balls

    return result





def show_chart(fig, height=420):

    fig.update_layout(

        height=height, template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",

        font=dict(family="Arial, sans-serif", color="#dce8ef", size=12),

        title_font=dict(size=18, color="#00f5a0"),

        margin=dict(l=20, r=25, t=65, b=30), legend_title_text="",

        hovermode="closest", transition_duration=800 if chart_motion and motion_mode == "Full motion" else (350 if chart_motion else 0),

        hoverlabel=dict(bgcolor="#142735", bordercolor="#00f5a0", font_color="#ffffff"),

    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(160,190,210,0.09)", zerolinecolor="rgba(160,190,210,0.15)")

    fig.update_yaxes(showgrid=True, gridcolor="rgba(160,190,210,0.09)", zerolinecolor="rgba(160,190,210,0.15)")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True}, theme=None)





def season_summary(data):

    result = data.groupby("season", as_index=False).agg(runs=("runs", "sum"), balls=("legal", "sum"))

    result["economy"] = 6 * result["runs"] / result["balls"].where(result["balls"] > 0)

    return result.dropna(subset=["economy"]).sort_values("season")





def section_title(number, title, subtitle=None):

    st.markdown(f"### {number}. {title}")

    if subtitle:

        st.caption(subtitle)



# =====================================================

# 7. DASHBOARD TABS

# =====================================================

overview_tab, player_tab, studio_tab = st.tabs(["📊 Overview", "🎯 Individual Bowler", "✨ Analytics Studio"])



# =====================================================

# TAB 1 — OVERVIEW

# =====================================================

with overview_tab:

    st.header("Bowling Overview")

    st.caption("A complete view of bowling performance across the selected data.")

    total_bowlers = df["bowler"].nunique()

    total_wickets = int(df["credited_wicket"].sum())

    total_balls = int(df["legal"].sum())

    total_matches = df["match"].nunique() if COL["match"] is not None else None

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("🏏 Bowlers", f"{total_bowlers:,}")

    k2.metric("🎯 Credited wickets", f"{total_wickets:,}")

    k3.metric("⚡ Legal balls", f"{total_balls:,}")

    k4.metric("🏆 Matches", f"{total_matches:,}" if total_matches is not None else "N/A")

    st.divider()



    section_title(1, "Bowling Economy by Season", "Track runs conceded per six legal balls over time.")

    data = independent_filters("economy_chart", allow_phase=False)

    stats = season_summary(data)

    if not stats.empty:

        fig = px.line(stats, x="season", y="economy", markers=True, hover_data=["balls"], title="Season economy trend", labels={"season":"Season","economy":"Runs per 6 legal balls","balls":"Legal balls"})

        fig.update_traces(line=dict(color="#00f5a0", width=3), marker=dict(size=9, color="#35d9ff"), fill="tozeroy", fillcolor="rgba(0,245,160,0.07)")

        show_chart(fig)

    else: st.info("No data for these filters.")

    st.divider()



    section_title(2, "Wickets by Innings Phase", "Compare wicket-taking performance in different phases.")

    data = independent_filters("wickets_phase_chart")

    stats = data.groupby("phase", as_index=False).agg(wickets=("credited_wicket", "sum"))

    stats = stats[stats["phase"].isin(PHASES)]

    if not stats.empty:

        fig = px.bar(stats, x="phase", y="wickets", text="wickets", title="Credited wickets by phase", category_orders={"phase":PHASES}, color="phase", color_discrete_sequence=CHART_COLORS)

        fig.update_traces(marker_line_width=0, textposition="outside")

        fig.update_layout(showlegend=False)

        show_chart(fig)

    else: st.info("No wicket data for these filters.")

    st.divider()



    section_title(3, "Best Economy — Bowlers", "Lower economy is better. Apply a minimum-ball threshold.")

    data = independent_filters("bowler_economy_chart")

    minimum_balls = st.selectbox("Minimum legal balls", [0, 60, 120, 300, 500], index=2, key="economy_chart_minimum_balls")

    stats = aggregate_bowlers(data)

    stats = stats[(stats["balls"] >= minimum_balls) & stats["economy"].notna()].nsmallest(15, "economy")

    if not stats.empty:

        chart_data = stats.sort_values("economy")

        fig = px.bar(chart_data, x="economy", y="bowler", orientation="h", title="Lowest economy bowlers", hover_data=["balls", "wickets"], color="economy", color_continuous_scale=["#00a878", "#00f5a0", "#35d9ff"])

        fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)

        show_chart(fig, height=490)

    else: st.info("No bowlers meet the minimum-ball requirement.")

    st.divider()



    section_title(4, "Dot-Ball Percentage by Phase", "Percentage of legal deliveries that conceded zero runs.")

    data = independent_filters("dot_ball_chart")

    stats = data.groupby("phase", as_index=False).agg(dots=("dot_ball", "sum"), balls=("legal", "sum"))

    stats["dot_percentage"] = 100 * stats["dots"] / stats["balls"].where(stats["balls"] > 0)

    stats = stats[stats["phase"].isin(PHASES)].dropna(subset=["dot_percentage"])

    if not stats.empty:

        fig = px.bar(stats, x="phase", y="dot_percentage", text=stats["dot_percentage"].map(lambda x: f"{x:.1f}%"), title="Dot-ball percentage", category_orders={"phase":PHASES}, labels={"dot_percentage":"Dot balls (%)"}, color="dot_percentage", color_continuous_scale=["#35d9ff", "#00f5a0"])

        fig.update_traces(textposition="outside")

        fig.update_layout(coloraxis_showscale=False)

        show_chart(fig)

    else: st.info("No dot-ball data for these filters.")

    st.divider()



    section_title(5, "Compare Bowling Styles", "Compare economy rates and wicket totals across styles.")

    data = independent_filters("style_comparison_chart")

    stats = data.groupby("style", as_index=False).agg(runs=("runs", "sum"), balls=("legal", "sum"), wickets=("credited_wicket", "sum"))

    stats["economy"] = 6 * stats["runs"] / stats["balls"].where(stats["balls"] > 0)

    stats = stats.dropna(subset=["economy"])

    if not stats.empty:

        fig = px.bar(stats, x="style", y="economy", color="wickets", title="Economy by bowling style", hover_data=["balls", "wickets"], color_continuous_scale=["#00a878", "#35d9ff", "#ffad55"])

        show_chart(fig)

    else: st.info("No style data for these filters.")

    st.divider()



    section_title(6, "Dismissal Types", "See which dismissal types contribute to credited wickets.")

    data = independent_filters("dismissal_chart")

    stats = data[data["credited_wicket"] == 1].groupby("kind", as_index=False).agg(wickets=("credited_wicket", "sum"))

    stats = stats.sort_values("wickets", ascending=False)

    if not stats.empty:

        fig = px.pie(stats, names="kind", values="wickets", title="Credited wickets by dismissal type", color_discrete_sequence=CHART_COLORS, hole=0.52)

        fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#101e2a", width=2)))

        show_chart(fig)

    else: st.info("No dismissal data for these filters.")



# =====================================================

# TAB 2 — INDIVIDUAL BOWLER

# =====================================================

with player_tab:

    st.header("Individual Bowler Performance")

    st.caption("Select a bowler and explore their performance in detail.")

    player_base = independent_filters("individual_bowler_selector", allow_phase=False)

    bowler_options = sorted(player_base["bowler"].dropna().unique().tolist())

    if not bowler_options:

        st.warning("No bowlers match the selected filters.")

    else:

        selected_bowler = st.selectbox("Select a bowler", bowler_options, key="individual_bowler_select")

        player_data = player_base[player_base["bowler"] == selected_bowler]

        player_stats = aggregate_bowlers(player_data).iloc[0]

        st.markdown(f"""

        <div style="padding:18px 22px;margin:10px 0 20px;border:1px solid #00f5a044;border-radius:16px;background:linear-gradient(110deg,#102c32,#122132);">

          <div style="color:#00f5a0;font-size:11px;letter-spacing:2px;font-weight:800;">PLAYER PROFILE</div>

          <div style="color:white;font-size:27px;font-weight:850;margin-top:6px;">{selected_bowler}</div>

          <div style="color:#a6bbc9;font-size:13px;">Performance snapshot for the selected filters</div>

        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        c1.metric("🎯 Wickets", f"{int(player_stats['wickets']):,}")

        c2.metric("⚡ Economy", f"{player_stats['economy']:.2f}" if pd.notna(player_stats["economy"]) else "N/A")

        c3.metric("🟢 Dot-ball percentage", f"{player_stats['dot_share']:.2f}%" if pd.notna(player_stats["dot_share"]) else "N/A")

        st.divider()



        section_title(1, "Economy by Season")

        data = independent_filters("individual_economy_chart", allow_phase=False)

        data = data[data["bowler"] == selected_bowler]

        stats = season_summary(data)

        if not stats.empty:

            fig = px.line(stats, x="season", y="economy", markers=True, hover_data=["balls"], title=f"{selected_bowler}: economy trend")

            fig.update_traces(line=dict(color="#00f5a0", width=3), marker=dict(size=10, color="#35d9ff"), fill="tozeroy", fillcolor="rgba(0,245,160,0.07)")

            show_chart(fig)

        else: st.info("No seasonal economy data.")

        st.divider()



        section_title(2, "Wickets by Phase")

        data = independent_filters("individual_wickets_chart")

        data = data[data["bowler"] == selected_bowler]

        stats = data.groupby("phase", as_index=False).agg(wickets=("credited_wicket", "sum"))

        stats = stats[stats["phase"].isin(PHASES)]

        if not stats.empty:

            fig = px.bar(stats, x="phase", y="wickets", text="wickets", title=f"{selected_bowler}: wickets by phase", category_orders={"phase":PHASES}, color="phase", color_discrete_sequence=CHART_COLORS)

            fig.update_traces(textposition="outside")

            fig.update_layout(showlegend=False)

            show_chart(fig)

        else: st.info("No phase wicket data.")

        st.divider()



        section_title(3, "Economy Against Opponents")

        data = independent_filters("individual_opponent_chart")

        data = data[data["bowler"] == selected_bowler]

        stats = data.groupby("opponent", as_index=False).agg(runs=("runs", "sum"), balls=("legal", "sum"), wickets=("credited_wicket", "sum"))

        stats["economy"] = 6 * stats["runs"] / stats["balls"].where(stats["balls"] > 0)

        stats = stats.dropna(subset=["economy"]).sort_values("economy")

        if not stats.empty:

            fig = px.bar(stats, x="economy", y="opponent", orientation="h", title=f"{selected_bowler}: economy against opponents", hover_data=["balls", "wickets"], color="economy", color_continuous_scale=["#00f5a0", "#35d9ff", "#ffad55"])

            fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)

            show_chart(fig, height=490)

        else: st.info("No opponent data.")

        st.divider()



        section_title(4, "Economy at Grounds")

        data = independent_filters("individual_ground_chart", allow_phase=False)

        data = data[data["bowler"] == selected_bowler]

        if COL["venue"] is None:

            st.info("No venue column was found. A join with the matches table may be required to display grounds.")

        else:

            stats = data.groupby("venue", as_index=False).agg(runs=("runs", "sum"), balls=("legal", "sum"), wickets=("credited_wicket", "sum"))

            stats["economy"] = 6 * stats["runs"] / stats["balls"].where(stats["balls"] > 0)

            stats = stats.dropna(subset=["economy"]).nsmallest(15, "economy")

            if not stats.empty:

                fig = px.bar(stats.sort_values("economy"), x="economy", y="venue", orientation="h", title=f"{selected_bowler}: economy by ground", hover_data=["balls", "wickets"], labels={"venue":"Ground", "economy":"Economy"}, color="economy", color_continuous_scale=["#00f5a0", "#35d9ff"])

                fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)

                show_chart(fig, height=490)

            else: st.info("No ground data.")

        st.divider()



        section_title(5, "Dismissal Types")

        data = independent_filters("individual_dismissal_chart")

        data = data[(data["bowler"] == selected_bowler) & (data["credited_wicket"] == 1)]

        stats = data.groupby("kind", as_index=False).agg(wickets=("credited_wicket", "sum")).sort_values("wickets", ascending=False)

        if not stats.empty:

            fig = px.bar(stats, x="kind", y="wickets", title=f"{selected_bowler}: dismissal types", labels={"kind":"Dismissal type", "wickets":"Wickets"}, color="kind", color_discrete_sequence=CHART_COLORS)

            fig.update_layout(showlegend=False)

            show_chart(fig)

        else: st.info("No credited dismissals for this selection.")



# =====================================================

# TAB 3 — ANALYTICS STUDIO (ADDITIONAL CHART VARIETY)

# =====================================================

with studio_tab:

    st.markdown('<div class="eyebrow">Explore the numbers differently</div>', unsafe_allow_html=True)

    st.header("Analytics Studio")

    st.caption("Interactive visual experiments: animated season movement, distribution, phase heatmaps and player radar profiles.")



    studio_data = independent_filters("analytics_studio", allow_phase=True)

    studio_bowlers = aggregate_bowlers(studio_data)

    valid_economy = studio_bowlers.dropna(subset=["economy"]).copy()

    if valid_economy.empty:

        st.info("There is not enough legal-ball data for these filters. Try another season or phase.")

    else:

        # Chart 1: bubble/scatter overview — size represents wickets, color represents economy.

        section_title(1, "Bowler Impact Map", "Each point is a bowler. Further right means more wickets; lower economy is generally more economical.")

        impact = valid_economy.copy()

        impact["bubble_size"] = impact["wickets"].clip(lower=1)

        fig = px.scatter(

            impact, x="wickets", y="economy", size="bubble_size", color="economy",

            hover_name="bowler", hover_data={"runs": True, "balls": True, "dots": True, "bubble_size": False},

            title="Wickets vs economy rate", color_continuous_scale=["#00f5a0", "#35d9ff", "#ffad55"],

            size_max=36,

        )

        fig.update_traces(marker=dict(opacity=.86, line=dict(width=1, color="#dcebf2")))

        fig.update_layout(coloraxis_showscale=False, xaxis_title="Credited wickets", yaxis_title="Economy rate")

        show_chart(fig, height=460)

        st.divider()



        # Chart 2: distribution histogram.

        section_title(2, "Economy Rate Distribution", "See the spread of economy rates rather than only the top-ranked bowlers.")

        fig = px.histogram(

            valid_economy, x="economy", nbins=24, marginal="box", hover_data=["bowler", "wickets", "balls"],

            title="How economy rates are distributed", color_discrete_sequence=["#00f5a0"],

        )

        fig.update_traces(marker_line_color="#07111b", marker_line_width=1, opacity=.88)

        show_chart(fig, height=430)

        st.divider()



        # Chart 3: phase heatmap.

        section_title(3, "Bowler × Innings Phase Heatmap", "Compare where the selected bowlers take wickets. The strongest cells stand out visually.")

        phase_data = studio_data[studio_data["phase"].isin(PHASES)]

        if phase_data.empty:

            st.info("Phase values are unavailable for this selection.")

        else:

            heat = phase_data.groupby(["bowler", "phase"], as_index=False).agg(wickets=("credited_wicket", "sum"))

            top_names = heat.groupby("bowler")["wickets"].sum().nlargest(15).index.tolist()

            heat = heat[heat["bowler"].isin(top_names)]

            pivot = heat.pivot(index="bowler", columns="phase", values="wickets").fillna(0)

            pivot = pivot.reindex(columns=[p for p in PHASES if p in pivot.columns])

            fig = px.imshow(

                pivot, text_auto=True, aspect="auto", color_continuous_scale=["#102330", "#087f68", "#00f5a0"],

                labels=dict(x="Innings phase", y="Bowler", color="Wickets"), title="Wicket concentration by phase",

            )

            fig.update_layout(coloraxis_colorbar=dict(title="Wickets"))

            show_chart(fig, height=max(430, 28 * len(pivot) + 150))

        st.divider()



        # Chart 4: animated season race using Plotly's native animation controls.

        section_title(4, "Animated Season Performance", "Use the play button or slider to move through seasons. Bubble size reflects wickets.")

        seasonal = df.copy()

        if "season" in seasonal.columns:

            if "season" in studio_data.columns:

                # Preserve the currently selected season/style/phase filters, but use all seasons for animation.

                seasonal = df.copy()

                selected_style = st.session_state.get("analytics_studio_style", ALL)

                selected_phase = st.session_state.get("analytics_studio_phase", ALL)

                if selected_style != ALL:

                    seasonal = seasonal[seasonal["style"].astype(str) == selected_style]

                if selected_phase != ALL:

                    seasonal = seasonal[seasonal["phase"] == selected_phase]

            seasonal_stats = seasonal.groupby(["season", "bowler"], as_index=False).agg(

                runs=("runs", "sum"), balls=("legal", "sum"), wickets=("credited_wicket", "sum")

            )

            seasonal_stats["economy"] = 6 * seasonal_stats["runs"] / seasonal_stats["balls"].where(seasonal_stats["balls"] > 0)

            seasonal_stats = seasonal_stats.dropna(subset=["economy"])

            if seasonal_stats["season"].nunique() > 1 and not seasonal_stats.empty:

                seasonal_stats["bubble_size"] = seasonal_stats["wickets"].clip(lower=1)

                fig = px.scatter(

                    seasonal_stats, x="wickets", y="economy", animation_frame="season", animation_group="bowler",

                    size="bubble_size", color="economy", hover_name="bowler", size_max=30,

                    range_x=[0, max(5, float(seasonal_stats["wickets"].max()) * 1.08)],

                    range_y=[0, max(8, float(seasonal_stats["economy"].quantile(.98)) * 1.15)],

                    color_continuous_scale=["#00f5a0", "#35d9ff", "#ffad55"], title="Season-by-season bowler race",

                )

                fig.update_layout(coloraxis_showscale=False, xaxis_title="Credited wickets", yaxis_title="Economy rate", transition=dict(duration=700, easing="cubic-in-out"))

                show_chart(fig, height=500)

            else:

                st.info("The database needs at least two seasons to play the animated season chart.")



        st.divider()

        # Chart 5: radar profile for a selected bowler, normalized to compare categories fairly.

        section_title(5, "Bowler Radar Profile", "A compact profile comparing wickets, dot-ball share and economy against the selected dataset range.")

        radar_names = sorted(valid_economy["bowler"].dropna().unique().tolist())

        radar_player = st.selectbox("Bowler for radar profile", radar_names, key="studio_radar_player")

        chosen = valid_economy[valid_economy["bowler"] == radar_player]

        if not chosen.empty:

            row = chosen.iloc[0]

            max_wickets = max(1.0, float(valid_economy["wickets"].max()))

            max_dot = max(1.0, float(valid_economy["dot_share"].dropna().max()) if valid_economy["dot_share"].notna().any() else 1.0)

            max_economy = max(1.0, float(valid_economy["economy"].max()))

            # Economy is inverted so a lower economy plots farther from the centre (better).

            economy_score = max(0.0, 100 * (1 - float(row["economy"]) / max_economy)) if max_economy else 0.0

            radar_values = [100 * float(row["wickets"]) / max_wickets, min(100, 100 * float(row["dot_share"] or 0) / max_dot), economy_score]

            radar_labels = ["Wicket impact", "Dot-ball share", "Economy efficiency"]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(

                r=radar_values + [radar_values[0]], theta=radar_labels + [radar_labels[0]],

                fill="toself", name=radar_player,

                line=dict(color="#00f5a0", width=3), fillcolor="rgba(0,245,160,0.20)",

                marker=dict(size=8, color="#35d9ff"),

            ))

            fig.update_layout(

                title=f"{radar_player} — normalized bowling profile", polar=dict(

                    bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(160,190,210,0.15)"),

                    angularaxis=dict(gridcolor="rgba(160,190,210,0.15)"),

                ), showlegend=False,

            )

            show_chart(fig, height=460)



# =====================================================

# 8. VISUAL LAB — ADDITIONAL CHART STYLES

# =====================================================

st.divider()

st.markdown('<div class="eyebrow">More ways to read the game</div>', unsafe_allow_html=True)

st.header("Visual Lab")

st.caption("Switch chart forms to explore bowling performance from new angles.")

visual_data = independent_filters("visual_lab", allow_phase=True)

visual_stats = aggregate_bowlers(visual_data)

visual_stats = visual_stats.dropna(subset=["economy"]).copy()

if not visual_stats.empty:

    chart_style = st.selectbox(

        "Choose a visualization",

        ["Wicket contribution treemap", "Economy violin plot", "Bowling profile in 3D", "Season wicket race", "Dismissal sunburst"],

        key="visual_lab_chart_style",

    )

    if chart_style == "Wicket contribution treemap":

        st.markdown("#### 🧩 Wicket contribution map")

        tree = visual_stats[visual_stats["wickets"] > 0].nlargest(30, "wickets")

        if not tree.empty:

            fig = px.treemap(tree, path=[px.Constant("All bowlers"), "bowler"], values="wickets", color="economy",

                             color_continuous_scale=[THEME["accent"], THEME["secondary"], "#ffad55"],

                             hover_data=["balls", "runs", "dot_share"], title="Share of wickets among leading bowlers")

            fig.update_traces(marker=dict(line=dict(color="#07111b", width=2)), selector=dict(type="treemap"))

            show_chart(fig, height=520)

        else:

            st.info("No credited wickets are available for the current filters.")

    elif chart_style == "Economy violin plot":

        st.markdown("#### 🎻 Economy-rate distribution by bowling style")

        violin_data = visual_data.copy()

        violin_data["economy"] = 6 * violin_data["runs"] / violin_data["legal"].where(violin_data["legal"] > 0)

        violin_data = violin_data.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["economy"])

        violin_data = violin_data[violin_data["economy"] <= violin_data["economy"].quantile(.99)] if not violin_data.empty else violin_data

        if not violin_data.empty:

            fig = px.violin(violin_data, x="style", y="economy", color="style", box=True, points="outliers",

                            color_discrete_sequence=CHART_COLORS, title="Economy spread by bowling style")

            fig.update_traces(meanline_visible=True, opacity=.82)

            fig.update_layout(showlegend=False, xaxis_title="Bowling style", yaxis_title="Economy rate")

            show_chart(fig, height=500)

        else:

            st.info("There is not enough delivery data for the violin plot.")

    elif chart_style == "Bowling profile in 3D":

        st.markdown("#### 🌐 Three-dimensional bowling profile")

        fig = px.scatter_3d(visual_stats, x="wickets", y="economy", z="dot_share", color="wickets", size="balls",

                            hover_name="bowler", hover_data=["runs", "dots"], size_max=24,

                            color_continuous_scale=[THEME["accent"], THEME["secondary"], "#ffad55"],

                            title="Wickets × economy × dot-ball share")

        fig.update_layout(scene=dict(xaxis_title="Wickets", yaxis_title="Economy", zaxis_title="Dot-ball %"), coloraxis_showscale=False)

        show_chart(fig, height=560)

    elif chart_style == "Season wicket race":

        st.markdown("#### 🏁 Animated wicket race")

        race = df.copy()

        selected_style = st.session_state.get("visual_lab_style", ALL)

        selected_phase = st.session_state.get("visual_lab_phase", ALL)

        if selected_style != ALL:

            race = race[race["style"].astype(str) == selected_style]

        if selected_phase != ALL:

            race = race[race["phase"] == selected_phase]

        race = race.groupby(["season", "bowler"], as_index=False).agg(wickets=("credited_wicket", "sum"), runs=("runs", "sum"), balls=("legal", "sum"))

        race = race[race["wickets"] > 0]

        if race["season"].nunique() > 1 and not race.empty:

            race["economy"] = 6 * race["runs"] / race["balls"].where(race["balls"] > 0)

            race = race.dropna(subset=["economy"])

            race["season_label"] = race["season"].astype(str)

            fig = px.bar(race, x="wickets", y="bowler", color="economy", animation_frame="season_label",

                         animation_group="bowler", orientation="h", range_x=[0, max(1, float(race["wickets"].max()) * 1.12)],

                         color_continuous_scale=[THEME["accent"], THEME["secondary"], "#ffad55"],

                         title="Wicket leaderboard across seasons")

            fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False,

                              transition=dict(duration=650, easing="cubic-in-out"))

            show_chart(fig, height=560)

        else:

            st.info("The season race needs at least two seasons with credited wickets.")

    else:

        st.markdown("#### ☀️ Dismissal sunburst")

        sun = visual_data[visual_data["credited_wicket"] == 1].copy()

        sun["phase_group"] = sun["phase"].where(sun["phase"].isin(PHASES), "Other")

        sun = sun.groupby(["phase_group", "kind"], as_index=False).agg(wickets=("credited_wicket", "sum"))

        sun = sun[sun["wickets"] > 0]

        if not sun.empty:

            fig = px.sunburst(sun, path=["phase_group", "kind"], values="wickets", color="wickets",

                              color_continuous_scale=[THEME["accent"], THEME["secondary"], "#ffad55"],

                              title="Wicket types nested inside innings phases")

            fig.update_traces(marker=dict(line=dict(color="#07111b", width=2)))

            show_chart(fig, height=530)

        else:

            st.info("No dismissal data is available for this selection.")

else:

    st.info("Choose different filters to populate the Visual Lab.")



# =====================================================

# 9. FOOTER

# =====================================================

st.divider()

st.markdown("""

<div style="padding:18px;border-radius:14px;background:linear-gradient(110deg,#10212c,#0b1721);border:1px solid #29404d;text-align:center;">

  <div style="color:#00f5a0;font-size:12px;font-weight:800;letter-spacing:2px;">IPL BOWLING INTELLIGENCE</div>

  <div style="color:#8da7b7;font-size:12px;margin-top:7px;">Data-driven cricket analysis • Built with Python, Streamlit and Plotly</div>

</div>

""", unsafe_allow_html=True)

st.caption(

    "Economy = runs × 6 / legal balls. Dot-ball percentage uses legal deliveries only. "

    "Credited wickets exclude run outs, retired hurt, retired out and obstructing the field. "

    "When inferred from over number, phases are Powerplay (0–5), Middle (6–14), and Death (15+)."

)
