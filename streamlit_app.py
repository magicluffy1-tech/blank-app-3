import streamlit as st
import random
import string
from datetime import datetime, timedelta

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Gems의 지식 마켓 플레이스",
    page_icon="💎",
    layout="wide"
)

# --- 상태 관리 (State Management) ---
def initialize_app_state():
    """앱의 모든 세션 상태를 한번에 초기화합니다."""
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'login'
    if 'market_info' not in st.session_state:
        st.session_state.market_info = {}
    if 'group_submissions' not in st.session_state:
        st.session_state.group_submissions = {}
    if 'current_student' not in st.session_state:
        st.session_state.current_student = {
            "name": None,
            "group": None,
            "notes": {}
        }
    st.session_state.initialized = True

# --- 헬퍼 함수 (Helper Functions) ---
def generate_access_code(length=4):
    """KM-XXXX 형태의 고유 접속 코드를 생성합니다."""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"KM-{code}"

def reset_to_login():
    """모든 상태를 초기화하고 로그인 화면으로 돌아갑니다."""
    st.session_state.app_mode = 'login'
    st.session_state.market_info = {}
    st.session_state.group_submissions = {}
    st.session_state.current_student = { "name": None, "group": None, "notes": {} }

# --- 교사 모드 (Teacher Mode) ---
def teacher_mode():
    """교사가 지식 시장을 개설하고 관리하는 전체 UI를 담당합니다."""
    st.header("👨‍🏫 교사 모드: 지식 마켓 플레이스 관리", divider='rainbow')

    if not st.session_state.market_info.get('is_open', False):
        st.subheader("1. 새로운 마켓 생성하기")
        with st.form("new_market_form"):
            st.write("수업명, 조 이름, 각 조의 전문가 주제를 입력해주세요.")
            class_name = st.text_input("수업명", "5학년 1학기 사회 - 우리 역사의 시작")
            cols = st.columns(2)
            group_names_input = cols[0].text_input("조 이름 (쉼표로 구분)", "A조, B조, C조")
            group_topics_input = cols[1].text_input("전문가 주제 (쉼표로 구분)", "고구려, 백제, 신라")
            submitted = st.form_submit_button("🚀 마켓 개설하기", type="primary", use_container_width=True)

            if submitted:
                group_names = [name.strip() for name in group_names_input.split(',')]
                group_topics = [topic.strip() for topic in group_topics_input.split(',')]
                if group_names and group_topics and len(group_names) == len(group_topics):
                    st.session_state.market_info = {
                        'class_name': class_name,
                        'access_code': generate_access_code(),
                        'groups': {name: topic for name, topic in zip(group_names, group_topics)},
                        'group_order': group_names,
                        'is_open': True,
                        'current_phase': 1,
                        'current_round': 0
                    }
                    st.session_state.group_submissions = {
                        name: {
                            'phase1_text': '', 'phase1_image': None, 'phase1_submitted': False,
                            'phase3_report': '', 'phase3_submitted': False
                        } for name in group_names
                    }
                    st.success("지식 마켓이 성공적으로 개설되었습니다!")
                    st.rerun()
                else:
                    st.error("조 이름과 전문가 주제의 개수를 동일하게 맞춰주세요.")
    else:
        info = st.session_state.market_info
        st.subheader(f"📊 '{info['class_name']}' 대시보드")
        st.info(f"**학생 접속 코드: `{info['access_code']}`**")
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.markdown("#### ✅ 조별 진행 상황")
            progress_data = []
            for group_name in info['group_order']:
                submission = st.session_state.group_submissions[group_name]
                p1_status = "✅ 완료" if submission['phase1_submitted'] else "⏳ 대기중"
                p3_status = "✅ 제출" if submission['phase3_submitted'] else "⏳ 미제출"
                progress_data.append({
                    "조 이름": group_name, "전문가 주제": info['groups'][group_name],
                    "설명 자료 준비": p1_status, "최종 보고서": p3_status
                })
            st.dataframe(progress_data, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("#### 🎮 수업 단계 제어")
            if info['current_phase'] == 1:
                st.write("**현재 단계:** 1. 우리 조 전문가 되기")
                if st.button("시장 둘러보기 시작 (Phase 2)", type="primary"):
                    st.session_state.market_info['current_phase'] = 2
                    st.session_state.market_info['current_round'] = 1
                    st.rerun()
            elif info['current_phase'] == 2:
                st.write(f"**현재 단계:** 2. 지식 시장 둘러보기 ({info['current_round']} 라운드)")
                num_groups = len(info['group_order'])
                if info['current_round'] < num_groups - 1:
                    if st.button(f"{info['current_round'] + 1} 라운드 시작", type="primary"):
                        st.session_state.market_info['current_round'] += 1
                        st.rerun()
                else:
                    st.write("모든 라운드가 종료되었습니다.")
                if st.button("결과물 정리 시작 (Phase 3)"):
                    st.session_state.market_info['current_phase'] = 3
                    st.session_state.market_info['current_round'] = 0
                    st.rerun()
            elif info['current_phase'] == 3:
                st.write("**현재 단계:** 3. 우리 조 지식 완성하기")
                st.success("학생들이 최종 보고서를 작성하고 있습니다.")
        st.divider()
        if st.button("🚨 모든 활동 종료 및 마켓 닫기", type="secondary"):
            reset_to_login()
            st.rerun()

# --- 학생 모드 (Student Mode) ---
def student_mode():
    """학생이 지식 시장에 참여하는 전체 UI를 담당합니다."""
    info = st.session_state.market_info
    student = st.session_state.current_student
    my_group = student['group']
    my_topic = info['groups'][my_group]

    with st.sidebar:
        st.title("💎 나의 정보")
        st.markdown(f"**이름:** {student['name']}")
        st.markdown(f"**소속:** {my_group}")
        st.markdown(f"**우리 조 주제:** {my_topic}")
        st.divider()
        phase_map = {
            1: "Phase 1: 우리 조 전문가 되기 (교사 준비)",
            2: f"Phase 2: 지식 시장 (가르치고 배우기)",
            3: "Phase 3: 우리 조 지식 완성하기 (자료화)"
        }
        st.info(f"**현재 활동**\n\n{phase_map.get(info['current_phase'], '활동 대기중')}")
        if info['current_phase'] == 2 and info['current_round'] > 0:
            st.subheader(f"Round {info['current_round']}")
        st.divider()
        if st.button("처음으로 돌아가기"):
            reset_to_login()
            st.rerun()

    if info['current_phase'] == 1:
        student_phase_1_expert()
    elif info['current_phase'] == 2:
        student_phase_2_market()
    elif info['current_phase'] == 3:
        student_phase_3_report()

def student_phase_1_expert():
    """[Phase 1] 우리 조 전문가 되기 UI (교사 역할 준비)"""
    my_group = st.session_state.current_student['group']
    my_topic = st.session_state.market_info['groups'][my_group]
    submission = st.session_state.group_submissions[my_group]

    st.header(f"Phase 1: 우리는 '{my_topic}' 전문가! 👑 (교사 준비)", divider='rainbow')
    st.info("다른 조 학생들을 가르칠 '교과서'를 만든다고 생각하고 설명 자료를 만들어주세요.")

    if submission['phase1_submitted']:
        st.success("우리 조 설명 자료 제출 완료! 교사가 다음 단계를 시작할 때까지 기다려주세요.")
        st.markdown("---")
        st.markdown("#### 최종 제출된 우리 조 자료")
        st.text_area("핵심 내용", value=submission['phase1_text'], height=200, disabled=True)
        if submission['phase1_image']:
            st.image(submission['phase1_image'], caption="업로드한 이미지")
    else:
        with st.form("expert_material_form"):
            text_content = st.text_area("핵심 내용 입력창 ✍️", placeholder=f"{my_topic}의 특징, 중요한 사건 등을 정리해보세요.", height=250)
            image_content = st.file_uploader("이미지/자료 업로드 🖼️", type=['png', 'jpg', 'jpeg'])
            submitted = st.form_submit_button("우리 조 자료 제출하기", type="primary", use_container_width=True)
            if submitted:
                if not text_content:
                    st.warning("핵심 내용은 반드시 입력해야 합니다.")
                else:
                    st.session_state.group_submissions[my_group]['phase1_text'] = text_content
                    if image_content:
                        st.session_state.group_submissions[my_group]['phase1_image'] = image_content.getvalue()
                    st.session_state.group_submissions[my_group]['phase1_submitted'] = True
                    st.success("자료가 성공적으로 제출되었습니다!")
                    st.rerun()

### --- 코드 수정 핵심 파트 ---
### 기존의 st.columns 대신 st.tabs를 사용하여 '학생'과 '교사' 역할을 명확히 분리합니다.
def student_phase_2_market():
    """[Phase 2] 지식 시장 둘러보기 UI (가르치고 배우기)"""
    info = st.session_state.market_info
    student = st.session_state.current_student
    my_group_name = student['group']
    current_round = info['current_round']

    st.header(f"Phase 2: 지식 시장 둘러보기 👀 (Round {current_round})", divider='rainbow')

    if current_round == 0:
        st.info("아직 시장 둘러보기가 시작되지 않았습니다. 교사의 안내를 기다려주세요.")
        return

    # --- 이번 라운드에 방문할 조와 주제 계산 ---
    my_group_idx = info['group_order'].index(my_group_name)
    num_groups = len(info['group_order'])
    visitor_target_idx = (my_group_idx + current_round) % num_groups
    visitor_target_group = info['group_order'][visitor_target_idx]
    visitor_target_topic = info['groups'][visitor_target_group]
    
    # --- 탭을 이용한 역할 분리 UI ---
    student_tab, teacher_tab = st.tabs(["[학생 역할: 배우러 가기 👨‍🎓]", "[교사 역할: 설명하기 👨‍🏫]"])

    # --- 학생 역할 탭 ---
    with student_tab:
        st.subheader(f"미션: `{visitor_target_group}`에서 '{visitor_target_topic}' 배우기")
        
        target_submission = st.session_state.group_submissions[visitor_target_group]
        
        # 방문할 조의 자료 보여주기
        if not target_submission['phase1_submitted']:
            st.warning(f"{visitor_target_group}에서 아직 설명 자료를 준비 중입니다.")
        else:
            st.markdown(f"#### 🔎 `{visitor_target_group}`의 설명 자료")
            st.text_area("핵심 내용", value=target_submission['phase1_text'], height=200, disabled=True, key=f"note_view_{visitor_target_group}")
            if target_submission['phase1_image']:
                st.image(target_submission['phase1_image'], caption=f"{visitor_target_group}가 업로드한 이미지")
        
        # 배운 내용 기록하기
        st.markdown("---")
        st.markdown("#### ✍️ 나의 배움 기록장")
        note_key = f"note_for_{visitor_target_topic}" # 주제별로 노트 키를 관리
        note_content = st.text_area(
            f"'{visitor_target_topic}'에 대해 배운 점을 이곳에 기록하여 나만의 자료로 만드세요.", 
            height=150, 
            key=note_key,
            value=st.session_state.current_student['notes'].get(visitor_target_topic, "")
        )
        # 입력 내용은 실시간으로 세션 상태에 저장
        st.session_state.current_student['notes'][visitor_target_topic] = note_content

    # --- 교사 역할 탭 ---
    with teacher_tab:
        my_topic = info['groups'][my_group_name]
        st.subheader(f"미션: 우리 조를 방문한 학생에게 '{my_topic}' 설명하기")
        
        my_submission = st.session_state.group_submissions[my_group_name]

        if not my_submission['phase1_submitted']:
            st.error("오류: 우리 조의 설명 자료가 아직 제출되지 않았습니다!")
        else:
            st.markdown("#### 📢 우리 조 설명 자료 (디지털 포스터)")
            st.text_area("핵심 내용", value=my_submission['phase1_text'], height=200, disabled=True, key=f"presenter_view_{my_group_name}")
            if my_submission['phase1_image']:
                st.image(my_submission['phase1_image'], caption="우리 조가 업로드한 이미지")


def student_phase_3_report():
    """[Phase 3] 우리 조 지식 완성하기 UI (자료화)"""
    my_group = st.session_state.current_student['group']
    my_topic = st.session_state.market_info['groups'][my_group]
    submission = st.session_state.group_submissions[my_group]
    student_notes = st.session_state.current_student['notes']

    st.header(f"Phase 3: 우리 조 지식 완성하기 🧠 (나의 자료 만들기)", divider='rainbow')
    st.info("내가 준비한 '교사' 자료와, 친구들에게 배운 '학생' 기록을 합쳐 최종 보고서를 작성하세요.")

    if submission['phase3_submitted']:
        st.success("최종 보고서를 제출 완료했습니다! 수고하셨습니다.")
    else:
        tab1, tab2, tab3 = st.tabs(["[작성] 최종 보고서", "[참고] 우리 조 전문가 자료", "[참고] 나의 배움 기록"])
        with tab1:
            with st.form("final_report_form"):
                report_content = st.text_area("보고서 내용 입력", height=400)
                submitted = st.form_submit_button("우리 조 최종 보고서 제출하기", type="primary", use_container_width=True)
                if submitted:
                    if not report_content:
                        st.warning("보고서 내용을 입력해주세요.")
                    else:
                        st.session_state.group_submissions[my_group]['phase3_report'] = report_content
                        st.session_state.group_submissions[my_group]['phase3_submitted'] = True
                        st.rerun()
        with tab2:
            st.markdown(f"#### 📖 우리 조 전문가 자료 ('{my_topic}')")
            my_submission = st.session_state.group_submissions[my_group]
            st.text_area("핵심 내용", value=my_submission['phase1_text'], height=200, disabled=True, key="ref_p1_text")
            if my_submission['phase1_image']:
                st.image(my_submission['phase1_image'], caption="우리 조가 업로드한 이미지")
        with tab3:
            st.markdown("#### 🗒️ 내가 시장에서 배운 내용")
            if not student_notes:
                st.write("아직 기록된 배움 내용이 없습니다.")
            else:
                for topic, note in student_notes.items():
                    st.text_area(f"'{topic}'에 대한 나의 기록", value=note, disabled=True, key=f"ref_note_{topic}")

# --- 로그인 페이지 (Login Page) ---
def login_page():
    """교사 또는 학생이 앱에 접속하는 초기 화면 UI"""
    st.title("💎 지식 마켓 플레이스")
    st.write("학생이 직접 교사와 학생이 되어 가르치고 배우는 수업 활동을 시작합니다.")
    teacher_tab, student_tab = st.tabs(["👨‍🏫 교사로 시작하기", "👨‍🎓 학생으로 참여하기"])
    with teacher_tab:
        if st.button("교사 모드로 시작하기", type="primary"):
            st.session_state.app_mode = 'teacher'
            st.rerun()
    with student_tab:
        with st.form("student_login_form"):
            access_code_input = st.text_input("접속 코드를 입력하세요 (예: KM-XXXX)")
            student_name_input = st.text_input("이름을 입력하세요")
            if st.session_state.market_info.get('is_open', False):
                market_groups = list(st.session_state.market_info['groups'].keys())
                group_choice = st.selectbox("소속 조를 선택하세요", options=market_groups)
            else:
                st.info("현재 열려있는 지식 마켓이 없습니다.")
                group_choice = None
            login_submitted = st.form_submit_button("마켓 참여하기")
            if login_submitted:
                if not st.session_state.market_info.get('is_open', False):
                    st.error("아직 참여할 수 있는 마켓이 없습니다.")
                elif access_code_input.upper() != st.session_state.market_info.get('access_code'):
                    st.error("접속 코드가 올바르지 않습니다.")
                elif not student_name_input or not group_choice:
                    st.error("이름과 조를 모두 입력하고 선택해주세요.")
                else:
                    st.session_state.app_mode = 'student'
                    st.session_state.current_student['name'] = student_name_input
                    st.session_state.current_student['group'] = group_choice
                    st.rerun()

# --- 메인 실행 로직 (Main Execution Logic) ---
def main():
    if 'initialized' not in st.session_state:
        initialize_app_state()

    if st.session_state.app_mode == 'login':
        login_page()
    elif st.session_state.app_mode == 'teacher':
        teacher_mode()
    elif st.session_state.app_mode == 'student':
        student_mode()

if __name__ == "__main__":
    main()