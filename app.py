import streamlit as st
import json
import os
import random
import re  # 정규표현식 모듈 추가 (괄호 패턴 찾기용)

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

# ==========================================
# 3. 사이드바
# ==========================================
st.sidebar.title("MENU 💼")
mode = st.sidebar.radio("학습 모드 선택", ["전체 문제 풀기", "주제별 풀기", "오답 노트 복습"])

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
    st.info(f"총 {len(all_data)}개의 문제가 준비되어 있습니다.")
    
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
                # 정규표현식으로 (A / B) 형태 찾기
                matches = re.findall(r'\(([^)]+?)\s*/\s*([^)]+?)\)', question['question'])
                
                # 선택형 빈칸이 있는 경우 (예: 기하평균 / 산술평균)
                if matches:
                    st.markdown("##### 빈칸에 들어갈 말을 선택하세요.")
                    user_selections = []
                    
                    # 각 빈칸마다 라디오 버튼 생성
                    for i, match in enumerate(matches):
                        options = [m.strip() for m in match] # ['기하평균', '산술평균']
                        choice = st.radio(f"빈칸 {i+1}", options, horizontal=True, key=f"q_{idx}_{i}")
                        user_selections.append(choice)
                    
                    if st.button("정답 확인 🎯", type="primary", use_container_width=True):
                        st.session_state['user_input'] = user_selections # 리스트로 저장
                        st.session_state['show_answer'] = True
                        st.rerun()
                
                # 일반 빈칸/주관식 문제 (자가 진단)
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
                # DB 정답 가져오기 (콤마로 구분된 문자열 -> 리스트 변환)
                # 예: "기하평균, 산술평균" -> ['기하평균', '산술평균']
                real_answers = [ans.strip() for ans in question['answer'].split(',')]
                user_answers = st.session_state['user_input']
                
                # 개수 맞는지 확인 후 비교
                if len(real_answers) == len(user_answers):
                    # 모든 답이 일치해야 정답
                    if real_answers == user_answers:
                        is_correct = True
                        st.success("✅ 정답입니다!")
                    else:
                        is_correct = False
                        st.error(f"❌ 틀렸습니다. 정답: {question['answer']}")
                else:
                    # DB 정답 개수와 추출된 문제 개수가 다를 경우 (예외 처리)
                    st.warning("⚠️ 문제 형식이 복잡하여 자동 채점이 어렵습니다. 아래 해설을 확인하세요.")
                    st.info(f"정답: {question['answer']}")
                    # 이 경우 틀린 것으로 간주하거나 사용자에게 맡김 (여기선 오답 처리)
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
            
            # 해설 및 점수 처리 (공통)
            # 일반 주관식은 user_result가 결정된 후, 나머지는 바로 표시
            if question.get('type') != '빈칸' or isinstance(st.session_state.get('user_input'), list) or st.session_state.get('user_result'):
                
                st.markdown(f"**[해설]** {question['explanation']}")
                
                # 점수 반영 (중복 방지)
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