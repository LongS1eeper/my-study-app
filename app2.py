import streamlit as st
import json
import os
import random
import re

# ==========================================
# 1. 페이지 설정 (반드시 코드 최상단에 위치)
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터 V2",
    page_icon="💰",
    layout="centered"
)

# ==========================================
# 2. 고급 CSS 디자인 적용
# ==========================================
st.markdown("""
    <style>
    /* [전체 폰트 및 배경] */
    .main {
        background-color: #f8f9fa;
    }
    
    /* [사이드바 디자인 수정] */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2, 
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #2c3e50 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #455a64 !important;
        font-weight: 500;
        font-size: 15px !important;
    }
    
    /* [메인 문제 박스] */
    .question-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        border-top: 5px solid #4CAF50; /* 포인트 컬러 */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .question-header {
        font-size: 14px;
        color: #888;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .question-text {
        font-size: 20px;
        font-weight: 700;
        color: #222;
        line-height: 1.6;
    }

    /* [보기 박스 (Context)] */
    .context-box {
        background-color: #e3f2fd; /* 연한 파랑 */
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2196F3;
        margin-bottom: 20px;
        font-size: 16px;
        color: #0d47a1;
        white-space: pre-line;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }

    /* [라디오 버튼 커스텀 - 카드 형태 (선택 전)] */
    .stRadio > div {
        background-color: transparent;
    }
    .stRadio label {
        background-color: white;
        padding: 15px 20px;
        border-radius: 12px;
        border: 2px solid #f0f0f0;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 16px;
        color: #333 !important; /* 글자색 강제 지정 */
        display: block; /* 박스 전체 클릭 가능하게 */
    }
    .stRadio label:hover {
        border-color: #4CAF50;
        background-color: #f1f8e9;
        transform: translateY(-2px);
    }

    /* [버튼 스타일] */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 55px;
        font-weight: 800;
        font-size: 18px;
        border: none;
        transition: transform 0.1s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* [해설 박스] */
    .explanation-box {
        background-color: #fff8e1; /* 연한 노랑 */
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #ffe0b2;
        margin-top: 25px;
        line-height: 1.7;
        color: #5d4037;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 로드 (자동 수리 기능 탑재)
# ==========================================
DB_FILE = "database2.json"
WRONG_NOTE_FILE = "wrong_notes_v2.json"

@st.cache_data
def load_data():
    if not os.path.exists(DB_FILE):
        st.error(f"❌ {DB_FILE} 파일을 찾을 수 없습니다.")
        return []
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        # 자동 수리 로직
        content = re.sub(r"\]\s*\[", ", ", content)
        latex_keywords = [
            "times", "sigma", "sqrt", "frac", "mu", "le", "ge", "ne", 
            "approx", "sum", "prod", "int", "alpha", "beta", "gamma", 
            "delta", "theta", "lambda", "pi", "rho", "phi", "omega"
        ]
        for word in latex_keywords:
            pattern = r'(?<!\\)\\' + word 
            replacement = r'\\\\' + word   
            content = re.sub(pattern, replacement, content)
        content = re.sub(r'(?<!\\)\\f', r'\\\\f', content)
        content = content.strip()
        if not content.startswith("["): content = "[" + content
        if not content.endswith("]"): content = content + "]"

        return json.loads(content)

    except json.JSONDecodeError:
        return []

def load_wrong_notes():
    if os.path.exists(WRONG_NOTE_FILE):
        with open(WRONG_NOTE_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_wrong_note(question_item):
    current_notes = load_wrong_notes()
    if not any(q['id'] == question_item['id'] for q in current_notes):
        current_notes.append(question_item)
        with open(WRONG_NOTE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_notes, f, ensure_ascii=False, indent=2)

# ==========================================
# 4. 세션 및 사이드바 설정
# ==========================================
if 'quiz_started' not in st.session_state:
    st.session_state.update({
        'quiz_data': [], 'current_idx': 0, 'score': 0,
        'quiz_started': False, 'show_answer': False, 'user_selection': None
    })

all_data = load_data()
wrong_data = load_wrong_notes()

# [사이드바 메뉴 구성]
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4762/4762311.png", width=80)
st.sidebar.title("🔥 투운사 합격 모드")
st.sidebar.markdown("---")

basic_modes = ["전체 문제 정주행", "랜덤 20문항 모의고사", "오답 노트 집중공략", "🎯 커스텀 범위 설정 (ID 직접 입력)"]
exam_modes = [
    "실전 모의고사 1회 (183~282번)",
    "실전 모의고사 2회 (283~382번)",
    "실전 모의고사 3회 (383~482번)",
    "실전 모의고사 4회 (483~582번)",
    "실전 모의고사 5회 (583~682번)"
]

mode = st.sidebar.radio(
    "학습 방법을 선택하세요", 
    basic_modes + exam_modes
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 처음으로 리셋", type="secondary"):
    st.session_state['quiz_started'] = False
    st.rerun()

if wrong_data:
    st.sidebar.success(f"📝 오답노트: {len(wrong_data)}개 저장됨")

# ==========================================
# 5. 메인 화면 로직
# ==========================================

# [퀴즈 대기 화면]
if not st.session_state['quiz_started']:
    st.title("💰 투자자산운용사 마스터")
    st.markdown("### 합격을 위한 완벽한 파트너 🚀")
    
    if not all_data:
        st.error("⚠️ 데이터 파일(database2.json)을 불러오지 못했습니다.")
    else:
        # 데이터 ID 범위 확인
        all_ids = [q['id'] for q in all_data]
        min_db_id = min(all_ids) if all_ids else 0
        max_db_id = max(all_ids) if all_ids else 0

        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9;">
            📊 현재 데이터베이스: 총 <strong>{len(all_data)}</strong>문제 (ID: {min_db_id} ~ {max_db_id})<br>
            👉 선택된 모드: <strong>{mode}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        final_questions = []
        
        # 1. 커스텀 범위 설정 모드
        if mode == "🎯 커스텀 범위 설정 (ID 직접 입력)":
            st.warning("🧐 풀고 싶은 문제의 ID 범위를 입력하세요.")
            col1, col2 = st.columns(2)
            with col1:
                start_id = st.number_input("시작 번호", min_value=min_db_id, max_value=max_db_id, value=min_db_id)
            with col2:
                end_id = st.number_input("종료 번호", min_value=min_db_id, max_value=max_db_id, value=max_db_id)
            
            if start_id > end_id:
                st.error("❌ 시작 번호가 종료 번호보다 클 수 없습니다.")
            else:
                final_questions = [q for q in all_data if start_id <= q['id'] <= end_id]
                final_questions.sort(key=lambda x: x['id'])
                if not final_questions:
                    st.error(f"⚠️ 해당 범위({start_id}~{end_id})에 해당하는 문제가 없습니다.")

        # 2. 기본 모드 처리
        elif mode == "전체 문제 정주행":
            final_questions = all_data.copy()
            final_questions.sort(key=lambda x: x['id'])
        elif mode == "랜덤 20문항 모의고사":
            final_questions = random.sample(all_data, min(20, len(all_data)))
        elif mode == "오답 노트 집중공략":
            final_questions = wrong_data
            if not final_questions:
                st.warning("🎉 저장된 오답이 없습니다! 완벽하시네요.")
        
        # 3. 실전 모의고사 회차별 처리
        elif "실전 모의고사" in mode:
            exam_ranges = {
                "1회": (183, 282), "2회": (283, 382), "3회": (383, 482),
                "4회": (483, 582), "5회": (583, 682)
            }
            for key, (start_id, end_id) in exam_ranges.items():
                if f"모의고사 {key}" in mode:
                    final_questions = [q for q in all_data if start_id <= q['id'] <= end_id]
                    final_questions.sort(key=lambda x: x['id'])
                    break
            
            if not final_questions:
                st.warning("⚠️ 해당 회차의 문제 데이터를 찾을 수 없습니다.")

        # 문제 풀기 버튼 (문제가 있을 때만 표시)
        if final_questions:
            btn_text = f"🏁 문제 풀기 시작하기 (총 {len(final_questions)}문제)"
            if st.button(btn_text, type="primary"):
                # 랜덤 모드나 오답 노트만 섞기, 나머지는 번호순 정렬
                if mode == "랜덤 20문항 모의고사" or mode == "오답 노트 집중공략":
                    random.shuffle(final_questions)
                
                st.session_state['quiz_data'] = final_questions
                st.session_state['current_idx'] = 0
                st.session_state['score'] = 0
                st.session_state['quiz_started'] = True
                st.session_state['show_answer'] = False
                st.session_state['user_selection'] = None
                st.rerun()

# [퀴즈 진행 화면]
else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    if idx >= len(q_list):
        st.balloons()
        st.markdown(f"""
            <div style="text-align: center; padding: 40px; background-color: #fff; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                <h1 style="font-size: 60px;">🏆</h1>
                <h2 style="color: #2c3e50;">학습이 종료되었습니다!</h2>
                <hr>
                <p style="font-size: 24px;">내 점수: <span style="color: #4CAF50; font-weight: bold;">{st.session_state['score']}</span> / {len(q_list)}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 홈으로 돌아가기", type="primary"):
            st.session_state['quiz_started'] = False
            st.rerun()
    else:
        # 상단 진행바
        progress = (idx + 1) / len(q_list)
        st.progress(progress)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"🚀 Progress: {idx + 1} / {len(q_list)}")
        with col2:
            st.caption(f"🏆 Score: {st.session_state['score']}")
        
        question = q_list[idx]
        
        # [문제 카드]
        st.markdown(f"""
        <div class="question-box">
            <div class="question-header">QUESTION {question['id']}</div>
            <div class="question-text">{question['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if question.get('context'):
            st.markdown(f'<div class="context-box">📢 <strong>보기</strong><br>{question["context"]}</div>', unsafe_allow_html=True)

        options = question['options']

        # ----------------------------------------------------
        # [상태 1] 정답 선택 전 (라디오 버튼 표시)
        # ----------------------------------------------------
        if not st.session_state['show_answer']:
            st.markdown("👇 **정답을 선택하세요**")
            choice = st.radio("정답 선택", options, index=None, key=f"q_{idx}", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("채점하기 ✅", type="primary", disabled=(choice is None)):
                st.session_state['user_selection'] = choice
                st.session_state['show_answer'] = True
                st.rerun()
        
        # ----------------------------------------------------
        # [상태 2] 채점 완료 후 (결과 및 색상 표시)
        # ----------------------------------------------------
        else:
            user_choice = st.session_state['user_selection']
            try:
                user_idx = options.index(user_choice) + 1
            except:
                user_idx = -1
            
            correct_idx = question['answer']
            
            # 1. 상단 정오답 배너 표시
            if user_idx == correct_idx:
                st.markdown("""
                    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 2px solid #4CAF50; text-align: center; margin-bottom: 20px;">
                        <h3 style="color: #2e7d32; margin: 0;">🎉 정답입니다!</h3>
                    </div>
                """, unsafe_allow_html=True)
                if 'processed' not in st.session_state:
                    st.session_state['score'] += 1
                    st.session_state['processed'] = True
            else:
                st.markdown(f"""
                    <div style="background-color: #ffebee; padding: 15px; border-radius: 10px; border: 2px solid #ef5350; text-align: center; margin-bottom: 20px;">
                        <h3 style="color: #c62828; margin: 0;">😥 틀렸습니다!</h3>
                        <p style="color: #555; margin-top: 5px;">선택한 답: {user_idx}번</p>
                    </div>
                """, unsafe_allow_html=True)
                if 'processed' not in st.session_state:
                    save_wrong_note(question)
                    st.session_state['processed'] = True
            
            # 2. 선지 전체 보여주기 (맞은 답은 초록, 틀린 답은 빨강 배경)
            for i, option_text in enumerate(options):
                opt_num = i + 1
                
                # 기본 스타일 (선택 안 한 나머지)
                div_style = "padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e0e0e0; background-color: #f9f9f9; color: #555;"
                prefix = f"{opt_num}. "
                
                # 색상 로직 적용
                if opt_num == correct_idx:
                    # 정답인 선지 (항상 초록색)
                    div_style = "padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #4CAF50; background-color: #e8f5e9; color: #2e7d32; font-weight: bold;"
                    prefix = "✅ "
                elif opt_num == user_idx and user_idx != correct_idx:
                    # 내가 고른 오답 선지 (빨간색)
                    div_style = "padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #ef5350; background-color: #ffebee; color: #c62828; font-weight: bold;"
                    prefix = "❌ "
                
                st.markdown(f'<div style="{div_style}">{prefix}{option_text}</div>', unsafe_allow_html=True)

            # 3. 해설 박스
            st.markdown(f"""
            <div class="explanation-box">
                <strong style="font-size: 18px;">💡 상세 해설</strong><br><br>
                {question['explanation']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 4. 다음 문제 버튼
            if st.button("다음 문제로 넘어가기 ➡️", type="primary"):
                st.session_state['current_idx'] += 1
                st.session_state['show_answer'] = False
                st.session_state['user_selection'] = None
                if 'processed' in st.session_state:
                    del st.session_state['processed']
                st.rerun()