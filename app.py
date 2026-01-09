import streamlit as st
import json
import os
import random
import re

# ==========================================
# 1. 페이지 설정 및 스타일 (CSS)
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터",
    page_icon="🎓",
    layout="centered"
)

# 커스텀 CSS (디자인 예쁘게 만들기)
st.markdown("""
    <style>
    .question-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    .question-text {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        line-height: 1.6;
    }
    .category-tag {
        background-color: #e8eaf6;
        color: #3f51b5;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 저장 함수
# ==========================================
DB_FILE = "database.json"
WRONG_NOTE_FILE = "wrong_notes.json"

@st.cache_data
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
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
# 3. 세션 상태 관리
# ==========================================
# 세션 변수 초기화 함수
def init_session():
    defaults = {
        'quiz_data': [], 'current_idx': 0, 'score': 0, 
        'quiz_started': False, 'show_answer': False, 
        'user_result': None, 'user_input': None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ==========================================
# 4. 사이드바 (메뉴)
# ==========================================
st.sidebar.header("📚 학습 메뉴")
mode = st.sidebar.radio(
    "모드 선택", 
    ["전체 문제 풀기", "주제별 풀기", "랜덤 30문항 모의고사", "오답 노트 복습"]
)

all_data = load_data()
categories = sorted(list(set([q.get('category', '기타') for q in all_data]))) if all_data else []

selected_category = None
if mode == "주제별 풀기":
    selected_category = st.sidebar.selectbox("주제 선택", categories)

if st.sidebar.button("🔄 처음으로 리셋", use_container_width=True):
    st.session_state['quiz_started'] = False
    st.rerun()

# ==========================================
# 5. 메인 화면 로직
# ==========================================
st.title("💰 투자자산운용사 마스터")

# --- [화면 1] 퀴즈 시작 전 ---
if not st.session_state['quiz_started']:
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=100)
    with col2:
        st.subheader("준비 되셨나요?")
        st.write(f"현재 데이터베이스에 **{len(all_data)}문제**가 있습니다.")
        st.write("이동 중에도 틈틈이 공부해서 합격합시다!")

    final_questions = []
    
    # 데이터 필터링
    if mode == "전체 문제 풀기":
        final_questions = all_data.copy()
    elif mode == "주제별 풀기" and selected_category:
        final_questions = [q for q in all_data if q.get('category') == selected_category]
    elif mode == "랜덤 30문항 모의고사":
        if len(all_data) > 30:
            final_questions = random.sample(all_data, 30)
        else:
            final_questions = all_data.copy()
    elif mode == "오답 노트 복습":
        final_questions = load_wrong_notes()
        if not final_questions:
            st.warning("📝 저장된 오답 노트가 없습니다.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if final_questions:
        btn_text = "🔥 모의고사 시작 (30문항)" if mode == "랜덤 30문항 모의고사" else "🚀 학습 시작하기"
        if st.button(btn_text, type="primary", use_container_width=True):
            if mode != "랜덤 30문항 모의고사":
                random.shuffle(final_questions)
            st.session_state['quiz_data'] = final_questions
            st.session_state['current_idx'] = 0
            st.session_state['score'] = 0
            st.session_state['quiz_started'] = True
            st.session_state['show_answer'] = False
            st.session_state['user_result'] = None
            st.session_state['user_input'] = None
            st.rerun()
    else:
        if mode != "오답 노트 복습":
            st.error("데이터 로드 실패.")

# --- [화면 2] 퀴즈 진행 중 ---
else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    # 상단 진행바
    progress = (idx + 1) / len(q_list)
    st.progress(progress)
    
    # 점수판
    c1, c2, c3 = st.columns(3)
    c1.metric("현재 문제", f"{idx + 1} / {len(q_list)}")
    c2.metric("맞은 개수", f"{st.session_state['score']} 개")
    c3.metric("남은 문제", f"{len(q_list) - (idx + 1)} 개")

    st.markdown("---")

    if idx < len(q_list):
        question = q_list[idx]
        
        # ----------------------------------------
        # 1. 문제 카드 표시 (디자인 개선)
        # ----------------------------------------
        category_text = question.get('category', '공통')
        
        st.markdown(f"""
            <div class="question-box">
                <div class="category-tag">Subject: {category_text}</div>
                <div class="question-text">Q. {question['question']}</div>
            </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------
        # 2. 사용자 입력 영역
        # ----------------------------------------
        if not st.session_state['show_answer']:
            st.markdown("##### 👇 정답을 선택하세요")
            
            # [유형 A] OX 퀴즈
            if question.get('type') == 'OX':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⭕ O (맞음)", use_container_width=True):
                        st.session_state['user_input'] = "O"
                        st.session_state['show_answer'] = True
                        st.rerun()
                with col2:
                    if st.button("❌ X (틀림)", use_container_width=True):
                        st.session_state['user_input'] = "X"
                        st.session_state['show_answer'] = True
                        st.rerun()

            # [유형 B] 빈칸 채우기 (선택형 or 주관식)
            else:
                # (A / B) 패턴 찾기
                matches = re.findall(r'\(([^)]+?)\s*/\s*([^)]+?)\)', question['question'])
                
                if matches:
                    # 선택형 빈칸 (라디오 버튼)
                    user_selections = []
                    for i, match in enumerate(matches):
                        options = [m.strip() for m in match]
                        # 섞어서 보여주기 (옵션) - 원하면 random.shuffle(options)
                        choice = st.radio(f"**[빈칸 {i+1}]** 정답은?", options, horizontal=True, key=f"q_{idx}_{i}")
                        user_selections.append(choice)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("정답 제출하기 📝", type="primary", use_container_width=True):
                        st.session_state['user_input'] = user_selections
                        st.session_state['show_answer'] = True
                        st.rerun()
                else:
                    # 순수 주관식 (생각해보기)
                    with st.expander("힌트 보기 💡"):
                        st.write("문맥을 잘 읽어보세요!")
                    
                    if st.button("정답 확인하기 👀", type="primary", use_container_width=True):
                        st.session_state['user_input'] = "VIEW_ONLY"
                        st.session_state['show_answer'] = True
                        st.rerun()

        # ----------------------------------------
        # 3. 정답 및 해설 표시 (결과 화면)
        # ----------------------------------------
        else:
            is_correct = False
            
            # --- 채점 로직 ---
            if question.get('type') == 'OX':
                real_ans = 'O' if 'O' in question['answer'].upper() else 'X'
                if st.session_state['user_input'] == real_ans:
                    is_correct = True
            
            elif isinstance(st.session_state.get('user_input'), list): # 선택형 빈칸
                real_answers = [ans.strip() for ans in question['answer'].split(',')]
                if len(real_answers) == len(st.session_state['user_input']):
                    if real_answers == st.session_state['user_input']:
                        is_correct = True
            
            elif st.session_state.get('user_input') == "VIEW_ONLY":
                # 주관식은 사용자에게 물어봄
                st.info(f"💡 정답: **{question['answer']}**")
                st.write("본인의 생각과 일치하나요?")
                c1, c2 = st.columns(2)
                if c1.button("🙆‍♂️ 맞음"):
                    st.session_state['user_result'] = 'correct'
                    st.rerun()
                if c2.button("🙅‍♂️ 틀림"):
                    st.session_state['user_result'] = 'wrong'
                    st.rerun()
                
                if st.session_state.get('user_result') == 'correct': is_correct = True
                elif st.session_state.get('user_result') == 'wrong': is_correct = False
                else: st.stop() # 버튼 누르기 전 대기

            # --- 결과 UI ---
            if is_correct:
                st.success("✅ 정답입니다! 훌륭해요!")
            else:
                st.error(f"❌ 아쉽네요. 정답은 [ {question['answer']} ] 입니다.")

            # --- 해설 박스 ---
            with st.container():
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba;">
                    <strong>🧐 상세 해설</strong><br><br>
                    {question['explanation']}
                </div>
                """, unsafe_allow_html=True)

            # --- 점수 반영 및 다음 버튼 ---
            if 'processed' not in st.session_state:
                if is_correct:
                    st.session_state['score'] += 1
                else:
                    save_wrong_note(question)
                st.session_state['processed'] = True
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("다음 문제로 넘어가기 👉", type="primary", use_container_width=True):
                st.session_state['current_idx'] += 1
                st.session_state['show_answer'] = False
                st.session_state['user_input'] = None
                st.session_state['user_result'] = None
                if 'processed' in st.session_state:
                    del st.session_state['processed']
                st.rerun()

    # 퀴즈 종료
    else:
        st.balloons()
        st.markdown("""
            <div style="text-align: center; padding: 50px;">
                <h1>🎉 수고하셨습니다!</h1>
                <h3>최종 점수</h3>
                <h1 style="color: #4CAF50; font-size: 60px;">
                    {score} / {total}
                </h1>
            </div>
        """.format(score=st.session_state['score'], total=len(q_list)), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 다시 풀기", use_container_width=True):
                st.session_state['quiz_started'] = False
                st.rerun()
        with col2:
            st.button("❌ 오답 노트 확인 (준비중)", disabled=True, use_container_width=True)