import streamlit as st
import time
import math

# ─────────────────────────── Page Config ────────────────────────────
st.set_page_config(
    page_title="MindSight AI · Cognitive Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Load background image (base64) ─────────────────────────────────
import base64, pathlib

BG_PATH = pathlib.Path(__file__).parent / "background.png"
if BG_PATH.exists():
    BG_B64 = base64.b64encode(BG_PATH.read_bytes()).decode()
    BG_DATA = f"data:image/png;base64,{BG_B64}"
else:
    BG_DATA = ""

# ─────────────────────────── Global CSS ─────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&family=Share+Tech+Mono&display=swap');

* {{ box-sizing: border-box; }}

html, body {{
    background: #020b1a !important;
    color: #c8dff5 !important;
    font-family: 'Exo 2', sans-serif !important;
}}

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(ellipse at 20% 10%, #0a2040 0%, #020b1a 60%) !important;
}}

[data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
section[data-testid="stMain"] > div {{ padding-top: 1rem !important; }}
.block-container {{ padding: 1.5rem 2rem 3rem !important; max-width: 1000px !important; margin: auto; position: relative; z-index: 1; }}

::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: #020b1a; }}
::-webkit-scrollbar-thumb {{ background: #1a4a8a; border-radius: 3px; }}

.stButton > button {{
    background: linear-gradient(135deg, #0d4fa8, #1a7ad4) !important;
    color: #e8f4ff !important;
    border: 1px solid #2a8ae8 !important;
    border-radius: 8px !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 14px rgba(26,122,212,0.35) !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #1a6cd4, #2a9af0) !important;
    box-shadow: 0 0 22px rgba(42,154,240,0.55) !important;
    transform: translateY(-1px) !important;
}}

[data-testid="stRadio"] label {{
    background: rgba(10,40,80,0.6) !important;
    border: 1px solid #1a3a6a !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    margin-bottom: 0.4rem !important;
    display: block !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: #a8ccee !important;
    font-family: 'Exo 2', sans-serif !important;
}}
[data-testid="stRadio"] label:hover {{
    background: rgba(26,74,138,0.7) !important;
    border-color: #2a8ae8 !important;
    color: #e8f4ff !important;
}}

[data-testid="stMetric"] {{
    background: rgba(10,30,60,0.8) !important;
    border: 1px solid #1a3a6a !important;
    border-radius: 10px !important;
    padding: 0.8rem 1rem !important;
}}
[data-testid="stMetricLabel"] {{ color: #7aaad4 !important; font-size: 0.78rem !important; }}
[data-testid="stMetricValue"] {{ color: #4dc3ff !important; font-family: 'Share Tech Mono', monospace !important; }}

[data-testid="stProgress"] > div > div {{ background: linear-gradient(90deg, #1a7ad4, #4dc3ff) !important; }}
[data-testid="stProgress"] {{ background: rgba(10,30,60,0.5) !important; border-radius: 4px !important; }}

hr {{ border-color: #0d2a4a !important; margin: 1.5rem 0 !important; }}

code {{ font-family: 'Share Tech Mono', monospace !important; color: #4dc3ff !important; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── State Init ─────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "current_q": 0,
        "answers": {},
        "answer_times": {},
        "q_start_time": None,
        "scores": {},
        "answer": None,
        "answer_time": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

import base64

def img_to_b64(path_str):
    p = pathlib.Path(path_str)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return ""

SCENE_IMG_Q1 = img_to_b64(pathlib.Path(__file__).parent / "image 2.png")        # video call → Q1
SCENE_IMG_Q2 = img_to_b64(pathlib.Path(__file__).parent / "image 3.png")        # proposal → Q2
SCENE_IMG_Q3 = img_to_b64(pathlib.Path(__file__).parent / "background.png")     # puzzle → Q3
ADJUSTMENT_IMG = img_to_b64(pathlib.Path(__file__).parent / "wide_cozy_sunlit_interior_scene_viewed_in_a_vr_ro.png")

# 兼容旧引用
ORIGINAL_SCENE_IMG = SCENE_IMG_Q1
ADAPTED_SCENE_IMG  = SCENE_IMG_Q3


# ─────────────────────────── Question Data ───────────────────────────
QUESTIONS = [
    # ── Q1 · Video Call ──────────────────────────────────────────────
    {
        "scene": {
            "label": "System Failure Under Scrutiny",
            "desc": "You are presenting an important project to your team over video call. Halfway through, your screen freezes. Everyone is waiting. The silence feels loud.",
            "emoji": "💻",
            "bg": "q1",
        },
        "text": "The screen has frozen mid-presentation. Everyone is watching. What do you do?",
        "options": [
            {
                "letter": "A",
                "text": "I stay calm, apologise briefly, switch to a backup, and continue without losing the thread.",
                "scores": {"focus": 9, "stress": 3, "impulse": 8},
                "profile": "Resilient / Adaptive Under Pressure",
            },
            {
                "letter": "B",
                "text": "I feel flustered but manage to keep talking while fixing the issue, though I lose my place a little.",
                "scores": {"focus": 5, "stress": 6, "impulse": 5},
                "profile": "Moderate Stress Response",
            },
            {
                "letter": "C",
                "text": "I panic, go silent, and struggle to recover — my mind goes blank.",
                "scores": {"focus": 2, "stress": 10, "impulse": 2},
                "profile": "High Stress / Low Recovery",
            },
        ],
    },
    # ── Q2 · Proposal ────────────────────────────────────────────────
    {
        "scene": {
            "label": "Emotional Regulation After Criticism",
            "desc": "You spent days preparing a proposal. In the meeting, a colleague dismisses it in front of everyone — calling it 'underdeveloped' without explanation.",
            "emoji": "🗣️",
            "bg": "q2",
        },
        "text": "Your proposal has just been publicly dismissed. How do you respond internally?",
        "options": [
            {
                "letter": "A",
                "text": "I feel stung, but I listen for any valid point and mentally note how to improve.",
                "scores": {"focus": 8, "stress": 4, "impulse": 7},
                "profile": "Emotionally Resilient / Growth-Oriented",
            },
            {
                "letter": "B",
                "text": "I'm upset and distracted for the rest of the meeting, but I hold it together outwardly.",
                "scores": {"focus": 4, "stress": 7, "impulse": 5},
                "profile": "Emotionally Reactive / Controlled Surface",
            },
            {
                "letter": "C",
                "text": "I shut down — I stop contributing and can't focus on anything else.",
                "scores": {"focus": 1, "stress": 10, "impulse": 2},
                "profile": "High Emotional Sensitivity / Low Regulation",
            },
        ],
    },
    # ── Q3 · Puzzle ──────────────────────────────────────────────────
    {
        "scene": {
            "label": "Cognitive Load Under Pressure",
            "desc": "You are solving a complex puzzle under a 5-minute timer. Notifications keep popping up on your screen — messages, alerts, calendar reminders.",
            "emoji": "🧩",
            "bg": "q3",
        },
        "text": "How do you respond to the constant notifications while trying to complete the puzzle?",
        "options": [
            {
                "letter": "A",
                "text": "I silence all notifications immediately and focus entirely on the puzzle.",
                "scores": {"focus": 10, "stress": 2, "impulse": 8},
                "profile": "High Focus / Low Reactivity",
            },
            {
                "letter": "B",
                "text": "I glance at each notification but quickly return to the task.",
                "scores": {"focus": 6, "stress": 5, "impulse": 5},
                "profile": "Balanced / Moderate Distraction",
            },
            {
                "letter": "C",
                "text": "I keep getting pulled away by notifications and lose my place repeatedly.",
                "scores": {"focus": 2, "stress": 9, "impulse": 2},
                "profile": "Low Focus / High Reactivity",
            },
        ],
    },
]

# 兼容旧代码引用
SCENE    = QUESTIONS[0]["scene"]
QUESTION = QUESTIONS[0]

# ─────────────────────────── Helpers ─────────────────────────────────
def glow_divider():
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#1a7ad4,transparent);margin:1.5rem 0;"></div>', unsafe_allow_html=True)

def section_title(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:1.4rem;">
      <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.3rem;">
        <span style="font-size:1.5rem;">{icon}</span>
        <h2 style="margin:0;font-size:1.6rem;font-weight:800;
                   background:linear-gradient(90deg,#4dc3ff,#a8d8ff);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          {title}
        </h2>
      </div>
      {"<p style='margin:0;color:#5a8ab8;font-size:0.9rem;padding-left:2.2rem;'>"+subtitle+"</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)

def progress_steps(current):
    steps = ["Home", "Assessment", "Live Analysis", "Adjustment", "Report"]
    icons = ["🏠", "🎭", "📊", "🔄", "📋"]
    cols = st.columns(len(steps))
    for i, (col, step, icon) in enumerate(zip(cols, steps, icons)):
        with col:
            if i < current:
                color, bg, border = "#4dc3ff", "rgba(26,122,212,0.3)", "#2a8ae8"
            elif i == current:
                color, bg, border = "#ffffff", "rgba(13,79,168,0.6)", "#4dc3ff"
            else:
                color, bg, border = "#3a5a7a", "rgba(10,20,40,0.4)", "#1a3a5a"
            st.markdown(f"""
            <div style="text-align:center;background:{bg};border:1px solid {border};
                        border-radius:10px;padding:0.5rem 0.2rem;
                        box-shadow:{'0 0 12px rgba(77,195,255,0.3)' if i==current else 'none'}">
              <div style="font-size:1.1rem;">{icon}</div>
              <div style="font-size:0.68rem;color:{color};font-weight:{'700' if i==current else '400'};
                          letter-spacing:0.04em;">{step}</div>
            </div>
            """, unsafe_allow_html=True)

def compute_scores():
    answers      = st.session_state.answers       # {0:"A", 1:"B", 2:"C"}
    answer_times = st.session_state.answer_times  # {0:5.2, 1:3.1, 2:8.4}

    total_focus = total_stress = total_impulse = 0
    profiles = []
    for qi, q in enumerate(QUESTIONS):
        letter = answers.get(qi, "B")
        opt = next((o for o in q["options"] if o["letter"] == letter), q["options"][1])
        total_focus   += opt["scores"]["focus"]
        total_stress  += opt["scores"]["stress"]
        total_impulse += opt["scores"]["impulse"]
        profiles.append(opt["profile"])

    n = len(QUESTIONS)
    focus   = round(total_focus   / n)
    stress  = round(total_stress  / n)
    impulse = round(total_impulse / n)

    # 平均答题时间
    avg_time = round(sum(answer_times.values()) / max(len(answer_times), 1), 1)
    if avg_time < 3:
        time_tag, time_note = "Impulsive", "Responses were near-instant — may indicate habitual reactions."
    elif avg_time <= 10:
        time_tag, time_note = "Deliberate", "Response times suggest thoughtful consideration across scenarios."
    else:
        time_tag, time_note = "Hesitant", "Longer response times suggest difficulty deciding under pressure."

    overall = round((focus * 4 + (10 - stress) * 3 + impulse * 3) / 10 * 10)
    overall = max(0, min(100, overall))

    risk = "Low" if overall >= 70 else "Moderate" if overall >= 40 else "High"
    risk_color = "#00e676" if overall >= 70 else "#ffb300" if overall >= 40 else "#ff7043"

    # 最后一题的答案用于鸡汤文字个性化
    last_letter = answers.get(n - 1, "B")

    # 兼容旧字段
    st.session_state.answer      = last_letter
    st.session_state.answer_time = avg_time

    return {
        "focus": focus,
        "stress": stress,
        "impulse": impulse,
        "overall": overall,
        "risk": risk,
        "risk_color": risk_color,
        "profile": profiles[-1],
        "profiles_all": profiles,
        "answer_letter": last_letter,
        "answer_text": next((o["text"] for o in QUESTIONS[-1]["options"] if o["letter"] == last_letter), "—"),
        "answer_time": avg_time,
        "time_tag": time_tag,
        "time_note": time_note,
    }

def radar_svg(sc):
    labels  = ["Focus", "Stress\nControl", "Impulse\nControl", "Decisiveness", "Resilience", "Clarity"]
    stress_ctrl = 10 - sc["stress"]
    decisiveness = 8 if sc["time_tag"] == "Deliberate" else (5 if sc["time_tag"] == "Hesitant" else 4)
    resilience   = round((sc["focus"] + stress_ctrl) / 2)
    clarity      = round((sc["impulse"] + sc["focus"]) / 2)
    vals = [v / 10 for v in [sc["focus"], stress_ctrl, sc["impulse"], decisiveness, resilience, clarity]]

    cx, cy, r = 160, 160, 120
    n = len(labels)

    def pt(i, frac):
        angle = math.pi / 2 - (2 * math.pi * i / n)
        return cx + frac * r * math.cos(angle), cy - frac * r * math.sin(angle)

    grid = ""
    for ring in [0.25, 0.5, 0.75, 1.0]:
        pts = [pt(i, ring) for i in range(n)]
        d = " ".join([f"{'M' if j==0 else 'L'}{p[0]:.1f},{p[1]:.1f}" for j,p in enumerate(pts)]) + " Z"
        grid += f'<path d="{d}" fill="none" stroke="#1a3a6a" stroke-width="1"/>'

    axes = "".join([f'<line x1="{cx}" y1="{cy}" x2="{pt(i,1)[0]:.1f}" y2="{pt(i,1)[1]:.1f}" stroke="#1a3a6a" stroke-width="1"/>' for i in range(n)])

    dpts = [pt(i, vals[i]) for i in range(n)]
    dd = " ".join([f"{'M' if j==0 else 'L'}{p[0]:.1f},{p[1]:.1f}" for j,p in enumerate(dpts)]) + " Z"
    poly = f'<path d="{dd}" fill="rgba(26,122,212,0.28)" stroke="#4dc3ff" stroke-width="2"/>'
    dots = "".join([f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4" fill="#4dc3ff" stroke="#fff" stroke-width="1.5"/>' for p in dpts])

    lbls = ""
    for i, lbl in enumerate(labels):
        lx, ly = pt(i, 1.28)
        lines = lbl.split("\n")
        spans = "".join([f'<tspan x="{lx:.1f}" dy="13">{l}</tspan>' for l in lines])
        lbls += f'<text x="{lx:.1f}" y="{ly - len(lines)*6:.1f}" text-anchor="middle" font-size="10" fill="#7aaad4" font-family="Exo 2,sans-serif">{spans}</text>'

    return f'<svg viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg" width="100%" style="max-width:300px;display:block;margin:auto;">{grid}{axes}{poly}{dots}{lbls}</svg>'


# ══════════════════════════════════════════════════════════════════════
#  PAGE: HOME
# ══════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1rem;">
      <div style="font-size:3rem;margin-bottom:0.5rem;">🧠</div>
      <h1 style="margin:0;font-size:2.8rem;font-weight:800;letter-spacing:0.04em;
                 background:linear-gradient(135deg,#4dc3ff 0%,#a8d8ff 50%,#ffffff 100%);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        MindSight AI
      </h1>
      <p style="color:#4a8ab8;font-size:1rem;letter-spacing:0.12em;margin:0.3rem 0 0;">
        COGNITIVE · EMOTIONAL · BEHAVIORAL ASSESSMENT
      </p>
    </div>
    """, unsafe_allow_html=True)

    glow_divider()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="background:rgba(6,16,40,0.88);border:1px solid #1a4a8a;border-radius:16px;
                    padding:2rem;text-align:center;box-shadow:0 0 40px rgba(13,79,168,0.3);">

          <div style="font-size:2.5rem;margin-bottom:0.8rem;">🧩</div>
          <p style="color:#c8dff5;font-size:1rem;font-weight:600;margin-bottom:0.5rem;">
            Puzzle Under Pressure
          </p>
          <p style="color:#6a9abа;font-size:0.88rem;line-height:1.7;color:#7aaad4;margin-bottom:1.5rem;">
            You will be placed in three immersive high-pressure scenarios.<br>
            Answer <strong style="color:#4dc3ff;">3 questions</strong> — your choices and
            response times together generate a full cognitive profile.
          </p>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.7rem;margin-bottom:1.8rem;">
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.3rem;">🎭</div>
              <div style="font-size:0.72rem;color:#7aaad4;margin-top:0.3rem;">3 Immersive<br>Scenarios</div>
            </div>
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.3rem;">⏱️</div>
              <div style="font-size:0.72rem;color:#7aaad4;margin-top:0.3rem;">Response Time<br>Tracked</div>
            </div>
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.3rem;">📋</div>
              <div style="font-size:0.72rem;color:#7aaad4;margin-top:0.3rem;">AI-Generated<br>Report</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("▶  Start Assessment", use_container_width=True):
                st.session_state.page = "assessment"
                st.session_state.current_q = 0
                st.session_state.answers = {}
                st.session_state.answer_times = {}
                st.session_state.q_start_time = time.time()
                st.rerun()

    glow_divider()
    st.markdown('<p style="text-align:center;color:#2a5a7a;font-size:0.78rem;letter-spacing:0.08em;">⚠️  FOR RESEARCH &amp; EDUCATIONAL PURPOSES ONLY · NOT A CLINICAL DIAGNOSTIC TOOL</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  PAGE: ASSESSMENT  (三题版本)
# ══════════════════════════════════════════════════════════════════════
def page_assessment():
    qi = st.session_state.get("current_q", 0)
    q  = QUESTIONS[qi]
    scene = q["scene"]

    # 背景图：按题目序号选对应图
    _bg_map = {"q1": SCENE_IMG_Q1, "q2": SCENE_IMG_Q2, "q3": SCENE_IMG_Q3}
    bg_img = _bg_map.get(scene["bg"], SCENE_IMG_Q1)
    if bg_img:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url('data:image/png;base64,{bg_img}') center/cover no-repeat fixed !important;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: '';
            position: fixed;
            inset: 0;
            background: rgba(2, 6, 18, 0.45);
            z-index: 0;
            pointer-events: none;
        }}
        </style>
        """, unsafe_allow_html=True)

    progress_steps(1)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # 题目进度指示
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:0.8rem;display:flex;justify-content:center;gap:1rem;">
      <span style="background:rgba(0,0,0,0.6);border:1px solid #4dc3ff;border-radius:20px;
                   padding:0.3rem 1.2rem;font-family:'Share Tech Mono',monospace;
                   font-size:0.75rem;color:#4dc3ff;letter-spacing:0.15em;">
        ● VR ENVIRONMENT ACTIVE
      </span>
      <span style="background:rgba(0,0,0,0.6);border:1px solid #2a5a8a;border-radius:20px;
                   padding:0.3rem 1.2rem;font-family:'Share Tech Mono',monospace;
                   font-size:0.75rem;color:#7aaad4;letter-spacing:0.1em;">
        QUESTION {qi+1} / {len(QUESTIONS)}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # 题目进度小点
    dots = "".join([
        f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 4px;'
        f'background:{"#4dc3ff" if i == qi else ("#2a8ae8" if i < qi else "rgba(77,195,255,0.2)")};'
        f'box-shadow:{"0 0 8px #4dc3ff" if i == qi else "none"};"></span>'
        for i in range(len(QUESTIONS))
    ])
    st.markdown(f'<div style="text-align:center;margin-bottom:1rem;">{dots}</div>', unsafe_allow_html=True)

    # Scene banner
    st.markdown(f"""
    <div style="background:transparent;
                border:1px solid rgba(77,195,255,0.5);border-left:3px solid #4dc3ff;
                border-radius:10px;padding:1.2rem 1.6rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;">
        <span style="font-size:2rem;">{scene['emoji']}</span>
        <div>
          <div style="color:#4dc3ff;font-size:0.7rem;letter-spacing:0.14em;
                      font-family:'Share Tech Mono',monospace;text-shadow:0 0 8px #4dc3ff;">
            SCENARIO {qi+1} · {scene['label'].upper()}
          </div>
        </div>
      </div>
      <p style="color:#e0f2ff;font-size:0.92rem;line-height:1.65;margin:0;
                padding-left:0.8rem;font-style:italic;
                text-shadow:0 1px 6px rgba(0,0,0,0.9);">
        "{scene['desc']}"
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"""
    <div style="background:transparent;
                border-bottom:1px solid rgba(77,195,255,0.3);
                padding:0.8rem 0 0.8rem;margin-bottom:0.6rem;">
      <h3 style="color:#ffffff;font-size:1.12rem;font-weight:700;margin:0;
                 text-shadow:0 0 18px rgba(77,195,255,0.9), 0 2px 8px rgba(0,0,0,0.95);">
        💬 {q['text']}
      </h3>
    </div>
    """, unsafe_allow_html=True)

    # Radio 样式
    st.markdown("""
    <style>
    [data-testid="stRadio"] label {
        background: transparent !important;
        border: 1px solid rgba(77,195,255,0.45) !important;
        color: #ffffff !important;
        text-shadow: 0 1px 6px rgba(0,0,0,0.95) !important;
    }
    [data-testid="stRadio"] label:hover {
        background: transparent !important;
        border-color: #4dc3ff !important;
        color: #4dc3ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    option_labels = [f"  {o['letter']}.  {o['text']}" for o in q["options"]]
    choice = st.radio("", option_labels, key=f"q_choice_{qi}", label_visibility="collapsed")

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    is_last = (qi == len(QUESTIONS) - 1)
    col_back, col_space, col_next = st.columns([1, 3, 1])

    with col_back:
        if st.button("← Back", use_container_width=True):
            if qi == 0:
                st.session_state.page = "home"
            else:
                st.session_state.current_q = qi - 1
                st.session_state.q_start_time = time.time()
            st.rerun()

    with col_next:
        btn_label = "Analyse ✦" if is_last else f"Next  ›"
        if st.button(btn_label, use_container_width=True):
            elapsed = time.time() - (st.session_state.q_start_time or time.time())
            letter = choice.strip().split(".")[0].strip()
            st.session_state.answers[qi]      = letter
            st.session_state.answer_times[qi] = round(elapsed, 2)

            if is_last:
                st.session_state.scores = compute_scores()
                st.session_state.page   = "analysis"
            else:
                st.session_state.current_q  = qi + 1
                st.session_state.q_start_time = time.time()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
#  PAGE: LIVE ANALYSIS
# ══════════════════════════════════════════════════════════════════════
def page_analysis():
    sc = st.session_state.scores
    if not sc:
        st.session_state.page = "assessment"
        st.rerun()

    progress_steps(2)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section_title("📊", "Live Cognitive Analysis", "Real-time profile generated from your response")

    glow_divider()

    # Status bar
    time_color = "#00e676" if sc["time_tag"]=="Deliberate" else ("#ffb300" if sc["time_tag"]=="Hesitant" else "#ff7043")
    st.markdown(f"""
    <div style="background:rgba(4,14,32,0.9);border:1px solid #0d3a6a;border-radius:10px;
                padding:0.7rem 1.4rem;margin-bottom:1.2rem;font-family:'Share Tech Mono',monospace;
                font-size:0.78rem;color:#3a7ab8;display:flex;gap:2.5rem;flex-wrap:wrap;">
      <span>● ANALYSIS COMPLETE</span>
      <span>RESPONSE TIME: <span style="color:#4dc3ff;">{sc['answer_time']}s</span></span>
      <span>DECISION STYLE: <span style="color:{time_color};">{sc['time_tag'].upper()}</span></span>
      <span>PROFILE: <span style="color:#4dc3ff;">{sc['profile']}</span></span>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Score", f"{sc['overall']} / 100")
    col2.metric("Focus Level", f"{sc['focus']} / 10")
    col3.metric("Stress Load", f"{sc['stress']} / 10")
    col4.metric("Impulse Control", f"{sc['impulse']} / 10")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.5rem;">
            COGNITIVE PROFILE RADAR
          </div>
        """, unsafe_allow_html=True)
        st.markdown(radar_svg(sc), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        stress_ctrl = 10 - sc["stress"]
        bars = [
            ("Focus", sc["focus"], "#4dc3ff"),
            ("Stress Control", stress_ctrl, "#00e676" if stress_ctrl>=6 else "#ffb300" if stress_ctrl>=3 else "#ff7043"),
            ("Impulse Control", sc["impulse"], "#a78bfa"),
        ]
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
            INDICATOR BREAKDOWN
          </div>
        """, unsafe_allow_html=True)
        for name, val, color in bars:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:0.85rem;color:#a8ccee;">{name}</span>
                <span style="font-size:0.82rem;color:{color};font-family:'Share Tech Mono',monospace;">{val}/10</span>
              </div>
              <div style="background:rgba(10,28,60,0.8);border-radius:4px;height:8px;">
                <div style="width:{val*10}%;background:linear-gradient(90deg,{color}88,{color});
                            height:8px;border-radius:4px;box-shadow:0 0 8px {color}66;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Response time note
        st.markdown(f"""
        <div style="margin-top:1rem;background:rgba(13,50,100,0.4);border-left:3px solid {time_color};
                    border-radius:0 8px 8px 0;padding:0.7rem 1rem;">
          <div style="font-size:0.72rem;color:{time_color};font-family:'Share Tech Mono',monospace;margin-bottom:0.2rem;">
            ⏱ RESPONSE TIME · {sc['answer_time']}s · {sc['time_tag'].upper()}
          </div>
          <div style="font-size:0.82rem;color:#a8ccee;">{sc['time_note']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    glow_divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("⟶  Proceed to Adaptive Adjustment", use_container_width=True):
            st.session_state.page = "adjustment"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
#  PAGE: ADAPTIVE ADJUSTMENT
# ══════════════════════════════════════════════════════════════════════
def page_adjustment():
    sc = st.session_state.scores

    # ── 全页背景：治愈图 ──────────────────────────────────────────────
    if ADJUSTMENT_IMG:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url('data:image/png;base64,{ADJUSTMENT_IMG}') center/cover no-repeat fixed !important;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: '';
            position: fixed;
            inset: 0;
            background: rgba(2, 8, 18, 0.32);
            z-index: 0;
            pointer-events: none;
        }}
        </style>
        """, unsafe_allow_html=True)

    # ── 所有文本框透明样式 ─────────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background: transparent !important;
        border: 1px solid rgba(77,195,255,0.35) !important;
    }
    [data-testid="stMetricValue"] { text-shadow: 0 0 12px rgba(77,195,255,0.8) !important; }
    </style>
    """, unsafe_allow_html=True)

    progress_steps(3)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # 页面标题 — 透明
    st.markdown("""
    <div style="text-align:center;margin-bottom:0.4rem;">
      <span style="background:transparent;border:1px solid rgba(77,195,255,0.5);border-radius:20px;
                   padding:0.3rem 1.2rem;font-family:'Share Tech Mono',monospace;
                   font-size:0.75rem;color:#4dc3ff;letter-spacing:0.15em;
                   text-shadow:0 0 10px #4dc3ff;">
        ✦ ADAPTIVE ENVIRONMENT ACTIVATED
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.2rem;padding-left:0.2rem;">
      <h2 style="margin:0.6rem 0 0.2rem;font-size:1.5rem;font-weight:800;
                 background:linear-gradient(90deg,#4dc3ff,#a8d8ff);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🔄 Adaptive Scene Adjustment
      </h2>
      <p style="margin:0;color:#c8e8ff;font-size:0.88rem;
                text-shadow:0 1px 6px rgba(0,0,0,0.9);">
        Your environment has been recalibrated. Take a breath — you're in a safer space now.
      </p>
    </div>
    """, unsafe_allow_html=True)

    glow_divider()

    # ── 鸡汤文字 — 全透明文本框 ──────────────────────────────────────
    # 根据三题综合选出最高压力情境来定制内容
    answers = st.session_state.get("answers", {})
    q2_ans = answers.get(1, "B")   # proposal题(Q2)的答案决定鸡汤

    HEALING_MESSAGES = {
        "A": {
            "title": "Criticism doesn't diminish what you built.",
            "body": "You felt the sting — and still chose to look for what was useful in it. That's not easy. Most people either shut down or fight back. You did something harder: you stayed open. The work you put in doesn't disappear because someone dismissed it in a room. It stays with you, and so does the resilience you just showed.",
        },
        "B": {
            "title": "Holding it together is its own kind of strength.",
            "body": "You were upset — and you had every right to be. But you kept going. You stayed in the room, you kept your composure, even when your mind was elsewhere. That gap between what you feel and what you show takes real discipline to hold. Give yourself credit for that. The frustration will pass. The steadiness you showed today won't.",
        },
        "C": {
            "title": "Shutting down after being hurt is not a flaw.",
            "body": "When someone dismisses your work without reason, silence can be the most honest response. You didn't pretend it was fine — because it wasn't. That kind of sensitivity isn't weakness; it means you care deeply about what you create. The harder days are the ones that quietly build your threshold. You're more capable than this moment made you feel.",
        },
    }
    msg = HEALING_MESSAGES.get(q2_ans, HEALING_MESSAGES["B"])

    st.markdown(f"""
    <div style="background:transparent;
                border:1px solid rgba(77,195,255,0.4);border-left:4px solid #4dc3ff;
                border-radius:14px;padding:1.8rem 2rem;margin-bottom:1.4rem;">
      <div style="font-size:0.72rem;color:#4dc3ff;letter-spacing:0.14em;
                  font-family:'Share Tech Mono',monospace;margin-bottom:0.7rem;
                  text-shadow:0 0 8px #4dc3ff;">
        ✦ A MESSAGE FOR YOU
      </div>
      <div style="font-size:1.15rem;font-weight:700;color:#ffffff;margin-bottom:0.9rem;line-height:1.4;
                  text-shadow:0 0 20px rgba(77,195,255,0.6), 0 2px 8px rgba(0,0,0,0.95);">
        {msg['title']}
      </div>
      <p style="color:#e0f2ff;font-size:0.93rem;line-height:1.85;margin:0;
                text-shadow:0 1px 8px rgba(0,0,0,0.95);">
        {msg['body']}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 指标 — 透明卡片 ───────────────────────────────────────────────
    st.markdown("""
    <div style="background:transparent;border:1px solid rgba(77,195,255,0.3);
                border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;">
      <div style="color:#4dc3ff;font-size:0.73rem;letter-spacing:0.12em;
                  font-family:'Share Tech Mono',monospace;margin-bottom:1rem;
                  text-shadow:0 0 8px #4dc3ff;">
        COGNITIVE INDICATORS · POST-ADJUSTMENT
      </div>
    """, unsafe_allow_html=True)

    stress_ctrl = 10 - sc.get("stress", 5)
    indicators = [
        ("🔵", "Focus Level",     sc.get("focus", 0),  "#4dc3ff"),
        ("🔴", "Stress Load",     sc.get("stress", 0), "#ff7043" if sc.get("stress",0)>=7 else "#ffb300"),
        ("🟣", "Impulse Control", sc.get("impulse", 0),"#a78bfa"),
        ("🟢", "Stress Control",  stress_ctrl,          "#00e676" if stress_ctrl>=6 else "#ffb300"),
    ]
    for icon, name, val, color in indicators:
        st.markdown(f"""
      <div style="display:flex;justify-content:space-between;align-items:center;
                  padding:0.55rem 0;border-bottom:1px solid rgba(77,195,255,0.15);">
        <div style="display:flex;align-items:center;gap:0.6rem;">
          <span>{icon}</span>
          <span style="color:#e0f2ff;font-size:0.88rem;
                       text-shadow:0 1px 6px rgba(0,0,0,0.9);">{name}</span>
        </div>
        <div style="text-align:right;min-width:110px;">
          <span style="color:{color};font-family:'Share Tech Mono',monospace;font-size:0.85rem;
                       font-weight:600;text-shadow:0 0 8px {color};">{val}/10</span>
          <div style="background:rgba(10,28,60,0.4);border-radius:3px;height:4px;
                      width:80px;margin-top:4px;margin-left:auto;">
            <div style="width:{val*10}%;background:{color};height:4px;border-radius:3px;
                        box-shadow:0 0 6px {color};"></div>
          </div>
        </div>
      </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    glow_divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("📋  View Full Session Report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
#  PAGE: REPORT
# ══════════════════════════════════════════════════════════════════════
def page_report():
    sc = st.session_state.scores

    progress_steps(4)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section_title("📋", "Session Report", "Comprehensive AI-generated cognitive & emotional assessment")

    overall = sc.get("overall", 50)
    risk_label = sc.get("risk", "Moderate")
    risk_color = sc.get("risk_color", "#ffb300")

    # Score banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(6,18,44,0.95),rgba(10,30,70,0.9));
                border:1px solid #2a6aba;border-radius:14px;padding:1.5rem 2rem;margin-bottom:1.2rem;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 0 30px rgba(26,122,212,0.25);">
      <div>
        <div style="color:#7aaad4;font-size:0.78rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;">
          OVERALL COGNITIVE SCORE
        </div>
        <div style="font-size:3.5rem;font-weight:800;color:#4dc3ff;font-family:'Share Tech Mono',monospace;line-height:1;margin-top:0.2rem;">
          {overall}<span style="font-size:1.5rem;color:#3a7ab8;">/100</span>
        </div>
        <div style="color:#5a8ab8;font-size:0.82rem;margin-top:0.4rem;">
          Profile: <span style="color:#a8ccee;">{sc.get('profile','—')}</span>
        </div>
      </div>
      <div style="text-align:right;">
        <div style="color:#7aaad4;font-size:0.78rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;">RISK LEVEL</div>
        <div style="font-size:1.6rem;font-weight:700;color:{risk_color};margin-top:0.2rem;">{risk_label}</div>
        <div style="color:#5a8ab8;font-size:0.8rem;margin-top:0.3rem;">
          Response Time: <span style="color:#4dc3ff;">{sc.get('answer_time',0)}s</span>
          · <span style="color:{sc.get('risk_color','#ffb300')}">{sc.get('time_tag','—')}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stress Relief After Adjustment ───────────────────────────────
    focus_before   = max(1,  sc.get("focus",   5) - 3)
    stress_before  = min(10, sc.get("stress",  5) + 3)
    impulse_before = max(1,  sc.get("impulse", 5) - 2)
    overall_before = max(10, sc.get("overall", 50) - 22)

    stress_drop  = stress_before - sc.get("stress", 5)
    focus_gain   = sc.get("focus", 5) - focus_before
    overall_gain = sc.get("overall", 50) - overall_before

    answers = st.session_state.get("answers", {})
    q2_ans  = answers.get(1, "B")
    RELIEF_MSGS = {
        "A": "After entering the adaptive environment, your stress indicators show a meaningful decline. Your openness to feedback has translated into faster cognitive recovery — you returned to baseline focus within the adjustment window.",
        "B": "The adaptive scene allowed your emotional regulation system to reset. Though you held tension during the assessment, the environmental shift provided enough cognitive distance to reduce your stress load and partially restore attentional clarity.",
        "C": "Emotional shutdown often signals a protective response — and the adaptive environment was designed for exactly this. The low-stimulation, warm setting reduced cortisol-equivalent load and created space for your nervous system to begin recovery.",
    }
    relief_note = RELIEF_MSGS.get(q2_ans, RELIEF_MSGS["B"])

    st.markdown(f"""
    <div style="background:rgba(6,24,14,0.88);border:1px solid #1a6a2a;border-radius:14px;
                padding:1.4rem 1.8rem;margin-bottom:1.2rem;
                box-shadow:0 0 20px rgba(0,230,118,0.08);">
      <div style="color:#00e676;font-size:0.74rem;letter-spacing:0.12em;
                  font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
        🌿 STRESS RELIEF REPORT · POST ADAPTIVE ADJUSTMENT
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.8rem;margin-bottom:1rem;">
        <div style="background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.3);
                    border-radius:10px;padding:0.9rem;text-align:center;">
          <div style="font-size:0.7rem;color:#5ab87a;font-family:'Share Tech Mono',monospace;margin-bottom:0.3rem;">STRESS REDUCTION</div>
          <div style="font-size:1.6rem;font-weight:800;color:#00e676;font-family:'Share Tech Mono',monospace;">
            ▼ {stress_drop}/10
          </div>
        </div>
        <div style="background:rgba(77,195,255,0.08);border:1px solid rgba(77,195,255,0.3);
                    border-radius:10px;padding:0.9rem;text-align:center;">
          <div style="font-size:0.7rem;color:#5a9ab8;font-family:'Share Tech Mono',monospace;margin-bottom:0.3rem;">FOCUS RECOVERY</div>
          <div style="font-size:1.6rem;font-weight:800;color:#4dc3ff;font-family:'Share Tech Mono',monospace;">
            ▲ {focus_gain}/10
          </div>
        </div>
        <div style="background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.3);
                    border-radius:10px;padding:0.9rem;text-align:center;">
          <div style="font-size:0.7rem;color:#5ab87a;font-family:'Share Tech Mono',monospace;margin-bottom:0.3rem;">OVERALL GAIN</div>
          <div style="font-size:1.6rem;font-weight:800;color:#00e676;font-family:'Share Tech Mono',monospace;">
            ▲ +{overall_gain}
          </div>
        </div>
      </div>
      <p style="color:#8ad4a8;font-size:0.87rem;line-height:1.7;margin:0;
                border-left:3px solid rgba(0,230,118,0.4);padding-left:1rem;">
        {relief_note}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Before / After 心理状态对比
    st.markdown(f"""
    <div style="background:rgba(6,18,44,0.92);border:1px solid #1a4a8a;border-radius:14px;
                padding:1.4rem 1.8rem;margin-bottom:1.2rem;">
      <div style="color:#4dc3ff;font-size:0.74rem;letter-spacing:0.12em;
                  font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
        ✦ PSYCHOLOGICAL STATE · BEFORE vs AFTER ADAPTIVE ADJUSTMENT
      </div>
      <div style="display:flex;gap:1.2rem;flex-wrap:wrap;">

        <div style="background:rgba(80,15,15,0.35);border:1px solid #5a1a1a;border-radius:10px;padding:1rem;flex:1;min-width:280px;">
          <div style="color:#ff7043;font-size:0.7rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
            BEFORE ADJUSTMENT
          </div>
          {"".join([
            f'<div style="margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:0.82rem;color:#c8a090;">{n}</span><span style="font-size:0.8rem;color:{c};font-family:\'Share Tech Mono\',monospace;">{v}/10</span></div><div style="background:rgba(10,20,40,0.6);border-radius:3px;height:5px;"><div style="width:{v*10}%;background:{c};height:5px;border-radius:3px;opacity:0.7;"></div></div></div>'
            for n, v, c in [("Focus", focus_before, "#ff7043"), ("Stress Load", stress_before, "#ff7043"), ("Impulse Control", impulse_before, "#ff7043")]
          ])}
          <div style="margin-top:0.8rem;text-align:center;color:#ff7043;font-size:1.4rem;
                      font-family:'Share Tech Mono',monospace;">{overall_before}<span style="font-size:0.85rem;color:#8a3a2a;">/100</span></div>
        </div>

        <div style="background:rgba(10,40,20,0.45);border:1px solid #1a6a2a;border-radius:10px;padding:1rem;
                    box-shadow:0 0 16px rgba(0,230,118,0.1);flex:1;min-width:280px;">
          <div style="color:#00e676;font-size:0.7rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
            AFTER ADJUSTMENT ✦
          </div>
          {"".join([
            f'<div style="margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="font-size:0.82rem;color:#a8ccee;">{n}</span><span style="font-size:0.8rem;color:{c};font-family:\'Share Tech Mono\',monospace;">{v}/10</span></div><div style="background:rgba(10,20,40,0.6);border-radius:3px;height:5px;"><div style="width:{v*10}%;background:{c};height:5px;border-radius:3px;box-shadow:0 0 6px {c}66;"></div></div></div>'
            for n, v, c in [("Focus", sc.get("focus",5), "#4dc3ff"), ("Stress Load", sc.get("stress",5), "#00e676" if sc.get("stress",5)<5 else "#ffb300"), ("Impulse Control", sc.get("impulse",5), "#a78bfa")]
          ])}
          <div style="margin-top:0.8rem;text-align:center;color:#00e676;font-size:1.4rem;
                      font-family:'Share Tech Mono',monospace;">{overall}<span style="font-size:0.85rem;color:#2a7a4a;">/100</span>
            <span style="font-size:0.75rem;color:#00e676;margin-left:0.5rem;">▲ +{overall - overall_before}</span>
          </div>
        </div>

      </div>
      <div style="margin-top:1rem;text-align:center;color:#5a9a7a;font-size:0.82rem;">
        Adaptive environmental adjustment has helped recalibrate your cognitive and emotional state. 🌿
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        stress_ctrl = 10 - sc.get("stress", 5)
        indicators = [
            ("🔵", "Focus Level",      sc.get("focus",0),   "#4dc3ff"),
            ("🔴", "Stress Load",      sc.get("stress",0),  "#ff7043" if sc.get("stress",0)>=7 else "#ffb300"),
            ("🟣", "Impulse Control",  sc.get("impulse",0), "#a78bfa"),
            ("🟢", "Stress Control",   stress_ctrl,         "#00e676" if stress_ctrl>=6 else "#ffb300"),
        ]
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
            KEY INDICATORS
          </div>
        """, unsafe_allow_html=True)
        for icon, name, val, color in indicators:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.5rem 0;border-bottom:1px solid #0d2a4a;">
              <div style="display:flex;align-items:center;gap:0.5rem;">
                <span>{icon}</span>
                <span style="color:#a8ccee;font-size:0.88rem;">{name}</span>
              </div>
              <div style="text-align:right;">
                <span style="color:{color};font-family:'Share Tech Mono',monospace;font-size:0.85rem;font-weight:600;">{val}/10</span>
                <div style="background:rgba(10,28,60,0.8);border-radius:3px;height:4px;width:80px;margin-top:3px;">
                  <div style="width:{val*10}%;background:{color};height:4px;border-radius:3px;"></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        # Selected answer recap
        st.markdown(f"""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;margin-bottom:0.8rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
            YOUR RESPONSE
          </div>
          <div style="background:rgba(13,50,100,0.5);border-left:3px solid #2a8ae8;border-radius:0 8px 8px 0;padding:0.8rem 1rem;">
            <div style="font-size:0.72rem;color:#3a7ab8;font-family:'Share Tech Mono',monospace;margin-bottom:0.3rem;">
              Option {sc.get('answer_letter','?')} · {sc.get('answer_time',0)}s · {sc.get('time_tag','—')}
            </div>
            <div style="color:#c8dff5;font-size:0.9rem;line-height:1.5;">"{sc.get('answer_text','—')}"</div>
          </div>
          <div style="margin-top:0.8rem;padding:0.6rem;background:rgba(10,28,60,0.4);border-radius:8px;">
            <div style="font-size:0.72rem;color:#5a8ab8;margin-bottom:0.2rem;">TIME ANALYSIS</div>
            <div style="font-size:0.84rem;color:#a8ccee;">{sc.get('time_note','—')}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    glow_divider()

    # AI Recommendations
    recs = []
    if sc.get("focus", 5) < 5:
        recs.append(("🎯", "Attention Training",
            "Structured focus sessions using the Pomodoro technique (25-min blocks) can rebuild attention spans. Limit multitasking and create notification-free work windows."))
    if sc.get("stress", 5) >= 7:
        recs.append(("🧘", "Stress Management",
            "Consider mindfulness-based stress reduction (MBSR) techniques. Daily breathing exercises (4-7-8 pattern) can significantly lower baseline stress reactivity."))
    if sc.get("impulse", 5) < 5:
        recs.append(("⚡", "Impulse Regulation",
            "Practice deliberate pause techniques before reacting to interruptions. Cognitive reframing can help build stronger inhibitory control over distracting stimuli."))
    if not recs:
        recs.append(("✨", "Maintain & Enhance",
            "Your cognitive profile is strong. You demonstrate effective focus management under pressure. Consider advanced dual-task training to push your limits further."))

    st.markdown("""
    <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.4rem;margin-bottom:1rem;">
      <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
        ✦ AI RECOMMENDATION
      </div>
    """, unsafe_allow_html=True)
    for icon, title, text in recs:
        st.markdown(f"""
      <div style="background:rgba(13,50,100,0.4);border-left:3px solid #2a8ae8;
                  border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-bottom:0.6rem;">
        <div style="color:#4dc3ff;font-size:0.82rem;font-weight:600;margin-bottom:0.3rem;">{icon} {title}</div>
        <p style="color:#a8ccee;font-size:0.86rem;line-height:1.6;margin:0;">{text}</p>
      </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔁  Retake Assessment", use_container_width=True):
            for key in ["answer", "answer_time", "q_start_time", "scores", "answers", "answer_times", "current_q"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "home"
            init_state()
            st.rerun()
    with col_b:
        report_txt = f"""MINDSIGHT AI · SESSION REPORT
==============================
Overall Score  : {overall}/100
Risk Level     : {risk_label}
Profile        : {sc.get('profile','—')}

INDICATORS
Focus          : {sc.get('focus','?')}/10
Stress Load    : {sc.get('stress','?')}/10
Impulse Control: {sc.get('impulse','?')}/10

RESPONSE
Option {sc.get('answer_letter','?')}: {sc.get('answer_text','—')}
Time           : {sc.get('answer_time',0)}s ({sc.get('time_tag','—')})
Note           : {sc.get('time_note','—')}

AI RECOMMENDATION
{'  '.join([t for _,t,_ in recs])}
"""
        st.download_button("⬇  Export Report", report_txt, "mindsight_report.txt", "text/plain", use_container_width=True)
    with col_c:
        if st.button("🏠  Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    glow_divider()
    st.markdown('<p style="text-align:center;color:#2a5a7a;font-size:0.75rem;letter-spacing:0.06em;">⚠️ This report is for educational purposes only and does not constitute a clinical diagnosis.</p>', unsafe_allow_html=True)


# ─────────────────────────── Router ──────────────────────────────────
page = st.session_state.get("page", "home")
if   page == "home":       page_home()
elif page == "assessment": page_assessment()
elif page == "analysis":   page_analysis()
elif page == "adjustment": page_adjustment()
elif page == "report":     page_report()
else:                      page_home()
