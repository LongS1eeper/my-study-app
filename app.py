import streamlit as st
import json
import os
import random
import re

# ==========================================
# 1. 설정 및 데이터 로드
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터",
    page_icon="💼",
    layout="centered"
)

# 파일 경로
DB_FILE = "database.json"
WRONG_NOTE_FILE = "wrong_notes.json"

@st.cache_data
def load_data():
    """database.json 파일을 로드합니다."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def load_wrong_notes():
    """오답 노트를 로드합니다."""
    if os.path.exists(WRONG_NOTE_FILE):
        with open(WRONG_NOTE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_wrong_note(question_item):
    """틀린 문제를 오답 노트 파일에 저장합니다."""
    current_notes = load_wrong_notes()
    if not any(q['id'] == question_item['id'] for q in current_notes):
        current_notes.append(question_item)
        with open(WRONG_NOTE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_notes, f, ensure_ascii=False, indent=2)

# ==========================================
# 2. 세션 상태 초기화
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
if 'user_result' not in st.session_state:
    st.session_state['user_result'] = None
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = None

# ==========================================
# 3. 사이드바
# ==========================================
st.sidebar.title("MENU 💼")

# [수정됨] 메뉴에 '랜덤 30문항 모의고사' 추가
mode = st.sidebar.radio(
    "학습 모드 선택", 
    ["전체 문제 풀기", "주제별 풀기", "랜덤 30문항 모의고사", "오답 노트 복습"]
)

all_data = load_data()
categories = sorted(list(set([q.get('category', '기타') for q in all_data]))) if all_data else []

selected_category = None
if mode == "주제별 풀기":
    selected_category = st.sidebar.selectbox("주제 선택", categories)

if st.sidebar.button("초기화 (처음부터 다시)"):
    st.session_state['quiz_started'] = False
    st.rerun()

# ==========================================
# 4. 메인 로직
# ==========================================
st.title("💰 투자자산운용사 핵심 퀴즈")

if not st.session_state['quiz_started']:
    st.info(f"데이터베이스에 총 {len(all_data)}개의 문제가 있습니다.")
    
    final_questions = []
    
    # 모드별 데이터 준비 로직
    if mode == "전체 문제 풀기":
        final_questions = all_data.copy()
        
    elif mode == "주제별 풀기" and selected_category:
        final_questions = [q for q in all_data if q.get('category') == selected_category]
        
    # [추가된 로직] 랜덤 30문항 추출
    elif mode == "랜덤 30문항 모의고사":
        if len(all_data) > 30:
            final_questions = random.sample(all_data, 30)
        else:
            final_questions = all_data.copy() # 30개보다 적으면 전부 다
            
    elif mode == "오답 노트 복습":
        final_questions = load_wrong_notes()
        if not final_questions:
            st.warning("저장된 오답 노트가 없습니다.")
    
    # 시작 버튼
    if final_questions:
        # 문구 다르게 표시
        btn_text = "모의고사 시작! (30문항) ⏱️" if mode == "랜덤 30문항 모의고사" else "학습 시작하기! 🚀"
        
        if st.button(btn_text):
            # 랜덤 모드는 이미 섞여 있지만, 한번 더 섞어줌 (다른 모드들을 위해)
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
            st.error("데이터를 불러오지 못했습니다.")

else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    progress = (idx / len(q_list))
    st.progress(progress)
    st.caption(f"진행률: {idx + 1} / {len(q_list)} (현재 점수: {st.session_state['score']}점)")

    if idx < len(q_list):
        question = q_list[idx]
        
        # --- 문제 표시 ---
        with st.container():
            category_text = question.get('category', '공통 주제')
            st.caption(f"🏷️ 주제: **{category_text}**") 
            
            st.markdown(f"### Q{idx+1}. [{question.get('type', '일반')}]")
            st.markdown(f"#### {question['question']}")
            st.divider()

        # --- 사용자 입력 및 정답 처리 ---
        if not st.session_state['show_answer']:
            
            # 1. OX 문제
            if question.get('type') == 'OX':
                st.markdown("##### 정답을 선택하세요.")
                c1, c2 = st.columns(2)
                if c1.button("⭕ O", use_container_width=True):
                    st.session_state['user_input'] = "O"
                    st.session_state['show_answer'] = True
                    st.rerun()
                if c2.button("❌ X", use_container_width=True):
                    st.session_state['user_input'] = "X"
                    st.session_state['show_answer'] = True
                    st.rerun()

            # 2. 빈칸 문제 (선택형 vs 일반형 자동 감지)
            else:
                matches = re.findall(r'\(([^)]+?)\s*/\s*([^)]+?)\)', question['question'])
                
                if matches:
                    st.markdown("##### 빈칸에 들어갈 말을 선택하세요.")
                    user_selections = []
                    
                    for i, match in enumerate(matches):
                        options = [m.strip() for m in match]
                        choice = st.radio(f"빈칸 {i+1}", options, horizontal=True, key=f"q_{idx}_{i}")
                        user_selections.append(choice)
                    
                    if st.button("정답 확인 🎯", type="primary", use_container_width=True):
                        st.session_state['user_input'] = user_selections
                        st.session_state['show_answer'] = True
                        st.rerun()
                
                else:
                    st.markdown("##### 정답을 떠올려보세요.")
                    if st.button("정답 확인하기 👀", type="primary", use_container_width=True):
                        st.session_state['user_input'] = "VIEW_ONLY"
                        st.session_state['show_answer'] = True
                        st.rerun()

        # --- 결과 확인 화면 ---
        else:
            is_correct = False
            
            # 1. OX 채점
            if question.get('type') == 'OX':
                real_ans = 'O' if 'O' in question['answer'].upper() else 'X'
                if st.session_state['user_input'] == real_ans:
                    is_correct = True
                    st.success("✅ 정답입니다!")
                else:
                    is_correct = False
                    st.error(f"❌ 오답입니다! 정답: {real_ans}")

            # 2. 선택형 빈칸 채점
            elif isinstance(st.session_state.get('user_input'), list):
                real_answers = [ans.strip() for ans in question['answer'].split(',')]
                user_answers = st.session_state['user_input']
                
                if len(real_answers) == len(user_answers):
                    if real_answers == user_answers:
                        is_correct = True
                        st.success("✅ 정답입니다!")
                    else:
                        is_correct = False
                        st.error(f"❌ 틀렸습니다. 정답: {question['answer']}")
                else:
                    st.warning("⚠️ 자동 채점 불가")
                    st.info(f"정답: {question['answer']}")
                    is_correct = False

            # 3. 일반 주관식 (자가 채점)
            else:
                st.info(f"💡 정답: **{question['answer']}**")
                st.markdown("본인의 답과 일치하나요?")
                c1, c2 = st.columns(2)
                if c1.button("🙆‍♂️ 맞음"):
                    st.session_state['user_result'] = 'correct'
                    st.rerun()
                if c2.button("🙅‍♂️ 틀림"):
                    st.session_state['user_result'] = 'wrong'
                    st.rerun()
                
                if st.session_state.get('user_result') == 'correct':
                    is_correct = True
                elif st.session_state.get('user_result') == 'wrong':
                    is_correct = False
            
            # 해설 및 점수 처리
            if question.get('type') != '빈칸' or isinstance(st.session_state.get('user_input'), list) or st.session_state.get('user_result'):
                
                st.markdown(f"**[해설]** {question['explanation']}")
                
                if 'processed' not in st.session_state:
                    if is_correct:
                        st.session_state['score'] += 1
                    else:
                        save_wrong_note(question)
                    st.session_state['processed'] = True
                
                st.markdown("---")
                if st.button("다음 문제 👉", type="primary", use_container_width=True):
                    st.session_state['current_idx'] += 1
                    st.session_state['show_answer'] = False
                    st.session_state['user_input'] = None
                    st.session_state['user_result'] = None
                    if 'processed' in st.session_state:
                        del st.session_state['processed']
                    st.rerun()

    else:
        st.balloons()
        st.success("🎉 학습 종료!")
        st.markdown(f"### 최종 점수: {st.session_state['score']} / {len(q_list)}")
        if st.button("처음으로"):
            st.session_state['quiz_started'] = False
            st.rerun()