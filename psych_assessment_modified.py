import streamlit as st
import base64
import json
import time
import random
from datetime import datetime

# ==========================================
# 1. 页面配置与全局样式
# ==========================================
st.set_page_config(
    page_title="Psychological Environment Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 读取背景图并转为base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

bg_base64 = get_base64_image("background.png")

# 全局CSS：文本框全透明 + 背景图设置
st.markdown(f"""
<style>
    /* 全局背景 */
    .stApp {{
        background: radial-gradient(circle at center, 
            rgba(255,255,255,0.1) 0%, 
            rgba(0,0,0,0.3) 100%),
            url("data:image/png;base64,{bg_base64}") no-repeat center center fixed;
        background-size: cover;
    }}
    
    /* 所有文本输入框、文本区域透明 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background-color: transparent !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        backdrop-filter: blur(2px);
    }}
    
    /* 按钮半透明 */
    .stButton > button {{
        background-color: rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        backdrop-filter: blur(3px);
    }}
    .stButton > button:hover {{
        background-color: rgba(255,255,255,0.3) !important;
    }}
    
    /* 滑块、选择框等组件透明化 */
    .stSlider > div > div > div > div {{
        background-color: rgba(255,255,255,0.2) !important;
    }}
    
    /* 标题和正文颜色适配深色背景 */
    h1, h2, h3, h4, p, label, .stMarkdown {{
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    
    /* 隐藏默认streamlit头部和菜单 */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 数据与配置（已按要求重排）
# ==========================================

# 图片路径映射（按新顺序）
SCENE_IMG_Q1 = "image 2.png"      # Video Call → 第1题背景
SCENE_IMG_Q2 = "image 3.png"      # Proposal → 第2题背景
SCENE_IMG_Q3 = "background.png"   # Puzzle → 第3题背景
ADJUSTED_IMG = "wide_cozy_sunlit_interior_scene_viewed_in_a_vr_ro.png"

# 问题配置（顺序已调整）
QUESTIONS = [
    {
        "id": "q1_video_call",
        "scenario": "Video Call",
        "description": "You are in an important video call meeting. The environment feels tense and uncomfortable.",
        "image": SCENE_IMG_Q1,
        "type": "likert",
        "prompt": "How stressful does this environment feel to you right now?"
    },
    {
        "id": "q2_proposal",
        "scenario": "Spent Days Preparing a Proposal",
        "description": "You have spent days preparing a critical proposal. The workspace feels cluttered and overwhelming.",
        "image": SCENE_IMG_Q2,
        "type": "likert",
        "prompt": "How much pressure does this environment add to your current task?"
    },
    {
        "id": "q3_puzzle",
        "scenario": "Puzzle",
        "description": "You are trying to solve a complex puzzle in this space. The surroundings feel distracting.",
        "image": SCENE_IMG_Q3,
        "type": "likert",
        "prompt": "How difficult is it to concentrate in this environment?"
    }
]

# 治愈鸡汤库（用于Adjustment页面）
HEALING_QUOTES = [
    "Your peace is more important than perfection. Breathe deeply.",
    "This moment is temporary. You have overcome harder things before.",
    "Rest is not laziness. It is necessary maintenance for your brilliant mind.",
    "You are allowed to take up space. You are allowed to be gentle with yourself.",
    "The world can wait. Your well-being cannot."
]

# 压力缓解指标
RELIEF_METRICS = [
    {"label": "Cortisol Level Reduction", "value": "-32%", "icon": "📉"},
    {"label": "Heart Rate Variability Improvement", "value": "+28%", "icon": "💚"},
    {"label": "Subjective Calmness Score", "value": "8.4/10", "icon": "🧘"},
    {"label": "Cognitive Load Decrease", "value": "-41%", "icon": "🧠"}
]


# ==========================================
# 3. Session State 初始化
# ==========================================
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "adjustment_complete" not in st.session_state:
    st.session_state.adjustment_complete = False
if "pre_stress_scores" not in st.session_state:
    st.session_state.pre_stress_scores = []


# ==========================================
# 4. 页面渲染函数
# ==========================================

def render_intro():
    st.markdown("# 🧠 Psychological Environment Assessment")
    st.markdown("""
    Welcome to our adaptive environmental psychology study.  
    This assessment will guide you through **3 scenario-based questions**, 
    followed by an **adaptive environment adjustment** experience, 
    and conclude with a **personalized relief report**.
    
    ⏱️ Estimated time: 8-10 minutes  
    🔒 All responses are anonymous and confidential.
    """)
    if st.button("Begin Assessment", type="primary"):
        st.session_state.page = "assessment"
        st.rerun()


def render_assessment():
    q_idx = st.session_state.current_q
    if q_idx >= len(QUESTIONS):
        st.session_state.page = "adjustment"
        st.rerun()
        return

    q = QUESTIONS[q_idx]
    
    # 显示当前题目对应的背景图
    img_b64 = get_base64_image(q["image"])
    if img_b64:
        st.markdown(f"""
        <div style="
            width:100%; 
            height:350px; 
            background: url('data:image/png;base64,{img_b64}') no-repeat center center;
            background-size: cover;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        "></div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### Question {q_idx+1}/3: {q['scenario']}")
    st.markdown(f"*{q['description']}*")
    st.markdown(f"**{q['prompt']}**")
    
    score = st.slider(
        "Stress / Difficulty Level",
        min_value=1, max_value=10, value=5,
        key=f"slider_{q['id']}",
        help="1 = Not at all, 10 = Extremely"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Next →", type="primary"):
            st.session_state.responses[q["id"]] = score
            st.session_state.pre_stress_scores.append(score)
            st.session_state.current_q += 1
            st.rerun()


def render_adjustment():
    """Adjustment页面：仅保留治愈鸡汤 + 指标，背景为adjusted图片"""
    adj_b64 = get_base64_image(ADJUSTED_IMG)
    
    # 全屏背景覆盖
    if adj_b64:
        st.markdown(f"""
        <style>
            .stApp {{
                background: url("data:image/png;base64,{adj_b64}") no-repeat center center fixed !important;
                background-size: cover !important;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🌿 Adaptive Environment Adjustment")
    st.markdown("*Take a moment to breathe. Your environment is adapting to support you.*")
    
    # 治愈鸡汤（随机选取2条）
    selected_quotes = random.sample(HEALING_QUOTES, 2)
    for quote in selected_quotes:
        st.markdown(f"""
        <div style="
            padding: 20px 30px;
            margin: 15px 0;
            border-left: 3px solid rgba(255,255,255,0.6);
            font-style: italic;
            font-size: 1.2rem;
            background: rgba(0,0,0,0.15);
            backdrop-filter: blur(4px);
            border-radius: 0 8px 8px 0;
        ">
            "{quote}"
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Real-time Physiological Adaptation Metrics")
    
    cols = st.columns(len(RELIEF_METRICS))
    for i, metric in enumerate(RELIEF_METRICS):
        with cols[i]:
            st.markdown(f"""
            <div style="
                text-align:center; 
                padding:20px 10px;
                background: rgba(0,0,0,0.15);
                backdrop-filter: blur(4px);
                border-radius: 10px;
                margin: 5px 0;
            ">
                <div style="font-size:2rem;">{metric['icon']}</div>
                <div style="font-size:1.5rem; font-weight:bold; margin:8px 0;">{metric['value']}</div>
                <div style="font-size:0.85rem; opacity:0.9;">{metric['label']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("")
    if st.button("Continue to Report →", type="primary"):
        st.session_state.adjustment_complete = True
        st.session_state.page = "report"
        st.rerun()


def render_report():
    st.markdown("# 📋 Personalized Assessment & Relief Report")
    st.markdown(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # === 新增：压力缓解报告 ===
    avg_pre = sum(st.session_state.pre_stress_scores) / len(st.session_state.pre_stress_scores) if st.session_state.pre_stress_scores else 5
    relief_percentage = round((avg_pre - 3.2) / avg_pre * 100, 1)  # 模拟缓解后基准3.2
    
    st.markdown("## 🌱 Post-Adjustment Stress Relief Summary")
    st.markdown(f"""
    After experiencing the adaptive environment adjustment, your physiological and psychological indicators 
    show significant improvement:
    
    - **Average Pre-Assessment Stress Level**: {avg_pre:.1f}/10
    - **Estimated Post-Adjustment Stress Level**: 3.2/10
    - **Overall Stress Relief**: **{relief_percentage}% reduction**
    - **Primary Relief Factors**: Environmental coherence restoration, biophilic visual cues activation, 
      cognitive load redistribution through spatial adaptation.
    
    > 💡 *The adaptive environment successfully reduced your acute stress response by modulating 
    > visual complexity, color temperature, and spatial openness parameters in real-time.*
    """)
    
    st.markdown("---")
    
    # === 保留原有部分：压力水平分析 ===
    st.markdown("## 📈 Original Stress Level Analysis")
    for q in QUESTIONS:
        score = st.session_state.responses.get(q["id"], "N/A")
        bar_color = "#ff6b6b" if isinstance(score, int) and score >= 7 else "#ffd93d" if isinstance(score, int) and score >= 4 else "#6bcb77"
        st.markdown(f"""
        **{q['scenario']}**: {score}/10  
        <div style="width:100%; background:rgba(255,255,255,0.1); border-radius:4px; height:12px; margin:5px 0 15px 0;">
            <div style="width:{score*10 if isinstance(score,int) else 0}%; background:{bar_color}; height:100%; border-radius:4px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # === 保留原有部分：心理分析 ===
    st.markdown("## 🔍 Psychological Profile Insights")
    high_stress_count = sum(1 for s in st.session_state.pre_stress_scores if s >= 7)
    if high_stress_count >= 2:
        st.markdown("""
        **High Environmental Sensitivity Detected**  
        You show strong reactivity to environmental stressors. Consider incorporating regular 
        micro-restoration breaks and personalized environmental controls into your daily routine.
        """)
    elif high_stress_count == 1:
        st.markdown("""
        **Moderate Environmental Sensitivity**  
        You are selectively sensitive to specific environmental triggers. Identifying and modifying 
        those specific factors can yield significant well-being improvements.
        """)
    else:
        st.markdown("""
        **Low Environmental Sensitivity / High Resilience**  
        You demonstrate strong environmental adaptability. Maintain your current coping strategies 
        and consider sharing your resilience practices with others.
        """)
    
    st.markdown("---")
    st.markdown("*Thank you for participating. This report is for informational purposes only and does not constitute clinical diagnosis.*")
    
    if st.button("Restart Assessment"):
        for key in ["page", "current_q", "responses", "adjustment_complete", "pre_stress_scores"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ==========================================
# 5. 主路由
# ==========================================
page_router = {
    "intro": render_intro,
    "assessment": render_assessment,
    "adjustment": render_adjustment,
    "report": render_report
}

current_page = st.session_state.get("page", "intro")
page_router[current_page]()
