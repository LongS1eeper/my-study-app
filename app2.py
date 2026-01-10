import streamlit as st
import json
import os
import random

# ==========================================
# 1. 페이지 설정 및 스타일 (CSS)
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터",
    page_icon="🎓",
    layout="centered"
)

# 디자인 커스텀 (가독성 향상)
st.markdown("""
    <style>
    .question-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .question-text {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .context-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #bbdefb;
        margin-bottom: 15px;
        font-size: 15px;
        color: #0d47a1;
        white-space: pre-line; /* 줄바꿈 보존 */
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .explanation-box {
        background-color: #fff3cd; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #ffeeba;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 저장 함수
# ==========================================
# 파일명을 database2.json으로 변경했습니다.
DB_FILE = "database2.json"
WRONG_NOTE_FILE = "wrong_notes.json"

@st.cache_data
def load_data():
    if not os.path.exists(DB_FILE):
        st.error(f"❌ {DB_FILE} 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
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
    # 이미 오답노트에 있는 문제인지 확인 (ID 기준)
    if not any(q['id'] == question_item['id'] for q in current_notes):
        current_notes.append(question_item)
        with open(WRONG_NOTE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_notes, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. 세션 상태 초기화
# ==========================================
if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []
if 'current_idx' not in st.session_state:
    st.session_state['current_idx'] = 0
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'quiz_started' not in st.session_state:
    st.session_state['quiz_started'] = False
if 'show_answer' not in st.session_state:
    st.session_state['show_answer'] = False
if 'user_selection' not in st.session_state:
    st.session_state['user_selection'] = None

# ==========================================
# 4. 사이드바 (메뉴 구성)
# ==========================================
st.sidebar.header("📚 학습 메뉴")
mode = st.sidebar.radio(
    "모드 선택", 
    ["전체 문제 풀기", "랜덤 20문항 모의고사", "오답 노트 복습"]
)

# 데이터 로드
all_data = load_data()

# 리셋 버튼
if st.sidebar.button("🔄 처음으로 리셋", type="primary"):
    st.session_state['quiz_started'] = False
    st.rerun()

# 오답노트 개수 표시
wrong_data = load_wrong_notes()
if wrong_data:
    st.sidebar.info(f"📝 현재 오답노트에 **{len(wrong_data)}**문제가 있습니다.")

# ==========================================
# 5. 메인 화면 로직
# ==========================================
st.title("💰 투자자산운용사 마스터")

# --- [화면 1] 퀴즈 시작 전 대기 화면 ---
if not st.session_state['quiz_started']:
    st.markdown("---")
    st.subheader("학습 준비")
    st.write(f"현재 데이터베이스에 총 **{len(all_data)}**개의 문제가 등록되어 있습니다.")
    
    # 문제 데이터 준비 로직
    final_questions = []
    
    if mode == "전체 문제 풀기":
        final_questions = all_data.copy()
        st.caption("모든 문제를 순서대로 풉니다.")
        
    elif mode == "랜덤 20문항 모의고사":
        if len(all_data) > 20:
            final_questions = random.sample(all_data, 20)
        else:
            final_questions = all_data.copy()
        st.caption("전체 데이터 중 20문제를 무작위로 뽑아 시험을 봅니다.")
        
    elif mode == "오답 노트 복습":
        final_questions = wrong_data
        if not final_questions:
            st.warning("저장된 오답 문제가 없습니다.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if final_questions:
        if st.button("🚀 문제 풀기 시작", type="primary", use_container_width=True):
            # 모드가 전체 풀기가 아닐 경우 섞어줌 (전체 풀기는 번호순 유지가 나을 수 있음)
            if mode == "랜덤 20문항 모의고사" or mode == "오답 노트 복습":
                random.shuffle(final_questions)
            
            st.session_state['quiz_data'] = final_questions
            st.session_state['current_idx'] = 0
            st.session_state['score'] = 0
            st.session_state['quiz_started'] = True
            st.session_state['show_answer'] = False
            st.session_state['user_selection'] = None
            st.rerun()

# --- [화면 2] 퀴즈 진행 화면 ---
else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    # 1. 퀴즈가 끝났는지 확인
    if idx >= len(q_list):
        st.balloons()
        st.markdown(f"""
            <div style="text-align: center; padding: 40px; background-color: #f0f2f6; border-radius: 10px;">
                <h2>🎉 학습 완료!</h2>
                <p style="font-size: 20px;">총 <strong>{len(q_list)}</strong>문제 중</p>
                <h1 style="color: #4CAF50; font-size: 50px;">{st.session_state['score']}문제 정답</h1>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("처음으로 돌아가기", use_container_width=True):
            st.session_state['quiz_started'] = False
            st.rerun()
            
    else:
        # 진행 상태바
        progress = (idx + 1) / len(q_list)
        st.progress(progress)
        
        # 상단 정보 (문제 번호 / 점수)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.caption(f"Question {idx + 1} / {len(q_list)}")
        with col3:
            st.caption(f"Score: {st.session_state['score']}")

        question = q_list[idx]
        
        # -------------------------------------------------------
        # [UI] 문제 표시 영역
        # -------------------------------------------------------
        # 1. 문제 텍스트
        st.markdown(f"""
        <div class="question-box">
            <div class="question-text">Q{question['id']}. {question['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 보기(Context) 박스 (데이터에 context가 있을 경우만 표시)
        if question.get('context'):
            st.markdown(f"""
            <div class="context-box">
                {question['context']}
            </div>
            """, unsafe_allow_html=True)

        # -------------------------------------------------------
        # [UI] 답안 선택 영역
        # -------------------------------------------------------
        # database2.json은 options가 리스트 형태입니다.
        options = question['options']
        
        # 정답 제출 전
        if not st.session_state['show_answer']:
            # 라디오 버튼으로 보기 출력
            # key를 unique하게 주어야 에러가 안 납니다.
            choice = st.radio(
                "정답을 선택하세요:", 
                options, 
                index=None, 
                key=f"radio_{idx}"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 선택 후 제출 버튼 활성화
            if st.button("정답 확인하기 ✅", type="primary", use_container_width=True, disabled=(choice is None)):
                st.session_state['user_selection'] = choice
                st.session_state['show_answer'] = True
                st.rerun()

        # -------------------------------------------------------
        # [UI] 결과 및 해설 영역
        # -------------------------------------------------------
        else:
            # 사용자가 선택한 값
            user_choice = st.session_state['user_selection']
            
            # 정답 인덱스 찾기 (JSON answer는 1부터 시작하는 정수임)
            # options 리스트에서 사용자가 선택한 문자열의 인덱스(0부터 시작)를 구하고 +1
            try:
                user_idx = options.index(user_choice) + 1
            except ValueError:
                user_idx = -1
            
            correct_idx = question['answer'] # 정답 번호 (1, 2, 3, 4)
            correct_text = options[correct_idx - 1] # 정답 텍스트

            # 정오답 판별
            if user_idx == correct_idx:
                st.success("⭕ 정답입니다!")
                if 'processed' not in st.session_state: # 점수 중복 반영 방지
                    st.session_state['score'] += 1
                    st.session_state['processed'] = True
            else:
                st.error(f"❌ 틀렸습니다. (선택: {user_idx}번)")
                # 틀리면 오답노트에 자동 저장
                if 'processed' not in st.session_state:
                    save_wrong_note(question)
                    st.session_state['processed'] = True

            # 정답 및 해설 표시
            st.markdown(f"**👉 정답: {correct_idx}번 ({correct_text})**")
            
            st.markdown(f"""
            <div class="explanation-box">
                <strong>📝 상세 해설</strong><br><br>
                {question['explanation']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 다음 문제 버튼
            if st.button("다음 문제 👉", type="primary", use_container_width=True):
                st.session_state['current_idx'] += 1
                st.session_state['show_answer'] = False
                st.session_state['user_selection'] = None
                if 'processed' in st.session_state:
                    del st.session_state['processed']
                st.rerun()