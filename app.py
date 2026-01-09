import streamlit as st
import json
import os
import random

# ==========================================
# 1. 설정 및 데이터 로드
# ==========================================
st.set_page_config(
    page_title="투자자산운용사 마스터",
    page_icon="💼",
    layout="centered"
)

# 파일 경로 (같은 폴더에 database.json이 있어야 함)
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
    # 중복 확인 (ID 기준)
    if not any(q['id'] == question_item['id'] for q in current_notes):
        current_notes.append(question_item)
        with open(WRONG_NOTE_FILE, "w", encoding="utf-8") as f:
            json.dump(current_notes, f, ensure_ascii=False, indent=2)

def clear_wrong_notes():
    """오답 노트 초기화"""
    if os.path.exists(WRONG_NOTE_FILE):
        os.remove(WRONG_NOTE_FILE)

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
    st.session_state['show_answer'] = False  # 정답 확인 상태
if 'user_result' not in st.session_state:
    st.session_state['user_result'] = None   # 사용자의 O/X 선택 결과

# ==========================================
# 3. 사이드바 (메뉴 및 필터)
# ==========================================
st.sidebar.title("MENU 💼")
mode = st.sidebar.radio("학습 모드 선택", ["전체 문제 풀기", "주제별 풀기", "오답 노트 복습"])

# 전체 데이터 로드
all_data = load_data()

# 카테고리 추출
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

# 퀴즈 시작 전 화면
if not st.session_state['quiz_started']:
    st.info(f"총 {len(all_data)}개의 문제가 준비되어 있습니다.")
    
    # 문제 데이터 필터링 및 셔플
    final_questions = []
    if mode == "전체 문제 풀기":
        final_questions = all_data.copy()
    elif mode == "주제별 풀기" and selected_category:
        final_questions = [q for q in all_data if q.get('category') == selected_category]
    elif mode == "오답 노트 복습":
        final_questions = load_wrong_notes()
        if not final_questions:
            st.warning("저장된 오답 노트가 없습니다.")
    
    if final_questions:
        if st.button("학습 시작하기! 🚀"):
            random.shuffle(final_questions)
            st.session_state['quiz_data'] = final_questions
            st.session_state['current_idx'] = 0
            st.session_state['score'] = 0
            st.session_state['quiz_started'] = True
            st.session_state['show_answer'] = False
            st.session_state['user_result'] = None
            st.rerun()
    else:
        if mode != "오답 노트 복습":
            st.error("데이터를 불러오지 못했습니다. database.json 파일을 확인해주세요.")

# 퀴즈 진행 화면
else:
    q_list = st.session_state['quiz_data']
    idx = st.session_state['current_idx']
    
    # 진행 상황 표시
    progress = (idx / len(q_list))
    st.progress(progress)
    st.caption(f"진행률: {idx + 1} / {len(q_list)} (현재 점수: {st.session_state['score']}점)")

    # 퀴즈가 끝났는지 확인
    if idx < len(q_list):
        question = q_list[idx]
        
        # --- 문제 표시 카드 ---
        with st.container():
            st.markdown(f"### Q{idx+1}. [{question.get('type', '일반')}]")
            st.markdown(f"#### {question['question']}")
            st.divider()

        # --- 정답 확인 전 (사용자 입력) ---
        if not st.session_state['show_answer']:
            st.markdown("##### 정답을 생각하고 버튼을 누르세요.")
            
            # OX 문제일 경우: 즉시 정답 체크
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
            
            # 빈칸/주관식 문제일 경우: 정답 확인 후 자가 채점 (이동 중 편의성)
            else:
                if st.button("정답 확인하기 👀", type="primary", use_container_width=True):
                    st.session_state['user_input'] = "VIEW" # 단순 확인용
                    st.session_state['show_answer'] = True
                    st.rerun()

        # --- 정답 확인 후 (결과 및 해설 표시) ---
        else:
            # 정답 판별 로직
            is_correct = False
            
            # OX 문제 자동 채점
            if question.get('type') == 'OX':
                # 데이터베이스 정답에서 'O', 'X' 문자만 추출해서 비교
                real_ans = 'O' if 'O' in question['answer'].upper() else 'X'
                if st.session_state['user_input'] == real_ans:
                    is_correct = True
                    st.success("✅ 정답입니다!")
                else:
                    is_correct = False
                    st.error("❌ 오답입니다!")
            
            # 빈칸 문제는 사용자에게 채점 권한 위임
            else:
                st.info(f"💡 정답: **{question['answer']}**")
                st.markdown("본인이 생각한 답과 일치하나요?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🙆‍♂️ 맞았습니다!"):
                        st.session_state['user_result'] = 'correct'
                        st.rerun()
                with col2:
                    if st.button("🙅‍♂️ 틀렸습니다"):
                        st.session_state['user_result'] = 'wrong'
                        st.rerun()

                # 자가 채점 결과 처리
                if st.session_state.get('user_result') == 'correct':
                    is_correct = True
                    st.success("잘 하셨습니다! 👍")
                elif st.session_state.get('user_result') == 'wrong':
                    is_correct = False
                    st.error("오답 노트에 저장됩니다. 📝")

            # 해설 표시 (OX는 자동 표시, 빈칸은 자가채점 버튼 누른 후 표시)
            if question.get('type') == 'OX' or st.session_state.get('user_result'):
                st.markdown(f"**[해설]** {question['explanation']}")
                
                # 점수 반영 및 오답 저장 (한 번만 실행되도록 제어)
                if 'processed' not in st.session_state:
                    if is_correct:
                        st.session_state['score'] += 1
                    else:
                        save_wrong_note(question)
                    st.session_state['processed'] = True

                st.markdown("---")
                # 다음 문제 버튼
                if st.button("다음 문제로 👉", type="primary", use_container_width=True):
                    st.session_state['current_idx'] += 1
                    st.session_state['show_answer'] = False
                    st.session_state['user_result'] = None
                    if 'processed' in st.session_state:
                        del st.session_state['processed']
                    st.rerun()

    else:
        # 모든 문제 종료
        st.balloons()
        st.success("🎉 모든 문제를 다 푸셨습니다!")
        st.markdown(f"### 최종 점수: {st.session_state['score']} / {len(q_list)}")
        
        if st.button("다시 처음으로"):
            st.session_state['quiz_started'] = False
            st.rerun()