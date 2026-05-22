# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
import datetime
from typing import Dict, Any, List, Optional
from korean_lunar_calendar import KoreanLunarCalendar
import plotly.graph_objects as go

def get_solar_date(input_date: datetime.date, calendar_type: str) -> datetime.date:
    if calendar_type == "양력":
        return input_date
    calendar = KoreanLunarCalendar()
    is_intercalation = (calendar_type == "음력(윤달)")
    if calendar.setLunarDate(input_date.year, input_date.month, input_date.day, is_intercalation):
        return datetime.date(calendar.solarYear, calendar.solarMonth, calendar.solarDay)
    return input_date

TIME_BRANCHES = [
    "🐭 자(子)시 (23:30 ~ 01:29)",
    "🐮 축(丑)시 (01:30 ~ 03:29)",
    "🐯 인(寅)시 (03:30 ~ 05:29)",
    "🐰 묘(卯)시 (05:30 ~ 07:29)",
    "🐲 진(辰)시 (07:30 ~ 09:29)",
    "🐍 사(巳)시 (09:30 ~ 11:29)",
    "🐴 오(午)시 (11:30 ~ 13:29)",
    "🐑 미(未)시 (13:30 ~ 15:29)",
    "🐵 신(申)시 (15:30 ~ 17:29)",
    "🐔 유(酉)시 (17:30 ~ 19:29)",
    "🐶 술(戌)시 (19:30 ~ 21:29)",
    "🐷 해(亥)시 (21:30 ~ 23:29)"
]

def get_hour_min_from_branch(branch_str: str) -> tuple:
    if not branch_str: return (None, 0)
    idx = TIME_BRANCHES.index(branch_str) if branch_str in TIME_BRANCHES else 0
    return (idx * 2, 0)

def get_branch_from_time_str(time_str: str) -> str:
    if not time_str: return TIME_BRANCHES[0]
    if time_str in TIME_BRANCHES: return time_str
    try:
        h, m = map(int, time_str.split(':'))
        total_m = h * 60 + m
        if total_m >= 23*60+30 or total_m < 1*60+30:
            return TIME_BRANCHES[0]
        for i in range(1, 12):
            if (2*i - 1)*60 + 30 <= total_m < (2*i + 1)*60 + 30:
                return TIME_BRANCHES[i]
        return TIME_BRANCHES[0]
    except:
        return TIME_BRANCHES[0]

@st.cache_data(ttl=600)
def get_best_match_record(friends_db_str: str) -> tuple:
    friends_db = json.loads(friends_db_str)
    if not friends_db or len(friends_db) < 2: return None
    males = [f for f in friends_db if f.get('성별') == '남자']
    females = [f for f in friends_db if f.get('성별') == '여자']
    if not males or not females: return None
    
    best_score = -1
    best_couple = None
    
    male_sajus = {}
    for m in males:
        try:
            m_solar = get_solar_date(datetime.datetime.strptime(m['birth_date'], "%Y-%m-%d").date(), m.get('calendar', '양력'))
            m_h, m_m = None, 0
            if m.get('birth_time'):
                if ":" in m['birth_time']: m_h, m_m = map(int, m['birth_time'].split(':'))
                else: m_h, m_m = get_hour_min_from_branch(m['birth_time'])
            male_sajus[m['이름']] = saju_engine.analyze_saju(m_solar.year, m_solar.month, m_solar.day, m_h, m_m)
        except: pass

    female_sajus = {}
    for f in females:
        try:
            f_solar = get_solar_date(datetime.datetime.strptime(f['birth_date'], "%Y-%m-%d").date(), f.get('calendar', '양력'))
            f_h, f_m = None, 0
            if f.get('birth_time'):
                if ":" in f['birth_time']: f_h, f_m = map(int, f['birth_time'].split(':'))
                else: f_h, f_m = get_hour_min_from_branch(f['birth_time'])
            female_sajus[f['이름']] = saju_engine.analyze_saju(f_solar.year, f_solar.month, f_solar.day, f_h, f_m)
        except: pass

    for m_name, m_saju in male_sajus.items():
        for f_name, f_saju in female_sajus.items():
            comp = saju_engine.get_compatibility(m_saju, f_saju)
            if comp['total_score'] > best_score:
                best_score = comp['total_score']
                best_couple = (m_name, f_name, best_score)
                
    return best_couple

# Set page config first
st.set_page_config(
    page_title="🔮 재미로 보는 사주 궁합 매칭",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import saju_engine

# Database File Path
DB_PATH = 'friends_db.json'
USER_DB_PATH = 'users_db.json'

def load_friends_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"친구 데이터베이스 로드 중 오류가 발생했습니다: {e}")
        return []

def save_friends_db(db: List[Dict[str, Any]]):
    try:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"친구 데이터베이스 저장 중 오류가 발생했습니다: {e}")

def load_users_db() -> List[Dict[str, Any]]:
    if not os.path.exists(USER_DB_PATH):
        return []
    try:
        with open(USER_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"사용자 데이터베이스 로드 중 오류가 발생했습니다: {e}")
        return []

def save_users_db(db: List[Dict[str, Any]]):
    try:
        with open(USER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"사용자 데이터베이스 저장 중 오류가 발생했습니다: {e}")

