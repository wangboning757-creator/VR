import streamlit as st
import time
import random
import math

# ─────────────────────────── Page Config ────────────────────────────
st.set_page_config(
    page_title="MindSight AI · Cognitive Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────── Global CSS ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&family=Share+Tech+Mono&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #020b1a !important;
    color: #c8dff5 !important;
    font-family: 'Exo 2', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, #0a2040 0%, #020b1a 60%) !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
section[data-testid="stMain"] > div { padding-top: 1rem !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1100px !important; margin: auto; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #020b1a; }
::-webkit-scrollbar-thumb { background: #1a4a8a; border-radius: 3px; }

/* ── Streamlit button override ── */
.stButton > button {
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
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1a6cd4, #2a9af0) !important;
    box-shadow: 0 0 22px rgba(42,154,240,0.55) !important;
    transform: translateY(-1px) !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label {
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
}
[data-testid="stRadio"] label:hover {
    background: rgba(26,74,138,0.7) !important;
    border-color: #2a8ae8 !important;
    color: #e8f4ff !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: rgba(10,30,60,0.8) !important;
    border: 1px solid #1a3a6a !important;
    border-radius: 10px !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stMetricLabel"] { color: #7aaad4 !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: #4dc3ff !important; font-family: 'Share Tech Mono', monospace !important; }

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #1a7ad4, #4dc3ff) !important; }
[data-testid="stProgress"] { background: rgba(10,30,60,0.5) !important; border-radius: 4px !important; }

/* ── Divider ── */
hr { border-color: #0d2a4a !important; margin: 1.5rem 0 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(8,22,45,0.8) !important;
    border: 1px solid #1a3a6a !important;
    border-radius: 10px !important;
}

/* ── Code / monospace ── */
code { font-family: 'Share Tech Mono', monospace !important; color: #4dc3ff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── State Init ─────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "q_index": 0,
        "answers": [],
        "answer_times": [],
        "q_start_time": None,
        "scene_index": 0,
        "analysis_done": False,
        "scores": {},
        "adjustment_viewed": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────── Data ────────────────────────────────────
SCENES = [
    {
        "name": "Quiet Library",
        "emoji": "📚",
        "desc": "A calm reading room with soft ambient light. Minimal noise, low stimulation.",
        "bg_color": "#061830",
        "accent": "#2a7ae8",
    },
    {
        "name": "City Café",
        "emoji": "☕",
        "desc": "A lively coffee shop with background chatter, music, and moderate activity.",
        "bg_color": "#0a1a2a",
        "accent": "#d48a1a",
    },
    {
        "name": "Forest Path",
        "emoji": "🌲",
        "desc": "Walking through a sunlit forest. Natural sounds, gentle movement.",
        "bg_color": "#061820",
        "accent": "#1aaa5a",
    },
]

QUESTIONS = [
    {
        "id": "stress",
        "scene_label": "Scene 01 · Social Interaction",
        "scene_desc": "You are in a meeting room. Your manager asks you to present your work unexpectedly.",
        "scene_emoji": "🏢",
        "question": "How do you feel right now?",
        "options": [
            ("A", "Completely calm — I'm ready for anything.", 10, "low"),
            ("B", "A little nervous, but I can manage.", 6, "medium"),
            ("C", "Quite anxious — I need a moment.", 3, "high"),
            ("D", "Overwhelmed. I want to leave.", 0, "critical"),
        ],
    },
    {
        "id": "attention",
        "scene_label": "Scene 02 · Cognitive Load",
        "scene_desc": "You are solving a complex puzzle under a 5-minute timer. Notifications keep popping up.",
        "scene_emoji": "🧩",
        "question": "How well can you focus on the task?",
        "options": [
            ("A", "Fully focused — distractions don't affect me.", 10, "high"),
            ("B", "Mostly focused with minor interruptions.", 7, "medium"),
            ("C", "Struggling to concentrate, losing track.", 3, "low"),
            ("D", "Cannot focus at all — feel paralysed.", 0, "critical"),
        ],
    },
    {
        "id": "emotion",
        "scene_label": "Scene 03 · Emotional Resilience",
        "scene_desc": "A friend cancels important plans at the last minute without explanation.",
        "scene_emoji": "💬",
        "question": "What is your immediate emotional response?",
        "options": [
            ("A", "Completely fine — things happen.", 10, "stable"),
            ("B", "Mildly disappointed, but I'll move on.", 7, "calm"),
            ("C", "Frustrated and a bit hurt.", 3, "unstable"),
            ("D", "Very upset — this ruins my day.", 0, "volatile"),
        ],
    },
]

# ─────────────────────────── Helper Components ───────────────────────
def card(content_fn, border_color="#1a4a8a", bg="rgba(8,22,48,0.85)"):
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border_color};border-radius:14px;
                padding:1.6rem 1.8rem;margin-bottom:1rem;
                box-shadow:0 0 24px rgba(13,79,168,0.18);">
    """, unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)

def badge(text, color="#1a7ad4", bg="rgba(26,122,212,0.15)"):
    return f'<span style="background:{bg};color:{color};border:1px solid {color};border-radius:20px;padding:2px 10px;font-size:0.75rem;font-family:\'Share Tech Mono\',monospace;letter-spacing:0.06em;">{text}</span>'

def section_title(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
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

def glow_divider():
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,#1a7ad4,transparent);margin:1.5rem 0;"></div>', unsafe_allow_html=True)

# ─────────────────────────── Score Engine ────────────────────────────
def compute_scores():
    answers = st.session_state.answers
    times = st.session_state.answer_times

    if len(answers) < 3:
        return {}

    raw = {}
    for i, q in enumerate(QUESTIONS):
        ans_letter = answers[i]
        for opt in q["options"]:
            if opt[0] == ans_letter:
                raw[q["id"]] = {"score": opt[2], "tag": opt[3]}
                break

    # Time factor: faster = more decisive
    avg_time = sum(times) / len(times) if times else 5
    decisiveness = max(0, min(100, 100 - (avg_time - 2) * 8))

    stress_score = raw.get("stress", {}).get("score", 5)
    attention_score = raw.get("attention", {}).get("score", 5)
    emotion_score = raw.get("emotion", {}).get("score", 5)

    overall = round((stress_score * 3 + attention_score * 3 + emotion_score * 4) / 10)
    overall = max(0, min(100, overall * 10))

    def level(s):
        if s >= 8: return ("High", "#00e676")
        if s >= 5: return ("Medium", "#ffb300")
        if s >= 2: return ("Low", "#ff7043")
        return ("Critical", "#f44336")

    return {
        "stress": {"score": stress_score, "label": level(stress_score)},
        "attention": {"score": attention_score, "label": level(attention_score)},
        "emotion": {"score": emotion_score, "label": level(emotion_score)},
        "decisiveness": round(decisiveness),
        "overall": overall,
        "avg_time": round(avg_time, 1),
        "raw": raw,
    }

def pick_scene(scores):
    if not scores:
        return SCENES[0]
    s = scores.get("stress", {}).get("score", 5)
    a = scores.get("attention", {}).get("score", 5)
    avg = (s + a) / 2
    if avg >= 7:
        return SCENES[1]
    elif avg >= 4:
        return SCENES[2]
    else:
        return SCENES[0]

# ──────────────────────────────────────────────────────────────────────
#  PAGE 0 · HOME
# ──────────────────────────────────────────────────────────────────────
def page_home():
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
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
        <div style="background:rgba(8,22,48,0.85);border:1px solid #1a4a8a;border-radius:16px;
                    padding:2rem;text-align:center;box-shadow:0 0 40px rgba(13,79,168,0.25);">
          <p style="color:#7aaad4;font-size:0.95rem;line-height:1.7;margin-bottom:1.5rem;">
            This assessment uses <strong style="color:#4dc3ff;">scenario-based cognitive probes</strong>
            to evaluate your stress resilience, attention stability, and emotional regulation
            through three immersive interactive scenes.
          </p>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.8rem;margin-bottom:1.8rem;">
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.4rem;">🎭</div>
              <div style="font-size:0.75rem;color:#7aaad4;margin-top:0.3rem;">3 Immersive<br>Scenarios</div>
            </div>
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.4rem;">⚡</div>
              <div style="font-size:0.75rem;color:#7aaad4;margin-top:0.3rem;">Real-time<br>Analysis</div>
            </div>
            <div style="background:rgba(13,50,100,0.5);border:1px solid #1a3a6a;border-radius:10px;padding:0.8rem;">
              <div style="font-size:1.4rem;">📋</div>
              <div style="font-size:0.75rem;color:#7aaad4;margin-top:0.3rem;">AI-Generated<br>Report</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("▶  Start Assessment", use_container_width=True):
                st.session_state.page = "assessment"
                st.session_state.q_index = 0
                st.session_state.answers = []
                st.session_state.answer_times = []
                st.session_state.q_start_time = time.time()
                st.rerun()

    glow_divider()

    st.markdown("""
    <p style="text-align:center;color:#2a5a7a;font-size:0.78rem;letter-spacing:0.08em;">
      ⚠️  FOR RESEARCH &amp; EDUCATIONAL PURPOSES ONLY · NOT A CLINICAL DIAGNOSTIC TOOL
    </p>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────
#  PAGE 1 · ASSESSMENT
# ──────────────────────────────────────────────────────────────────────
def page_assessment():
    qi = st.session_state.q_index

    if qi >= len(QUESTIONS):
        st.session_state.scores = compute_scores()
        st.session_state.page = "analysis"
        st.rerun()
        return

    progress_steps(1)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    q = QUESTIONS[qi]
    progress_val = (qi) / len(QUESTIONS)

    # Header
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">
      <div>{badge(f"Question {qi+1} / {len(QUESTIONS)}", '#4dc3ff')}</div>
      <div style="font-family:'Share Tech Mono',monospace;color:#3a7ab8;font-size:0.8rem;">
        {q['scene_label']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress_val)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    # Scene Card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(6,24,56,0.95),rgba(10,35,75,0.9));
                border:1px solid #1a4a8a;border-left:4px solid #2a8ae8;
                border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:1.2rem;
                box-shadow:0 0 30px rgba(26,122,212,0.2);">
      <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.6rem;">
        <span style="font-size:2rem;">{q['scene_emoji']}</span>
        <div>
          <div style="color:#4dc3ff;font-size:0.78rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;">
            SCENARIO
          </div>
          <div style="color:#c8dff5;font-size:1.05rem;font-weight:600;">{q['scene_label']}</div>
        </div>
      </div>
      <p style="color:#8ab8d8;font-size:0.95rem;line-height:1.6;margin:0;font-style:italic;">
        "{q['scene_desc']}"
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"""
    <h3 style="color:#e8f4ff;font-size:1.2rem;font-weight:700;margin-bottom:1rem;">
      💬 {q['question']}
    </h3>
    """, unsafe_allow_html=True)

    option_labels = [f"  {opt[0]}.  {opt[1]}" for opt in q["options"]]
    choice = st.radio(
        "Choose your response:",
        option_labels,
        key=f"q_{qi}",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    col_prev, col_space, col_next = st.columns([1, 3, 1])
    with col_prev:
        if qi > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.q_index -= 1
                if st.session_state.answers:
                    st.session_state.answers.pop()
                if st.session_state.answer_times:
                    st.session_state.answer_times.pop()
                st.session_state.q_start_time = time.time()
                st.rerun()
    with col_next:
        label = "Next →" if qi < len(QUESTIONS) - 1 else "Analyse ✦"
        if st.button(label, use_container_width=True):
            elapsed = time.time() - (st.session_state.q_start_time or time.time())
            st.session_state.answer_times.append(round(elapsed, 2))
            selected_letter = choice.strip().split(".")[0].strip()
            st.session_state.answers.append(selected_letter)
            st.session_state.q_index += 1
            st.session_state.q_start_time = time.time()
            st.rerun()


# ──────────────────────────────────────────────────────────────────────
#  PAGE 2 · LIVE ANALYSIS
# ──────────────────────────────────────────────────────────────────────
def page_analysis():
    scores = st.session_state.scores
    if not scores:
        scores = compute_scores()
        st.session_state.scores = scores

    progress_steps(2)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section_title("📊", "Live Cognitive Analysis", "Real-time profile generated from your responses")

    glow_divider()

    # Simulated sensor readout header
    st.markdown(f"""
    <div style="background:rgba(4,14,32,0.9);border:1px solid #0d3a6a;border-radius:10px;
                padding:0.8rem 1.4rem;margin-bottom:1.2rem;font-family:'Share Tech Mono',monospace;
                font-size:0.78rem;color:#3a7ab8;display:flex;gap:2rem;">
      <span>● SYSTEM ONLINE</span>
      <span>AVG RESPONSE TIME: <span style="color:#4dc3ff;">{scores.get('avg_time',0)}s</span></span>
      <span>DECISIVENESS INDEX: <span style="color:#4dc3ff;">{scores.get('decisiveness',0)}%</span></span>
      <span>SESSION: <span style="color:#4dc3ff;">COMPLETE</span></span>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    def color_for(label_tuple):
        return label_tuple[1] if isinstance(label_tuple, tuple) else "#4dc3ff"

    stress = scores.get("stress", {})
    attention = scores.get("attention", {})
    emotion = scores.get("emotion", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Score", f"{scores.get('overall', 0)} / 100")
    col2.metric("Stress Level", stress.get("label", ("—",""))[0] if stress else "—",
                delta=f"Score {stress.get('score','?')}/10" if stress else "")
    col3.metric("Attention", attention.get("label", ("—",""))[0] if attention else "—",
                delta=f"Score {attention.get('score','?')}/10" if attention else "")
    col4.metric("Emotional State", emotion.get("label", ("—",""))[0] if emotion else "—",
                delta=f"Score {emotion.get('score','?')}/10" if emotion else "")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Cognitive profile visual — hexagonal radar as SVG
    def radar_svg(scores_dict):
        labels = ["Stress\nResilience", "Attention\nStability", "Emotional\nRegulation",
                  "Decisiveness", "Engagement", "Adaptability"]
        vals = [
            scores_dict.get("stress", {}).get("score", 5) / 10,
            scores_dict.get("attention", {}).get("score", 5) / 10,
            scores_dict.get("emotion", {}).get("score", 5) / 10,
            scores_dict.get("decisiveness", 50) / 100,
            random.uniform(0.55, 0.85),
            random.uniform(0.5, 0.8),
        ]
        cx, cy, r = 180, 180, 130
        n = len(labels)

        def pt(i, frac):
            angle = math.pi / 2 - (2 * math.pi * i / n)
            return cx + frac * r * math.cos(angle), cy - frac * r * math.sin(angle)

        # Grid rings
        grid_paths = ""
        for ring in [0.25, 0.5, 0.75, 1.0]:
            pts = [pt(i, ring) for i in range(n)]
            d = " ".join([f"{'M' if j==0 else 'L'}{p[0]:.1f},{p[1]:.1f}" for j, p in enumerate(pts)]) + " Z"
            grid_paths += f'<path d="{d}" fill="none" stroke="#1a3a6a" stroke-width="1"/>'

        # Axes
        axes = ""
        for i in range(n):
            x2, y2 = pt(i, 1.0)
            axes += f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1a3a6a" stroke-width="1"/>'

        # Data polygon
        data_pts = [pt(i, vals[i]) for i in range(n)]
        data_d = " ".join([f"{'M' if j==0 else 'L'}{p[0]:.1f},{p[1]:.1f}" for j, p in enumerate(data_pts)]) + " Z"
        data_poly = f'<path d="{data_d}" fill="rgba(26,122,212,0.25)" stroke="#4dc3ff" stroke-width="2"/>'

        # Dots
        dots = "".join([f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4" fill="#4dc3ff" stroke="#fff" stroke-width="1.5"/>'
                        for p in data_pts])

        # Labels
        label_els = ""
        for i, lbl in enumerate(labels):
            lx, ly = pt(i, 1.25)
            lines = lbl.split("\n")
            dy_start = -len(lines) * 7
            spans = "".join([f'<tspan x="{lx:.1f}" dy="14">{l}</tspan>' for l in lines])
            label_els += f'<text x="{lx:.1f}" y="{ly + dy_start:.1f}" text-anchor="middle" font-size="10" fill="#7aaad4" font-family="Exo 2,sans-serif">{spans}</text>'

        return f"""
        <svg viewBox="0 0 360 360" xmlns="http://www.w3.org/2000/svg" width="100%" style="max-width:340px;display:block;margin:auto;">
          <rect width="360" height="360" fill="rgba(6,18,40,0.0)"/>
          {grid_paths}{axes}{data_poly}{dots}{label_els}
        </svg>"""

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.5rem;">
            COGNITIVE PROFILE RADAR
          </div>
        """, unsafe_allow_html=True)
        st.markdown(radar_svg(scores), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;height:100%;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
            INDICATOR BREAKDOWN
          </div>
        """, unsafe_allow_html=True)

        indicators = [
            ("Stress Resilience", stress.get("score", 0), stress.get("label", ("—","#888"))),
            ("Attention Stability", attention.get("score", 0), attention.get("label", ("—","#888"))),
            ("Emotional Regulation", emotion.get("score", 0), emotion.get("label", ("—","#888"))),
            ("Decisiveness", scores.get("decisiveness", 0) // 10, ("Index", "#4dc3ff")),
        ]

        for name, score_val, lbl in indicators:
            bar_pct = score_val * 10
            color = lbl[1] if isinstance(lbl, tuple) else "#4dc3ff"
            label_text = lbl[0] if isinstance(lbl, tuple) else str(lbl)
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:0.85rem;color:#a8ccee;">{name}</span>
                <span style="font-size:0.82rem;color:{color};font-family:'Share Tech Mono',monospace;">{label_text}</span>
              </div>
              <div style="background:rgba(10,28,60,0.8);border-radius:4px;height:8px;">
                <div style="width:{bar_pct}%;background:linear-gradient(90deg,{color}88,{color});
                            height:8px;border-radius:4px;transition:width 0.5s;
                            box-shadow:0 0 8px {color}66;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    glow_divider()

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("⟶  Proceed to Adaptive Adjustment", use_container_width=True):
            st.session_state.page = "adjustment"
            st.rerun()


# ──────────────────────────────────────────────────────────────────────
#  PAGE 3 · ADAPTIVE SCENE ADJUSTMENT
# ──────────────────────────────────────────────────────────────────────
def page_adjustment():
    scores = st.session_state.scores
    scene = pick_scene(scores)

    progress_steps(3)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section_title("🔄", "Adaptive Scene Adjustment", "AI selects the optimal environment based on your cognitive profile")

    glow_divider()

    overall = scores.get("overall", 50)

    # Before / After
    col_before, col_arrow, col_after = st.columns([5, 1, 5])

    with col_before:
        st.markdown(f"""
        <div style="background:rgba(40,10,10,0.5);border:1px solid #6a1a1a;border-radius:12px;padding:1.2rem;">
          <div style="color:#ff7043;font-size:0.72rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.6rem;">
            ▲ BASELINE STATE
          </div>
          <div style="font-size:1.8rem;margin-bottom:0.4rem;">🏙️</div>
          <div style="color:#e8c0b0;font-weight:600;margin-bottom:0.3rem;">High-Stress Environment</div>
          <div style="color:#8a5a5a;font-size:0.82rem;line-height:1.5;">
            Noisy, high-pressure scenario with competing demands.<br>
            Stress indicators elevated. Cognitive load at maximum.
          </div>
          <div style="margin-top:0.8rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
            <span style="background:rgba(244,67,54,0.2);color:#f44336;border:1px solid #f44336;
                         border-radius:4px;padding:2px 8px;font-size:0.72rem;">Stress: HIGH</span>
            <span style="background:rgba(255,152,0,0.2);color:#ff9800;border:1px solid #ff9800;
                         border-radius:4px;padding:2px 8px;font-size:0.72rem;">Focus: IMPAIRED</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_arrow:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;height:100%;
                    font-size:2rem;color:#4dc3ff;padding-top:2rem;">⟶</div>
        """, unsafe_allow_html=True)

    with col_after:
        st.markdown(f"""
        <div style="background:rgba(10,30,10,0.5);border:1px solid #1a6a2a;border-radius:12px;padding:1.2rem;
                    box-shadow:0 0 20px rgba(26,170,90,0.15);">
          <div style="color:#00e676;font-size:0.72rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.6rem;">
            ✦ ADAPTED ENVIRONMENT
          </div>
          <div style="font-size:1.8rem;margin-bottom:0.4rem;">{scene['emoji']}</div>
          <div style="color:#b0e8c0;font-weight:600;margin-bottom:0.3rem;">{scene['name']}</div>
          <div style="color:#5a8a6a;font-size:0.82rem;line-height:1.5;">{scene['desc']}</div>
          <div style="margin-top:0.8rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
            <span style="background:rgba(0,230,118,0.2);color:#00e676;border:1px solid #00e676;
                         border-radius:4px;padding:2px 8px;font-size:0.72rem;">Optimised</span>
            <span style="background:rgba(77,195,255,0.2);color:#4dc3ff;border:1px solid #4dc3ff;
                         border-radius:4px;padding:2px 8px;font-size:0.72rem;">AI-Selected</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # Adjustment parameters
    st.markdown("""
    <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
      SCENE PARAMETERS · ADAPTIVE CALIBRATION
    </div>
    """, unsafe_allow_html=True)

    params = {
        "Noise Level": max(5, 100 - overall),
        "Social Density": max(10, 80 - overall),
        "Pacing Speed": max(20, overall + 10),
        "Visual Complexity": max(10, 70 - overall),
    }

    cols = st.columns(len(params))
    for col, (param, val) in zip(cols, params.items()):
        with col:
            color = "#00e676" if val < 40 else ("#ffb300" if val < 70 else "#ff7043")
            st.markdown(f"""
            <div style="background:rgba(8,22,48,0.8);border:1px solid #1a3a6a;border-radius:10px;
                        padding:0.8rem;text-align:center;">
              <div style="font-size:0.72rem;color:#5a8ab8;margin-bottom:0.4rem;">{param}</div>
              <div style="font-size:1.4rem;font-family:'Share Tech Mono',monospace;color:{color};">{val}%</div>
              <div style="background:rgba(10,25,55,0.8);border-radius:3px;height:4px;margin-top:0.5rem;">
                <div style="width:{val}%;background:{color};height:4px;border-radius:3px;
                            box-shadow:0 0 6px {color}88;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    glow_divider()

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("📋  View Full Session Report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()


# ──────────────────────────────────────────────────────────────────────
#  PAGE 4 · SESSION REPORT
# ──────────────────────────────────────────────────────────────────────
def page_report():
    scores = st.session_state.scores
    answers = st.session_state.answers
    times = st.session_state.answer_times

    progress_steps(4)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section_title("📋", "Session Report", "Comprehensive AI-generated cognitive & emotional assessment")

    overall = scores.get("overall", 50)

    # Overall score banner
    risk_label, risk_color = (
        ("Low", "#00e676") if overall >= 70 else
        ("Moderate", "#ffb300") if overall >= 40 else
        ("High", "#ff7043")
    )

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(6,18,44,0.95),rgba(10,30,70,0.9));
                border:1px solid #2a6aba;border-radius:14px;padding:1.5rem 2rem;margin-bottom:1.2rem;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 0 30px rgba(26,122,212,0.25);">
      <div>
        <div style="color:#7aaad4;font-size:0.78rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;">
          OVERALL COGNITIVE SCORE
        </div>
        <div style="font-size:3.5rem;font-weight:800;color:#4dc3ff;font-family:'Share Tech Mono',monospace;
                    line-height:1;margin-top:0.2rem;">
          {overall}<span style="font-size:1.5rem;color:#3a7ab8;">/100</span>
        </div>
      </div>
      <div style="text-align:right;">
        <div style="color:#7aaad4;font-size:0.78rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;">
          RISK LEVEL
        </div>
        <div style="font-size:1.6rem;font-weight:700;color:{risk_color};margin-top:0.2rem;">
          {risk_label}
        </div>
        <div style="color:#5a8ab8;font-size:0.8rem;margin-top:0.2rem;">
          Avg Response: {scores.get('avg_time', 0)}s
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Key Indicators
    col_l, col_r = st.columns(2)

    stress = scores.get("stress", {})
    attention = scores.get("attention", {})
    emotion = scores.get("emotion", {})

    with col_l:
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
            KEY INDICATORS
          </div>
        """, unsafe_allow_html=True)

        for name, data, icon in [
            ("Stress Level", stress, "🔴"),
            ("Attention Stability", attention, "🟡"),
            ("Emotional State", emotion, "🟢"),
        ]:
            label = data.get("label", ("—","#888"))
            ltext, lcolor = (label[0], label[1]) if isinstance(label, tuple) else (str(label), "#888")
            s_val = data.get("score", 0)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.5rem 0;border-bottom:1px solid #0d2a4a;">
              <div style="display:flex;align-items:center;gap:0.5rem;">
                <span>{icon}</span>
                <span style="color:#a8ccee;font-size:0.88rem;">{name}</span>
              </div>
              <span style="color:{lcolor};font-family:'Share Tech Mono',monospace;font-size:0.85rem;font-weight:600;">
                {ltext} ({s_val}/10)
              </span>
            </div>
            """, unsafe_allow_html=True)

        dec = scores.get("decisiveness", 0)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;">
          <div style="display:flex;align-items:center;gap:0.5rem;">
            <span>⚡</span>
            <span style="color:#a8ccee;font-size:0.88rem;">Engagement</span>
          </div>
          <span style="color:#4dc3ff;font-family:'Share Tech Mono',monospace;font-size:0.85rem;font-weight:600;">
            {"High" if dec>=70 else "Medium" if dec>=40 else "Low"} ({dec}%)
          </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        # Response timeline
        st.markdown("""
        <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.2rem;">
          <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:1rem;">
            RESPONSE TIMELINE
          </div>
        """, unsafe_allow_html=True)

        for i, (q, ans, t) in enumerate(zip(QUESTIONS, answers, times)):
            opt_text = next((o[1] for o in q["options"] if o[0] == ans), ans)
            opt_label = next((o[3] for o in q["options"] if o[0] == ans), "")
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;padding:0.6rem;background:rgba(10,28,60,0.6);
                        border-radius:8px;border-left:3px solid #1a7ad4;">
              <div style="display:flex;justify-content:space-between;margin-bottom:0.2rem;">
                <span style="font-size:0.72rem;color:#3a7ab8;font-family:'Share Tech Mono',monospace;">
                  Q{i+1} · {q['scene_label'].split('·')[1].strip()}
                </span>
                <span style="font-size:0.72rem;color:#3a7ab8;font-family:'Share Tech Mono',monospace;">{t}s</span>
              </div>
              <div style="color:#a8ccee;font-size:0.82rem;">
                <strong style="color:#e8f4ff;">{ans}.</strong> {opt_text[:50]}{'...' if len(opt_text)>50 else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    glow_divider()

    # AI Recommendation
    def gen_recommendation(scores):
        s = scores.get("stress", {}).get("score", 5)
        a = scores.get("attention", {}).get("score", 5)
        e = scores.get("emotion", {}).get("score", 5)
        recs = []
        if s < 5:
            recs.append("**Stress Management**: Consider mindfulness-based stress reduction (MBSR) techniques. Daily breathing exercises (4-7-8 pattern) can significantly lower baseline cortisol.")
        if a < 5:
            recs.append("**Attention Training**: Structured focus sessions using the Pomodoro technique (25-min blocks) can rebuild attention spans. Limit multitasking environments.")
        if e < 5:
            recs.append("**Emotional Regulation**: Cognitive reframing exercises and journalling can improve emotional stability. Social skills practice in low-pressure settings is recommended.")
        if not recs:
            recs.append("**Maintain & Enhance**: Your cognitive profile is strong. Continue with current routines. Consider advanced resilience training to push your limits further.")
        return recs

    st.markdown("""
    <div style="background:rgba(6,18,44,0.9);border:1px solid #1a4a8a;border-radius:12px;padding:1.4rem;margin-bottom:1rem;">
      <div style="color:#4dc3ff;font-size:0.75rem;letter-spacing:0.1em;font-family:'Share Tech Mono',monospace;margin-bottom:0.8rem;">
        ✦ AI RECOMMENDATION
      </div>
    """, unsafe_allow_html=True)

    for rec in gen_recommendation(scores):
        st.markdown(f"""
      <div style="background:rgba(13,50,100,0.4);border-left:3px solid #2a8ae8;
                  border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-bottom:0.6rem;">
        <p style="color:#a8ccee;font-size:0.88rem;line-height:1.6;margin:0;">{rec}</p>
      </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔁  Retake Assessment", use_container_width=True):
            for key in ["q_index", "answers", "answer_times", "q_start_time", "scores"]:
                del st.session_state[key]
            st.session_state.page = "home"
            init_state()
            st.rerun()
    with col_b:
        report_text = f"""MINDSIGHT AI · SESSION REPORT
==============================
Overall Score : {scores.get('overall', 0)}/100
Risk Level    : {risk_label}

INDICATORS
Stress        : {scores.get('stress',{}).get('label',('?',))[0]} ({scores.get('stress',{}).get('score','?')}/10)
Attention     : {scores.get('attention',{}).get('label',('?',))[0]} ({scores.get('attention',{}).get('score','?')}/10)
Emotion       : {scores.get('emotion',{}).get('label',('?',))[0]} ({scores.get('emotion',{}).get('score','?')}/10)
Decisiveness  : {scores.get('decisiveness','?')}%

RESPONSES
""" + "\n".join([f"Q{i+1}: {a} ({t}s)" for i,(a,t) in enumerate(zip(answers, times))])
        st.download_button("⬇  Export Report", report_text, "mindsight_report.txt",
                           "text/plain", use_container_width=True)
    with col_c:
        if st.button("🏠  Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    glow_divider()
    st.markdown("""
    <p style="text-align:center;color:#2a5a7a;font-size:0.75rem;letter-spacing:0.06em;">
      ⚠️ This report is generated for educational purposes only and does not constitute a clinical diagnosis.
      Please consult a licensed mental health professional for formal assessment.
    </p>
    """, unsafe_allow_html=True)


# ─────────────────────────── Router ──────────────────────────────────
page = st.session_state.get("page", "home")

if page == "home":
    page_home()
elif page == "assessment":
    page_assessment()
elif page == "analysis":
    page_analysis()
elif page == "adjustment":
    page_adjustment()
elif page == "report":
    page_report()
else:
    page_home()
