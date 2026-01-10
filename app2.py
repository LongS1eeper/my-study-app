import streamlit as st
import json
import os
import random

# ==========================================
# 1. 페이지 설정 (반드시 코드 최상단에 위치)
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터 V2",
    page_icon="🏆",
    layout="centered"
)

# 디자인 커스텀 (모바일 가독성 최적화)
st.markdown("""
    <style>
    .question-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .question-text {
        font-size: 18px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .context-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 15px;
        font-size: 15px;
        color: #495057;
        white-space: pre-line;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 55px;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
    }
    .explanation-box {
        background-color: #fff8e1; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #ffe0b2;
        margin-top: 20px;
        line-height: 1.6;
    }
    /* 라디오 버튼 크기 키우기 (터치하기 편하게) */
    .stRadio label {
        font-size: 16px;
        padding: 10px;
        border-radius: 8px;
        background-color: #f8f9fa;
        margin-bottom: 5px;
        display: block;
        cursor: pointer;
    }
    .stRadio label:hover {
        background-color: #e9ecef;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드
# ==========================================
DB_FILE = "database2.json"
WRONG_NOTE_FILE = "wrong_notes_v2.json"

@st.cache_data
def load_data():
    if not os.path.exists(DB_FILE):
        st.error(f"❌ {DB_FILE} 파일을 찾을 수 없습니다.")
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            st.error("JSON 파일 형식이 올바르지 않습니다.")
            return []

def load_wrong_notes():
    if os.path.exists(WRONG_NOTE_FILE):
        with open(WRONG_NOTE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_wrong_note(question_item):
    current_notes = load_wrong_notes()
    if not any(q['id'] == question_item['id'] for q in current_notes):
        current_notes.append(question_item)
        with open(WRONG_NOTE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_notes, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. 세션 초기화
# ==========================================
if 'quiz_started' not in st.session_state:
    st.session_state.update({
        'quiz_data': [], 'current_idx': 0, 'score': 0,
        'quiz_started': False, 'show_answer': False, 'user_selection': None
    })

# ==========================================
# 4. 사이드바 메뉴
# ==========================================
st.sidebar.title("📚 학습 메뉴")
mode = st.sidebar.radio("모드 선택", ["전체 문제 풀기", "랜덤 20문항", "오답 노트"])

if st.sidebar.button("🔄 처음으로 리셋", type="primary"):
    st.session_state['quiz_started'] = False
    st.rerun()

all_data = load_data()
wrong_data = load_wrong_notes()

if wrong_data:
    st.sidebar.caption(f"📝 오답노트: {len(wrong_data)}문제")

# ==========================================
# 5. 메인 화면
# ==========================================
st.title("💰 투운사 마스터 V2")

# --- 퀴즈 대기 화면 ---
if not st.session_state['quiz_started']:
    st.markdown("---")
    st.info(f"총 **{len(all_data)}**개의 문제가 준비되어 있습니다.")
    
    final_questions = []
    if mode == "전체 문제 풀기":
        final_questions = all_data.copy()
    elif mode == "랜덤 20문항":
        final_questions = random.sample(all_data, min(20, len(all_data)))
    elif mode == "오답 노트":
        final_questions = wrong_data
        if not final_questions:
            st.warning("저장된 오답이 없습니다.")

    if final_questions:
        if st.button("🚀 문제 풀기 시작", type="primary"):
            if mode != "전체 문제 풀기":
                random.shuffle(final_questions)
            st.session_state['quiz_data'] = final_questions
            st.session_state['current_idx'] = 0
            st.session_state['score'] = 0
            st.session_state['quiz_started'] = True
            st.session_state['show_answer'] = False
            st.session_state['user_selection'] = None
            st.rerun()

# --- 퀴즈 진행 화면 ---
else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    if idx >= len(q_list):
        st.balloons()
        st.success(f"🎉 완료! 점수: {st.session_state['score']} / {len(q_list)}")
        if st.button("처음으로"):
            st.session_state['quiz_started'] = False
            st.rerun()
    else:
        # 진행바
        st.progress((idx + 1) / len(q_list))
        st.caption(f"문제 {idx + 1} / {len(q_list)} | 점수: {st.session_state['score']}")
        
        question = q_list[idx]
        
        # 문제 & 보기 박스
        st.markdown(f"""
        <div class="question-box">
            <div class="question-text">Q{question['id']}. {question['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if question.get('context'):
            st.markdown(f'<div class="context-box">{question["context"]}</div>', unsafe_allow_html=True)

        options = question['options']

        # 정답 선택 영역
        if not st.session_state['show_answer']:
            choice = st.radio("정답 선택:", options, index=None, key=f"q_{idx}")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("제출하기 ✅", type="primary", disabled=(choice is None)):
                st.session_state['user_selection'] = choice
                st.session_state['show_answer'] = True
                st.rerun()
        
        # 결과 화면
        else:
            user_choice = st.session_state['user_selection']
            try:
                user_idx = options.index(user_choice) + 1
            except:
                user_idx = -1
            
            correct_idx = question['answer']
            correct_text = options[correct_idx - 1]

            if user_idx == correct_idx:
                st.success("⭕ 정답입니다!")
                if 'processed' not in st.session_state:
                    st.session_state['score'] += 1
                    st.session_state['processed'] = True
            else:
                st.error(f"❌ 땡! (선택: {user_idx}번)")
                if 'processed' not in st.session_state:
                    save_wrong_note(question)
                    st.session_state['processed'] = True
            
            st.markdown(f"**👉 정답: {correct_idx}번 ({correct_text})**")
            st.markdown(f'<div class="explanation-box"><strong>💡 해설</strong><br>{question["explanation"]}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("다음 문제 👉", type="primary"):
                st.session_state['current_idx'] += 1
                st.session_state['show_answer'] = False
                st.session_state['user_selection'] = None
                if 'processed' in st.session_state:
                    del st.session_state['processed']
                st.rerun()