# Inject Custom CSS for Premium Mystical Look
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    /* Apply Fonts & Colors to App */
    .stApp {
        background-color: #0b0512;
        background-image: radial-gradient(circle at 10% 20%, rgba(123, 31, 162, 0.15) 0%, transparent 50%),
                          radial-gradient(circle at 90% 80%, rgba(74, 20, 140, 0.15) 0%, transparent 50%);
        color: #e2d7ec;
        font-family: 'Noto Sans KR', 'Outfit', sans-serif !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #12091d !important;
        border-right: 1px solid rgba(186, 104, 200, 0.15) !important;
    }
    
    /* Headers Custom styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Noto Sans KR', 'Outfit', sans-serif !important;
        background: linear-gradient(120deg, #f3e5f5, #ce93d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Subheader custom tint */
    .stSubheader {
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    /* Glassmorphic card design */
    .mystic-card {
        background: rgba(30, 15, 52, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(186, 104, 200, 0.18);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .mystic-card:hover {
        transform: translateY(-3px);
        border-color: rgba(186, 104, 200, 0.4);
        box-shadow: 0 12px 40px 0 rgba(123, 31, 162, 0.25);
    }
    
    /* Score Indicator Style */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7b1fa2, #ba68c8);
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        box-shadow: 0 3px 10px rgba(123, 31, 162, 0.3);
    }
    
    /* Result Grade Highlight */
    .grade-text {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffeb3b !important;
        text-shadow: 0 0 10px rgba(253, 216, 53, 0.4);
        margin: 5px 0;
    }
    
    /* Custom style for buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #6a1b9a, #4a148c) !important;
        color: #ffffff !important;
        border: 1px solid rgba(186, 104, 200, 0.4) !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        padding: 10px 30px !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 15px rgba(123, 31, 162, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
        margin-top: 15px;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #7b1fa2, #5e35b1) !important;
        box-shadow: 0 6px 22px rgba(142, 36, 170, 0.5) !important;
        transform: translateY(-1px);
        border-color: rgba(225, 190, 231, 0.6) !important;
    }
    
    /* Element Color Badges */
    .badge-wood { background-color: #E8F5E9; color: #2E7D32; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
    .badge-fire { background-color: #FFEBEE; color: #C62828; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
    .badge-earth { background-color: #FFFDE7; color: #F57F17; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
    .badge-metal { background-color: #FAFAFA; color: #424242; border-radius: 4px; padding: 2px 6px; font-weight: bold; }
    .badge-water { background-color: #E1F5FE; color: #0277BD; border-radius: 4px; padding: 2px 6px; font-weight: bold; }

    /* Info & Tips Box */
    .mystic-info {
        background: rgba(123, 31, 162, 0.08);
        border-left: 4px solid #ba68c8;
        padding: 15px;
        border-radius: 4px 12px 12px 4px;
        margin-bottom: 20px;
    }
    
    /* Custom Table Style */
    .friends-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        color: #e2d7ec;
    }
    .friends-table th {
        background: rgba(123, 31, 162, 0.25);
        border-bottom: 2px solid rgba(186, 104, 200, 0.3);
        padding: 12px;
        text-align: left;
        font-weight: 700;
    }
    .friends-table td {
        padding: 12px;
        border-bottom: 1px solid rgba(186, 104, 200, 0.1);
        background: rgba(255, 255, 255, 0.02);
    }
    .friends-table tr:hover td {
        background: rgba(186, 104, 200, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to generate pillar card
def get_pillar_card_html(title: str, pillar_data: Optional[Dict[str, Any]]) -> str:
    if not pillar_data:
        return f"""
        <div style="
            background: rgba(255, 255, 255, 0.02);
            border: 1px dashed rgba(186, 104, 200, 0.2);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            min-height: 185px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.4); font-weight: 600; margin-bottom: 10px;">{title}</div>
            <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.3); font-weight: 700;">모름</div>
            <div style="font-size: 0.65rem; color: rgba(255, 255, 255, 0.25); margin-top: 5px;">시주 제외 분석</div>
        </div>
        """
    s_el = pillar_data['stem_element']
    b_el = pillar_data['branch_element']
    
    s_color = saju_engine.ELEMENT_COLORS.get(s_el, {'bg': '#FAFAFA', 'text': '#424242'})
    b_color = saju_engine.ELEMENT_COLORS.get(b_el, {'bg': '#FAFAFA', 'text': '#424242'})
    
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(186, 104, 200, 0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        min-height: 185px;
        transition: border-color 0.3s;
    ">
        <div style="font-size: 0.8rem; color: #ce93d8; font-weight: 600; margin-bottom: 8px;">{title}</div>
        <!-- Stem -->
        <div style="
            background: {s_color['bg']};
            color: {s_color['text']};
            border-radius: 6px;
            padding: 8px 0;
            margin-bottom: 6px;
            font-weight: 900;
            font-size: 1.35rem;
            line-height: 1.2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        ">
            {pillar_data['stem_hanja']}<span style="font-size: 0.85rem; font-weight: 500;">({pillar_data['stem_kr']})</span>
        </div>
        <!-- Branch -->
        <div style="
            background: {b_color['bg']};
            color: {b_color['text']};
            border-radius: 6px;
            padding: 8px 0;
            font-weight: 900;
            font-size: 1.35rem;
            line-height: 1.2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        ">
            {pillar_data['branch_hanja']}<span style="font-size: 0.85rem; font-weight: 500;">({pillar_data['branch_kr']})</span>
        </div>
        <div style="font-size: 0.72rem; color: rgba(255, 255, 255, 0.6); margin-top: 8px; font-weight: 500;">
            {pillar_data['branch_animal']}띠 · {b_el}({saju_engine.BRANCHES_INFO[pillar_data['branch_hanja']]['yinyang']})
        </div>
    </div>
    """

# Helper to create customized HTML progress bar for elements
def make_element_bar_html(el: str, count: int, pct: float) -> str:
    color_info = saju_engine.ELEMENT_COLORS.get(el, {'bg': '#ccc', 'text': '#333'})
    
    # Map element to raw bar colors
    bar_colors = {
        '목': '#4CAF50', # green
        '화': '#E53935', # red
        '토': '#FFB300', # yellow/amber
        '금': '#B0BEC5', # silver/grey
        '수': '#1E88E5'  # blue
    }
    bar_color = bar_colors.get(el, '#7e57c2')
    
    return f"""
    <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px; font-weight: 600;">
            <span style="color: {color_info['text']}; background: {color_info['bg']}; padding: 2px 8px; border-radius: 4px;">{el}({count}개)</span>
            <span style="color: #ce93d8;">{pct}%</span>
        </div>
        <div style="background: rgba(255, 255, 255, 0.08); border-radius: 8px; height: 10px; overflow: hidden; border: 1px solid rgba(186, 104, 200, 0.15);">
            <div style="background: {bar_color}; width: {pct}%; height: 100%; border-radius: 8px;"></div>
        </div>
    </div>
    """

# Radar Chart Function
def render_radar_chart(element_power_pct):
    categories = ['목(木)', '화(火)', '토(土)', '금(金)', '수(水)']
    values = [
        element_power_pct.get('목', 0),
        element_power_pct.get('화', 0),
        element_power_pct.get('토', 0),
        element_power_pct.get('금', 0),
        element_power_pct.get('수', 0)
    ]
    
    categories = categories + [categories[0]]
    values = values + [values[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(186, 104, 200, 0.4)',
        line=dict(color='#ba68c8', width=2),
        name='오행 파워 스코어'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 10] if max(values) > 0 else [0, 100],
                gridcolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='#ffffff')
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.2)',
                tickfont=dict(color='#ffeb3b', size=14, weight='bold')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=30, b=30),
        height=320
    )
    return fig

# Helper for element color badge text
def get_badge_html(el: str) -> str:
    cls_map = {'목': 'badge-wood', '화': 'badge-fire', '토': 'badge-earth', '금': 'badge-metal', '수': 'badge-water'}
    cls = cls_map.get(el, '')
    return f'<span class="{cls}">{el}</span>'

# Common function to render user saju analysis UI
def render_saju_analysis(user_saju, u_name):
    u_cols = st.columns(4)
    u_pillars_order = [
        ("시주 (Hour)", user_saju['pillars']['hour']),
        ("일주 (Day)", user_saju['pillars']['day']),
        ("월주 (Month)", user_saju['pillars']['month']),
        ("연주 (Year)", user_saju['pillars']['year'])
    ]
    
    for idx, (title, p_data) in enumerate(u_pillars_order):
        with u_cols[idx]:
            st.markdown(get_pillar_card_html(title, p_data), unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    col_u_left, col_u_right = st.columns([2, 3])
    with col_u_left:
        st.markdown("<div style='font-size: 1rem; font-weight: 700; color:#ce93d8; margin-bottom: 5px;'>📊 오행 파워 다이어그램 (전문가 가중치 반영)</div>", unsafe_allow_html=True)
        power_pcts = user_saju.get('element_power_percentages', {})
        if power_pcts:
            fig = render_radar_chart(power_pcts)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        st.markdown("<div style='font-size: 0.9rem; font-weight: 700; color:#ce93d8; margin-bottom: 5px; margin-top: 5px;'>📊 단순 글자 수 분포</div>", unsafe_allow_html=True)
        for el, count in user_saju['element_counts'].items():
            pct = user_saju['element_percentages'][el]
            st.markdown(make_element_bar_html(el, count, pct), unsafe_allow_html=True)
            
    with col_u_right:
        st.markdown("<div style='font-size: 1rem; font-weight: 700; color:#ce93d8; margin-bottom: 10px;'>사주 특징 요약</div>", unsafe_allow_html=True)
        
        lack_badges = ", ".join([get_badge_html(x) for x in user_saju['lacking_elements']])
        dom_badges = ", ".join([get_badge_html(x) for x in user_saju['dominant_elements']])
        
        st.markdown(f"""
        <div class="mystic-card" style="padding: 18px; margin-bottom: 0;">
            <p>👤 <b>일간 본성:</b> <b>{user_saju['day_stem_kr']}화({user_saju['day_stem']})</b> - {saju_engine.STEMS_INFO[user_saju['day_stem']]['desc']}</p>
            <p>❄️ <b>사주 온도(조후):</b> {user_saju['temp_kr']}</p>
            <p>📈 <b>강한 기운 (과다오행):</b> {dom_badges}</p>
            <p>📉 <b>부족한 기운 (결핍오행):</b> {lack_badges}</p>
        </div>
        """, unsafe_allow_html=True)
        
    luck = user_saju.get('luck_texts', {})
    if luck:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 1rem; font-weight: 700; color:#ce93d8; margin-bottom: 10px;'>🌟 일간(태어난 날)으로 보는 5가지 운세</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(186, 104, 200, 0.2);">
            <p style="margin-bottom: 8px;">🎭 <b>성향:</b> {luck.get('성향', '')}</p>
            <p style="margin-bottom: 8px;">💘 <b>연애/결혼:</b> {luck.get('연애운', '')}</p>
            <p style="margin-bottom: 8px;">💰 <b>재물/금전:</b> {luck.get('재물운', '')}</p>
            <p style="margin-bottom: 8px;">💼 <b>직업/적성:</b> {luck.get('직업운', '')}</p>
            <p style="margin-bottom: 0;">🌿 <b>건강/주의:</b> {luck.get('건강운', '')}</p>
        </div>
        """, unsafe_allow_html=True)

# Sidebar Setup
with st.sidebar:
    # Display the mystical crystal ball image we generated
    if os.path.exists("crystal_ball.png"):
        st.image("crystal_ball.png", use_container_width=True)
    else:
        st.markdown("<div style='font-size: 4rem; text-align: center;'>🔮</div>", unsafe_allow_html=True)
        
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>🔮 솔로 사주 궁합</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; font-size: 0.85rem; color: #b39ddb; margin-bottom: 20px;'>
    전통 사주명리학(오행의 균형, 조후, 천간합, 지지합)을 기반으로 나에게 가장 잘 어울리는 짝을 찾아드립니다.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Quick Saju Fact in sidebar
    st.markdown("""
    <div class='mystic-info' style='font-size: 0.82rem;'>
    💡 <b>사주 팁:</b><br/>
    사주에서 <b>일간(日干)</b>은 내 성격과 태도를 나타내고, <b>일지(日支)</b>는 나의 내면과 배우자 자리를 의미합니다. 서로 결핍된 오행을 채워줄 때 최고의 속궁합이 발현됩니다!
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("#### 🔒 제작자 관리 모드")
    dev_passcode = st.text_input("인증번호 입력", type="password", help="제작자만 사용하는 관리용 인증번호입니다.")
    is_maker = (dev_passcode == "9180")

# Main Title and Page Layout
st.markdown("<h1>🔮 재미로 보는 솔로 사주 궁합 매칭</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #b39ddb; margin-top: -10px;'>내 생년월일과 친구들 데이터베이스를 바탕으로, 나에게 부족함을 채워주는 찰떡 인연을 매칭해 드려요!</p>", unsafe_allow_html=True)

# Load database
friends_db = load_friends_db()

# Navigation Tabs based on Maker Mode
if is_maker:
    tab_match_solo, tab_match_couple, tab_friends, tab_guide = st.tabs(["💘 솔로 궁합 매치", "💞 커플 궁합 매치", "👥 친구 관리 및 등록 (제작자 전용)", "📖 사주 오행 가이드"])
else:
    tab_match_solo, tab_match_couple, tab_guide = st.tabs(["💘 솔로 궁합 매치", "💞 커플 궁합 매치", "📖 사주 오행 가이드"])

# ==========================================
# TAB 1: 솔로 궁합 매칭 (Match Finder)
# ==========================================
with tab_match_solo:
    # Session state initialization
    if 'u_name' not in st.session_state:
        st.session_state.u_name = ""
    if 'u_phone' not in st.session_state:
        st.session_state.u_phone = ""
    if 'u_gender' not in st.session_state:
        st.session_state.u_gender = "여자"
    if 'u_pref' not in st.session_state:
        st.session_state.u_pref = "모든 성별"
    if 'u_birth' not in st.session_state:
        st.session_state.u_birth = datetime.date(1995, 1, 1)
    if 'u_calendar' not in st.session_state:
        st.session_state.u_calendar = "양력"
    if 'u_has_time' not in st.session_state:
        st.session_state.u_has_time = False
    if 'u_time_branch' not in st.session_state:
        st.session_state.u_time_branch = TIME_BRANCHES[0]
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
        
    st.markdown("<h3 style='margin-top: 10px;'>🔍 이전 프로필 불러오기</h3>", unsafe_allow_html=True)
    
    users_db = load_users_db()
    
    col_search_input, col_search_btn = st.columns([3, 1])
    with col_search_input:
        search_phone = st.text_input("핸드폰 뒷자리 4자리를 입력하세요 (이전에 번호를 등록했던 사용자만 검색 가능)", max_chars=4, placeholder="예: 1234")
    with col_search_btn:
        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        do_search = st.button("🔍 프로필 검색")
        
    if do_search:
        if not search_phone.strip():
            st.warning("⚠️ 핸드폰 뒷자리를 입력해주세요.")
            st.session_state.search_results = []
        else:
            matches = [u for u in users_db if u.get('phone') == search_phone.strip()]
            if not matches:
                st.warning("⚠️ 일치하는 프로필이 없습니다.")
                st.session_state.search_results = []
            else:
                st.session_state.search_results = matches
                st.success(f"{len(matches)}명의 프로필을 찾았습니다! 아래에서 선택해주세요.")
                
    selected_user = None
    if st.session_state.search_results:
        if len(st.session_state.search_results) == 1:
            selected_user = st.session_state.search_results[0]
            st.info(f"✅ **{selected_user['이름']}**님의 프로필이 확인되었습니다.")
        else:
            names = [u['이름'] for u in st.session_state.search_results]
            sel_name = st.selectbox("동일한 번호가 있습니다. 본인의 닉네임을 선택해 주세요.", ["선택하세요"] + names)
            if sel_name != "선택하세요":
                selected_user = next(u for u in st.session_state.search_results if u['이름'] == sel_name)
                
    if selected_user:
        col_load, col_del = st.columns([1, 1])
        with col_load:
            if st.button("⬇️ 이 프로필 정보로 아래 입력창 채우기"):
                st.session_state.u_name = selected_user['이름']
                st.session_state.u_phone = selected_user.get('phone', '')
                st.session_state.u_gender = selected_user['성별']
                st.session_state.u_pref = selected_user.get('pref', '모든 성별')
                st.session_state.u_birth = datetime.datetime.strptime(selected_user['birth_date'], "%Y-%m-%d").date()
                st.session_state.u_calendar = selected_user.get('calendar', '양력')
                st.session_state.u_has_time = selected_user.get('has_time', False)
                if selected_user.get('has_time') and selected_user.get('birth_time'):
                    st.session_state.u_time_branch = get_branch_from_time_str(selected_user['birth_time'])
                st.rerun()
                
        with col_del:
            if st.button("🗑️ 프로필 영구 삭제하기"):
                users_db = [u for u in users_db if u['이름'] != selected_user['이름']]
                save_users_db(users_db)
                friends_db = load_friends_db()
                friends_db = [f for f in friends_db if f['이름'] != selected_user['이름']]
                save_friends_db(friends_db)
                st.session_state.search_results = []
                st.success("🗑️ 프로필이 완전히 삭제되었습니다.")
                st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 10px;'>내 정보 입력하기</h3>", unsafe_allow_html=True)
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        u_name = st.text_input("이름 또는 닉네임", key="u_name", placeholder="예: 길동이")
        u_phone = st.text_input("핸드폰 뒷자리 (선택. 향후 정보 불러오기/삭제 용도로만 안전하게 사용됩니다)", max_chars=4, key="u_phone", placeholder="예: 1234")
        u_gender = st.selectbox("나의 성별", ["여자", "남자"], key="u_gender")
        u_pref = st.selectbox("어떤 상대와 매칭할까요?", ["모든 성별", "남자만", "여자만"], key="u_pref")
        
    with col_input2:
        u_birth = st.date_input(
            "생년월일 선택", 
            key="u_birth",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date(2100, 12, 31)
        )
        u_calendar = st.radio("달력 종류", ["양력", "음력(평달)", "음력(윤달)"], key="u_calendar", horizontal=True)
        
        u_has_time = st.checkbox("태어난 시간을 아시나요?", key="u_has_time")
        if u_has_time:
            u_time_branch = st.selectbox("태어난 시간 (12지시)", TIME_BRANCHES, key="u_time_branch")
            u_hour, u_minute = get_hour_min_from_branch(u_time_branch)
        else:
            u_hour = None
            u_minute = 0
            u_time_branch = None
            
    # Actions Layout: Save Profile & Run Matching
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        save_profile = st.button("💾 내 프로필 저장 / 업데이트")
        if save_profile:
            if not u_name.strip():
                st.warning("⚠️ 이름을 입력해 주세요!")
            else:
                users_db = load_users_db()
                if u_has_time:
                    birth_time_str = u_time_branch
                else:
                    birth_time_str = None
                
                new_user = {
                    "이름": u_name.strip(),
                    "phone": u_phone.strip(),
                    "성별": u_gender,
                    "pref": u_pref,
                    "birth_date": u_birth.strftime("%Y-%m-%d"),
                    "calendar": u_calendar,
                    "has_time": u_has_time,
                    "birth_time": birth_time_str
                }
                
                existing_idx = next((idx for idx, u in enumerate(users_db) if u['이름'] == u_name.strip()), None)
                if existing_idx is not None:
                    users_db[existing_idx] = new_user
                    st.success(f"💾 **{u_name.strip()}**님의 프로필이 업데이트되었습니다!")
                else:
                    users_db.append(new_user)
                    st.success(f"💾 **{u_name.strip()}**님의 프로필이 새로 저장되었습니다!")
                save_users_db(users_db)
                st.rerun()
                
    with col_act2:
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        agree_save = st.checkbox("💡 (필수) 입력하신 사주 정보와 닉네임은 매칭 풀에 저장됩니다. 동의하시겠습니까?")
        run_matching = st.button("💘 최고의 궁합 매칭 시작하기")
        
    if run_matching:
        if not u_name.strip():
            st.warning("⚠️ 이름을 입력해 주세요!")
        elif not agree_save:
            st.warning("⚠️ 매칭을 진행하려면 개인정보 저장에 동의해 주세요.")
        elif not friends_db and not users_db:
            st.warning("⚠️ 매칭할 수 있는 대상이 없습니다.")
        else:
            # Convert to solar date if lunar
            solar_date = get_solar_date(u_birth, u_calendar)
            
            # 1. Analyze User Saju
            try:
                user_saju = saju_engine.analyze_saju(
                    year=solar_date.year,
                    month=solar_date.month,
                    day=solar_date.day,
                    hour=u_hour,
                    minute=u_minute
                )
            except Exception as e:
                st.error(f"회원님의 사주 분석 중 오류가 발생했습니다. 생년월일을 확인해 주세요! (오류: {e})")
                user_saju = None
                
            if user_saju:
                # 동의를 받았으므로 DB에 사용자 정보 자동 저장/업데이트
                users_db = load_users_db()
                birth_time_str = u_time_branch if u_has_time else None
                new_user = {
                    "이름": u_name.strip(),
                    "phone": u_phone.strip(),
                    "성별": u_gender,
                    "pref": u_pref,
                    "birth_date": u_birth.strftime("%Y-%m-%d"),
                    "calendar": u_calendar,
                    "has_time": u_has_time,
                    "birth_time": birth_time_str
                }
                existing_idx = next((idx for idx, u in enumerate(users_db) if u['이름'] == u_name.strip()), None)
                if existing_idx is not None:
                    users_db[existing_idx] = new_user
                else:
                    users_db.append(new_user)
                save_users_db(users_db)
                
                # friends_db (전체 매칭 풀) 에도 저장
                existing_f_idx = next((idx for idx, f in enumerate(friends_db) if f['이름'] == u_name.strip()), None)
                if existing_f_idx is not None:
                    friends_db[existing_f_idx] = new_user
                else:
                    friends_db.append(new_user)
                save_friends_db(friends_db)
                
                st.balloons()
                st.success(f"✨ **{u_name}**님의 사주 분석이 완료되었으며 전체 매칭 풀에 안전하게 등록/업데이트되었습니다!")
                
                # Show User's Own Saju Brief
                st.markdown(f"#### 🔮 {u_name}님의 사주 팔자 분석")
                render_saju_analysis(user_saju, u_name)
                
                st.markdown("<br/><hr/><br/>", unsafe_allow_html=True)
                st.markdown("### 🏆 당신과 가장 잘 맞는 인연 TOP 3")
                
                # 2. Filter & Calculate scores for friends
                # Combine friends and users for the matching pool
                combined_pool = list(friends_db)
                for u in users_db:
                    if u['이름'] != u_name.strip():
                        # Prevent duplicate names
                        if not any(f['이름'] == u['이름'] for f in combined_pool):
                            combined_pool.append(u)
                
                # 2. Filter & Calculate scores for combined pool
                match_results = []
                
                for friend in combined_pool:
                    # Filter by gender preference
                    if u_pref == "남자만" and friend['성별'] != "남자":
                        continue
                    if u_pref == "여자만" and friend['성별'] != "여자":
                        continue
                    
                    # Parse birth
                    try:
                        f_birth_str = friend['birth_date']
                        f_birth_date = datetime.datetime.strptime(f_birth_str, "%Y-%m-%d").date()
                        
                        f_calendar = friend.get('calendar', '양력')
                        f_solar_date = get_solar_date(f_birth_date, f_calendar)
                        
                        f_time_str = friend.get('birth_time')
                        if f_time_str:
                            try:
                                if ":" in f_time_str:
                                    f_h, f_m = map(int, f_time_str.split(':'))
                                else:
                                    f_h, f_m = get_hour_min_from_branch(f_time_str)
                            except Exception:
                                f_h, f_m = None, 0
                        else:
                            f_h, f_m = None, 0
                            
                        # Analyze friend saju
                        friend_saju = saju_engine.analyze_saju(
                            year=f_solar_date.year,
                            month=f_solar_date.month,
                            day=f_solar_date.day,
                            hour=f_h,
                            minute=f_m
                        )
                        
                        # Get compatibility
                        comp = saju_engine.get_compatibility(user_saju, friend_saju)
                        match_results.append({
                            'friend_info': friend,
                            'saju_analysis': friend_saju,
                            'compatibility': comp
                        })
                    except Exception as e:
                        st.error(f"친구 '{friend['이름']}' 사주 분석 실패: {e}")
                        
                # Sort by score descending
                match_results = sorted(match_results, key=lambda x: x['compatibility']['total_score'], reverse=True)
                
                if not match_results:
                    st.warning("선택하신 조건(성별 등)에 매칭되는 친구가 없습니다. 친구 목록을 추가하거나 설정을 조정해 주세요.")
                else:
                    # Take top 3
                    top_matches = match_results[:3]
                    
                    for rank, match in enumerate(top_matches):
                        f_info = match['friend_info']
                        f_saju = match['saju_analysis']
                        comp = match['compatibility']
                        
                        rank_emoji = ["🥇 1등", "🥈 2등", "🥉 3등"][rank]
                        
                        # Draw glassmorphic card for match
                        st.markdown(f"""
                        <div class="mystic-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(186, 104, 200, 0.2); padding-bottom: 10px; margin-bottom: 15px;">
                                <span style="font-size: 1.5rem; font-weight: 800; color: #ffeb3b;">{rank_emoji}: {f_info['이름']} ({f_info['성별']})</span>
                                <span class="score-badge">궁합 점수: {comp['total_score']}점</span>
                            </div>
                            <p style="font-size: 1rem; color: #e1bee7; font-style: italic; margin-top: -5px; margin-bottom: 15px;">
                                ✍️ 친구 메모: "{f_info.get('memo', '특별한 정보가 없습니다.')}"
                            </p>
                            <div class="grade-text">{comp['grade']}</div>
                            <div style="margin-bottom: 15px; font-weight: 500; line-height: 1.6;">{comp['grade_desc']}</div>
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 12px; border-radius: 8px; border-left: 3px solid #ffeb3b; font-size: 0.9rem;">
                                <div>🍀 <b>핵심 어울림 포인트:</b></div>
                                <div style="margin-top: 4px;">• {comp['explanations']['stem_desc']}</div>
                                <div style="margin-top: 4px;">• {comp['explanations']['def_desc']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Expander for deep analysis
                        with st.expander(f"🔍 {f_info['이름']}님과의 자세한 사주 분석 & 오행 비교"):
                            col_f_saju_u, col_f_saju_f = st.columns(2)
                            
                            with col_f_saju_u:
                                st.markdown(f"<div style='text-align:center; font-weight: 700; color:#ba68c8; margin-bottom:8px;'>[나] {u_name}님의 명식</div>", unsafe_allow_html=True)
                                u_cols_f = st.columns(4)
                                u_pillars_order = [
                                    ("시주 (Hour)", user_saju['pillars']['hour']),
                                    ("일주 (Day)", user_saju['pillars']['day']),
                                    ("월주 (Month)", user_saju['pillars']['month']),
                                    ("연주 (Year)", user_saju['pillars']['year'])
                                ]
                                for idx, (title, p_data) in enumerate(u_pillars_order):
                                    with u_cols_f[idx]:
                                        st.markdown(get_pillar_card_html(title, p_data), unsafe_allow_html=True)
                                        
                            with col_f_saju_f:
                                st.markdown(f"<div style='text-align:center; font-weight: 700; color:#ce93d8; margin-bottom:8px;'>[상대방] {f_info['이름']}님의 명식</div>", unsafe_allow_html=True)
                                f_cols_f = st.columns(4)
                                f_pillars_order = [
                                    ("시주 (Hour)", f_saju['pillars']['hour']),
                                    ("일주 (Day)", f_saju['pillars']['day']),
                                    ("월주 (Month)", f_saju['pillars']['month']),
                                    ("연주 (Year)", f_saju['pillars']['year'])
                                ]
                                for idx, (title, p_data) in enumerate(f_pillars_order):
                                    with f_cols_f[idx]:
                                        st.markdown(get_pillar_card_html(title, p_data), unsafe_allow_html=True)
                                        
                            st.markdown("<br/>", unsafe_allow_html=True)
                            
                            # Element Distribution Side-by-Side
                            st.markdown("##### 📊 오행(Five Elements) 비율 비교")
                            col_comp_u, col_comp_f = st.columns(2)
                            
                            with col_comp_u:
                                st.markdown(f"<div style='font-size:0.85rem; font-weight:600; margin-bottom:5px;'>{u_name}님의 오행</div>", unsafe_allow_html=True)
                                for el, count in user_saju['element_counts'].items():
                                    pct = user_saju['element_percentages'][el]
                                    st.markdown(make_element_bar_html(el, count, pct), unsafe_allow_html=True)
                                    
                            with col_comp_f:
                                st.markdown(f"<div style='font-size:0.85rem; font-weight:600; margin-bottom:5px;'>{f_info['이름']}님의 오행</div>", unsafe_allow_html=True)
                                for el, count in f_saju['element_counts'].items():
                                    pct = f_saju['element_percentages'][el]
                                    st.markdown(make_element_bar_html(el, count, pct), unsafe_allow_html=True)
                                    
                            st.markdown("<br/>", unsafe_allow_html=True)
                            
                            # Score Breakdown Details
                            st.markdown("##### 🎯 부문별 세부 궁합 점수 (100점 만점)")
                            
                            score_breakdown = comp['breakdown']
                            exps = comp['explanations']
                            
                            score_cols = st.columns(4)
                            
                            with score_cols[0]:
                                st.metric("일간 조화 (정신)", f"{score_breakdown['stem_score']} / 30")
                            with score_cols[1]:
                                st.metric("오행 보완 (시너지)", f"{score_breakdown['def_score']} / 35")
                            with score_cols[2]:
                                st.metric("일지 조화 (속궁합)", f"{score_breakdown['branch_score']} / 20")
                            with score_cols[3]:
                                st.metric("온도 조율 (조후)", f"{score_breakdown['temp_score']} / 15")
                                
                            st.markdown(f"""
                            <div style="background: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 8px; border: 1px solid rgba(186, 104, 200, 0.1); margin-top: 10px;">
                                <p>🧠 <b>정신적 궁합 (일간):</b> {exps['stem_desc']}</p>
                                <p>🧩 <b>오행 결핍보완:</b> {exps['def_desc']}</p>
                                <p>🚪 <b>현실/속궁합 (일지):</b> {exps['branch_desc']}</p>
                                <p>🌡️ <b>에너지 온도 조화:</b> {exps['temp_desc']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown("<br/>", unsafe_allow_html=True)
                            
                    # Show best record from DB
                    best_record = get_best_match_record(json.dumps(friends_db))
                    if best_record:
                        m_n, f_n, b_s = best_record
                        st.info(f"🏆 **현재까지 지인분들 중 최고 궁합은 '{m_n}'님과 '{f_n}'님으로 {b_s}점 입니다! (기록을 깨보세요!)**")

# ==========================================
# TAB 1-2: 커플 궁합 매치 (Couple Match)
# ==========================================
with tab_match_couple:
    st.markdown("<h3 style='margin-top: 10px;'>💞 우리 커플의 궁합 점수는?</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #b39ddb;'>두 분의 생년월일을 입력하시면, 사주 오행과 성향을 분석하여 궁합 점수와 특징을 알려드립니다. (※ 입력된 정보는 데이터베이스에 저장되지 않습니다.)</p>", unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### 🧑‍🦰 남성 사주 정보")
        c_name1 = st.text_input("닉네임 (남성)", key="c_name1")
        c_birth1 = st.date_input("생년월일 (남성)", key="c_birth1", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), value=datetime.date(1995, 1, 1))
        c_calendar1 = st.radio("달력 종류 (남성)", ["양력", "음력(평달)", "음력(윤달)"], key="c_calendar1", horizontal=True)
        c_has_time1 = st.checkbox("태어난 시간을 아시나요? (남성)", key="c_has_time1")
        c_hour1, c_min1 = None, 0
        if c_has_time1:
            c_time_branch1 = st.selectbox("태어난 시간 (남성)", TIME_BRANCHES, key="c_time_branch1")
            c_hour1, c_min1 = get_hour_min_from_branch(c_time_branch1)
            
    with col_c2:
        st.markdown("#### 👩‍🦱 여성 사주 정보")
        c_name2 = st.text_input("닉네임 (여성)", key="c_name2")
        c_birth2 = st.date_input("생년월일 (여성)", key="c_birth2", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31), value=datetime.date(1995, 1, 1))
        c_calendar2 = st.radio("달력 종류 (여성)", ["양력", "음력(평달)", "음력(윤달)"], key="c_calendar2", horizontal=True)
        c_has_time2 = st.checkbox("태어난 시간을 아시나요? (여성)", key="c_has_time2")
        c_hour2, c_min2 = None, 0
        if c_has_time2:
            c_time_branch2 = st.selectbox("태어난 시간 (여성)", TIME_BRANCHES, key="c_time_branch2")
            c_hour2, c_min2 = get_hour_min_from_branch(c_time_branch2)
            
    run_couple = st.button("💞 우리 궁합 점수 확인하기")
    
    if run_couple:
        if not c_name1.strip() or not c_name2.strip():
            st.warning("⚠️ 두 분의 닉네임을 모두 입력해 주세요!")
        else:
            try:
                solar_c1 = get_solar_date(c_birth1, c_calendar1)
                solar_c2 = get_solar_date(c_birth2, c_calendar2)
                
                saju1 = saju_engine.analyze_saju(solar_c1.year, solar_c1.month, solar_c1.day, c_hour1, c_min1)
                saju2 = saju_engine.analyze_saju(solar_c2.year, solar_c2.month, solar_c2.day, c_hour2, c_min2)
                
                comp = saju_engine.calculate_compatibility(saju1, saju2)
                st.balloons()
                st.success("✨ 두 분의 궁합 분석이 완료되었습니다!")
                
                st.markdown("---")
                st.markdown(f"#### 🧑‍🦰 남성측({c_name1}) 사주 분석")
                render_saju_analysis(saju1, c_name1)
                
                st.markdown("---")
                st.markdown(f"#### 👩‍🦱 여성측({c_name2}) 사주 분석")
                render_saju_analysis(saju2, c_name2)
                
                st.markdown("---")
                st.markdown(f"### 💖 {c_name1} 님과 {c_name2} 님의 최종 궁합 점수: <span style='color:#ffeb3b; font-size:2rem;'>{comp['score']}점</span>", unsafe_allow_html=True)
                st.markdown(f"**궁합 등급:** {comp['grade']}")
                st.markdown("<br/>", unsafe_allow_html=True)
                
                st.markdown("##### 🎯 부문별 궁합 해설")
                score_breakdown = comp['breakdown']
                exps = comp['explanations']
                
                s_cols = st.columns(4)
                with s_cols[0]: st.metric("정신적 조화 (일간)", f"{score_breakdown['stem_score']} / 30")
                with s_cols[1]: st.metric("오행 보완성", f"{score_breakdown['def_score']} / 35")
                with s_cols[2]: st.metric("현실적 조화 (일지)", f"{score_breakdown['branch_score']} / 20")
                with s_cols[3]: st.metric("온도 조화 (조후)", f"{score_breakdown['temp_score']} / 15")
                
                st.markdown(f'''
                <div class="mystic-card" style="margin-top: 15px;">
                    <p>🧠 <b>가치관 및 소통 (일간):</b> {exps["stem_desc"]}</p>
                    <p>🧩 <b>오행 시너지:</b> {exps["def_desc"]}</p>
                    <p>🚪 <b>현실 및 환경 조화 (일지):</b> {exps["branch_desc"]}</p>
                    <p>🌡️ <b>에너지 조율 (조후):</b> {exps["temp_desc"]}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Show best record from DB
                friends_db = load_friends_db()
                best_record = get_best_match_record(json.dumps(friends_db))
                if best_record:
                    m_n, f_n, b_s = best_record
                    st.info(f"🏆 **현재까지 지인분들 중 최고 궁합은 '{m_n}'님과 '{f_n}'님으로 {b_s}점 입니다! (기록을 깨보세요!)**")
                
            except Exception as e:
                st.error(f"궁합 분석 중 오류가 발생했습니다: {e}")

# ==========================================
# TAB 2: 친구 관리 및 등록 (Manage Friends)
# ==========================================
if is_maker:
    with tab_friends:
        st.markdown("<h3 style='margin-top: 10px;'>👥 등록된 친구 목록</h3>", unsafe_allow_html=True)
        st.write("내 주변 매칭 후보군에 등록된 친구들의 목록입니다. Saju 일주(일간+일지)와 동물이 자동으로 분석되어 표시됩니다.")
        
        if not friends_db:
            st.info("현재 등록된 친구가 없습니다. 아래 양식에서 친구를 새로 등록해 주세요!")
        else:
            # Build a table of friends with parsed Saju using pandas
            table_data = []
            for idx, friend in enumerate(friends_db):
                try:
                    f_birth = datetime.datetime.strptime(friend['birth_date'], "%Y-%m-%d").date()
                    
                    # 달력 타입 변환 로직 (기본은 양력, 있으면 음력 -> 양력 변환)
                    f_calendar = friend.get('calendar', '양력')
                    f_solar_date = get_solar_date(f_birth, f_calendar)

                    f_time = friend.get('birth_time')
                    if f_time:
                        try:
                            if ":" in f_time:
                                f_h, f_m = map(int, f_time.split(':'))
                            else:
                                f_h, f_m = get_hour_min_from_branch(f_time)
                        except Exception:
                            f_h, f_m = None, 0
                    else:
                        f_h, f_m = None, 0
                        
                    f_saju = saju_engine.analyze_saju(f_solar_date.year, f_solar_date.month, f_solar_date.day, f_h, f_m)
                    
                    day_pillar_str = f"{f_saju['day_stem_kr']}{f_saju['day_branch_kr']} ({f_saju['day_stem']}{f_saju['day_branch']})"
                    animal = f_saju['pillars']['day']['branch_animal']
                    element = f_saju['day_stem_element']
                    
                    table_data.append({
                        "번호": idx + 1,
                        "이름": friend['이름'],
                        "핸드폰": friend.get('phone', '-'),
                        "성별": friend['성별'],
                        "생년월일": friend['birth_date'],
                        "달력": f_calendar,
                        "시간": friend.get('birth_time') or '모름',
                        "태어난 일주": day_pillar_str,
                        "오행 및 동물": f"{animal} ({element})",
                        "메모": friend.get('memo', '')
                    })
                except Exception as e:
                    table_data.append({
                        "번호": idx + 1,
                        "이름": friend['이름'] + " (에러)",
                        "핸드폰": friend.get('phone', '-'),
                        "성별": friend.get('성별', '-'),
                        "생년월일": friend.get('birth_date', '-'),
                        "달력": friend.get('calendar', '-'),
                        "시간": friend.get('birth_time') or '모름',
                        "태어난 일주": f"에러: {e}",
                        "오행 및 동물": "-",
                        "메모": "-"
                    })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        st.write("---")
        
        # Grid for Add and Delete forms
        col_add, col_del = st.columns(2)
        
        with col_add:
            st.markdown("<h4>➕ 새로운 친구 등록하기</h4>", unsafe_allow_html=True)
            with st.container():
                add_name = st.text_input("친구 이름 또는 닉네임", placeholder="예: 무쇠팔")
                add_gender = st.selectbox("친구 성별", ["남자", "여자"])
                add_birth = st.date_input(
                    "친구 생년월일 (양력)", 
                    value=datetime.date(1995, 1, 1),
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date(2100, 12, 31)
                )
                add_has_time = st.checkbox("친구 태어난 시간을 아시나요?")
                
                add_hour = None
                add_minute = 0
                if add_has_time:
                    time_cols_add = st.columns(3)
                    with time_cols_add[0]:
                        add_ampm = st.selectbox("오전/오후 (친구)", ["오전 (AM)", "오후 (PM)"], key="add_ampm")
                    with time_cols_add[1]:
                        add_hour_12 = st.selectbox("시간 (1시~12시) (친구)", list(range(1, 13)), index=11, key="add_hour_12")
                    with time_cols_add[2]:
                        add_minute = st.selectbox("분 (친구)", [0, 10, 20, 30, 40, 50], index=0, key="add_minute")
                    
                    if add_ampm == "오전 (AM)":
                        add_hour = 0 if add_hour_12 == 12 else add_hour_12
                    else:
                        add_hour = 12 if add_hour_12 == 12 else add_hour_12 + 12
                
                add_memo = st.text_input("간단한 메모 (성격, 키워드 등)", placeholder="예: 유쾌한 친구, 운동 매니아")
                
                submit_add = st.button("친구 데이터베이스에 등록")
                if submit_add:
                    if not add_name.strip():
                        st.error("이름을 입력해 주세요!")
                    elif any(f['이름'] == add_name.strip() for f in friends_db):
                        st.error("이미 같은 이름의 친구가 등록되어 있습니다. 다른 고유한 이름을 사용해 주세요.")
                    else:
                        new_friend = {
                            "이름": add_name.strip(),
                            "성별": add_gender,
                            "birth_date": add_birth.strftime("%Y-%m-%d"),
                            "birth_time": f"{add_hour:02d}:{add_minute:02d}" if add_has_time else None,
                            "memo": add_memo.strip()
                        }
                        friends_db.append(new_friend)
                        save_friends_db(friends_db)
                        st.success(f"🎉 **{add_name.strip()}**님이 성공적으로 등록되었습니다!")
                        st.rerun()
                        
        with col_del:
            st.markdown("<h4>🗑️ 친구 정보 삭제하기</h4>", unsafe_allow_html=True)
            if not friends_db:
                st.write("삭제할 친구가 없습니다.")
            else:
                friend_names = [f['이름'] for f in friends_db]
                del_names = st.multiselect("삭제할 친구들을 선택하세요 (여러 명 선택 가능)", friend_names)
                submit_del = st.button("선택한 친구 일괄 삭제")
                
                if submit_del:
                    if not del_names:
                        st.warning("⚠️ 삭제할 친구를 최소 1명 이상 선택해 주세요.")
                    else:
                        friends_db = [f for f in friends_db if f['이름'] not in del_names]
                        save_friends_db(friends_db)
                        st.success(f"🗑️ 선택하신 {len(del_names)}명의 데이터가 완전히 삭제되었습니다.")
                        st.rerun()

# ==========================================
# TAB 3: 사주 오행 가이드 (Saju Guide)
# ==========================================
with tab_guide:
    st.markdown("<h3 style='margin-top: 10px;'>📖 사주와 오행 알아보기</h3>", unsafe_allow_html=True)
    st.write("명리학에서 말하는 만물의 다섯 가지 원소(오행)와 그 조화에 대해 알아봅니다. 궁합 점수가 어떻게 계산되는지 이해할 수 있습니다.")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("""
        <div class="mystic-card">
            <h4>🌱 오행(五行)의 기본 성향</h4>
            <ul>
                <li><b class="badge-wood">목(木 - Wood):</b> 파란색/초록색. 성장과 창조, 기획력을 상징합니다. 시작하는 힘이 강하며 유연하지만 고집이 있을 수 있습니다.</li>
                <li><b class="badge-fire">화(火 - Fire):</b> 빨간색. 열정과 표현력, 예의를 상징합니다. 감정을 솔직히 표현하고 분위기를 밝게 만들지만 끈기가 필요할 때가 있습니다.</li>
                <li><b class="badge-earth">토(土 - Earth):</b> 노란색. 신뢰와 포용력, 중재를 상징합니다. 안정감 있고 묵묵하게 남의 말을 잘 들어주며 조화를 이끌어냅니다.</li>
                <li><b class="badge-metal">금(金 - Metal):</b> 흰색/회색. 결단력과 정의, 의리를 상징합니다. 맺고 끊음이 확실하며 깔끔하지만 다소 냉철해 보일 수 있습니다.</li>
                <li><b class="badge-water">수(水 - Water):</b> 검은색/파란빛. 지혜와 직관, 유연함을 상징합니다. 지식 탐구욕이 강하고 상황 대처 능력이 좋지만 생각이 많아 행동이 느릴 수 있습니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_g2:
        st.markdown("""
        <div class="mystic-card">
            <h4>🔄 상생(相生)과 상극(相剋)</h4>
            <p><b>상생 (서로를 돕는 순환):</b></p>
            <p>나무(木)가 타서 불(火)을 생하고, 불(火)이 타서 흙(土)을 생하며, 흙(土) 속에서 쇠(金)가 나고, 쇠(金)에서 물(水)이 맺히며, 물(水)이 나무(木)를 기릅니다. 이 순환이 유기적일 때 서로 시너지가 생깁니다.</p>
            <p><b>상극 (서로를 통제하는 긴장):</b></p>
            <p>나무(木)는 흙(土)의 양분을 빼앗고, 흙(土)은 물(水)을 흐리거나 가두며, 물(水)은 불(火)을 끄고, 불(火)은 쇠(金)를 녹이며, 쇠(金)는 나무(木)를 베어 냅니다. 적당한 극(剋)은 상대방에게 긴장감과 매력을 제공합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div class="mystic-card" style="width: 100%;">
        <h4>🤝 궁합(宮合) 매칭 평가 기준</h4>
        <ol>
            <li><b>일간 조화 (정신적 합 - 30점):</b> 나와 상대방의 타고난 영혼의 성향(일간)이 천간합(甲己, 乙庚, 丙辛, 丁壬, 戊癸)을 이루거나 오행 상생 관계인지 확인합니다.</li>
            <li><b>오행 결핍 보완 (시너지 - 35점):</b> 나에게 없는 결핍된 오행 기운을 상대방이 넉넉히 가지고 있는지를 점수화합니다. 나를 숨 쉬게 해주는 상대를 찾는 가장 현실적인 점수입니다.</li>
            <li><b>일지 조화 (현실적 속궁합 - 20점):</b> 부부궁이자 사생활을 의미하는 일지(日支)가 서로 육합(六合)이나 삼합(三合)으로 강하게 끌어당기는지 확인합니다.</li>
            <li><b>온도 조율 (조후 균형 - 15점):</b> 한 명이 뜨겁고 건조한 사주(화 기운 과다)일 때 다른 한 명이 차갑고 습한 사주(수 기운 과다)라면 에너지가 만나 완벽한 중화를 이루므로 높게 평가합니다.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
