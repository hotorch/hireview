import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import traceback
from streamlit_chat import message
import openai
import os
from utils.util import get_image_base64,read_prompt_from_txt,local_css
from PIL import Image
from src.chat import (make_initial_args,
                      save_conversation_history,
                      preprocessing_conversation_history,
                      ggori_chat_with_gpt3)
st.session_state.logger.info("start")
NEXT_PAGE = 'generate_feedback'

#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG
local_css("css/background.css")
local_css("css/3_interview.css")

## set variables
ALL_CONVERSATION_SAVE_DIR = os.path.join(st.session_state["save_dir"],'3_interview_all_conversation_histories.txt')

## load image
fav_image = Image.open(st.session_state.FAV_IMAGE_PATH)
logo_image = get_image_base64(st.session_state.LOGO_IMAGE_PATH)

## read prompt
sys_prompt = read_prompt_from_txt("./data/prompt/sys_prompt.txt")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True)

## set icon
chat_icon_user = st.session_state['USER_ICON']
chat_icon_interviewer = st.session_state['INTERVIEWER_ICON']
st.session_state.logger.info("set user , interview icon")

## make initial args
st.session_state.main_question = {'프로그래밍 능력': '지원자가 사용한 프레임워크나 라이브러리 중 가장 자신 있는 것은 무엇인지 알려주세요', '알고리즘 이해': '지원자가 알고리즘을 선택하고 적용하는 기준이 무엇인지 알려주세요', '커뮤니케이션 능력': '프로젝트에서 팀원들과의 협업 방식에 대해 설명해주세요', '비즈니스 이해': '지원자가 개발한 서비스의 수익 모델이나 비즈니스 모델에 대해 알려주세요', '클라우드 서비스 이해': '클라우드 환경에서 모델을 배포하거나 서비스를 구축한 경험이 있는지 알려주세요', '통계학 이해': '지원자가 사용한 통계 모델의 원리와 적용 방법을 설명해주세요'}
st.session_state.selected_job = "AI 엔지니어"
initial_questions,whole_counts,initial_args_lst = make_initial_args(st.session_state.main_question.values(), 
                                                                    st.session_state.user_name)
st.session_state.logger.info("make initial args")

## args to session state
for args in initial_args_lst:
    args_key = list(args.keys())[0]                 # args key
    args_value = list(args.values())[0]             # args value
    if args_key not in st.session_state:            # session state에 초기값이 없을 경우애만 값 세팅
        st.session_state[args_key] = args_value

## 전체 문장 수, 18이 될 예정
st.session_state.whole_conversation_counts = st.session_state.max_conversation_count*whole_counts

## title
st.title("AI 면접 대화")
st.session_state.logger.info(f"Total 진행 현황: {st.session_state.total_question_count}/18")
st.session_state.logger.info(f"Total 진행 현황: {st.session_state.conversation_count}/3")

## interview progress bar
interview_progress = st.empty() # 진행률
progress_rate = st.session_state.total_question_count/18 # 진행률 계산
with interview_progress:
    progress_bar = st.progress(progress_rate, text = f"진행률 {int(progress_rate*100)}%")

##
for message in st.session_state.messages:
    if message["role"]=='user':
        role, content = message["role"], message["content"]
        icon = chat_icon_user
    else:
        role, content = message["role"], message["content"]
        icon = chat_icon_interviewer
    with st.chat_message(role,avatar=icon):
        st.markdown(content)

#################### 1. User Input 부분 ##############################
# Accept user input, 새로운 Input을 받음
# 첫번째 질문인 경우, user 입력은 Pass
if user_message := st.chat_input("입력된 대화문이 너무 짧을 경우, 원활한 면접이 진행되지 않을 수 있습니다!"):
    if st.session_state.conversation_count == 0:
        pass
    else:
    # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_message})
    # Display user message in chat message container
        with st.chat_message("user",avatar = st.session_state.USER_ICON):
            st.markdown(user_message)
        # Count args 업데이트
        st.session_state.total_question_count += 1  # 전체 질문 +1
        st.session_state.conversation_count += 1    # 대질문 별 질문 +1
#################### User Input 부분 End ####################

#################### 2. Assistant Output 부분 ####################
# Display assistant response in chat message container
with st.chat_message("assistant",avatar=st.session_state.INTERVIEWER_ICON):
# with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    # D) 전체 AI 상담이 끝났을 경우
    if st.session_state.total_question_count > st.session_state.whole_conversation_counts: # 전체 질문이 다 끝나면 무조건 종료시킴
        print(f'# D) 전체 AI 상담이 끝났을 경우')
        time.sleep(2) # 바로 넘어가는게 자연스럽지 못해서 추가
        assistant_response = "고생하셨습니다. 전체 AI 면접을 종료합니다. 잠시후 피드백 페이지로 이동합니다."
        st.session_state.conversation_history.extend([{"role": "user", "content": user_message} 
                                                    ,{"role": "assistant", "content": assistant_response}])
        # 해당 대화까지 내용 저장(리스트로 묶어서)
        st.session_state.all_conversation_history.append(st.session_state.conversation_history[1:]) # 시스템 프롬프트는 빠짐
    # A) 대질문의 첫번재 질문인 경우
    elif st.session_state.conversation_count == 0:
        print(' A) 대질문의 첫번재 질문인 경우')
        Prompts = sys_prompt.replace("{selected_job}",str(st.session_state.selected_job))
        initial_question = initial_questions[st.session_state.initial_questions_idx] # 대질문 중 해당 질문 세팅
        st.session_state.conversation_history = [ {"role": "system", "content": Prompts},
                                                {"role": "assistant", "content": initial_question}
                                                ]
        assistant_response = initial_question
        # Count args 업데이트
        st.session_state.total_question_count += 1  # 전체 질문 +1
        st.session_state.conversation_count += 1    # 대질문 별 질문 +1
    # B) 진행 횟수가 max_conversation_count 보다 작을 경우
    elif st.session_state.conversation_count <= st.session_state.max_conversation_count:
        print('# B) 진행 횟수가 max_conversation_count과 같거나 작은 경우')
        assistant_response, st.session_state.conversation_history = ggori_chat_with_gpt3(user_message
                                                                                        , st.session_state.conversation_history
                                                                                        , st.session_state.conversation_count
                                                                                        , st.session_state.max_conversation_count
                                                                                        )
    # C) 진행 횟수가 max_conversation_count 보다 넘어간 경우
    elif st.session_state.conversation_count > st.session_state.max_conversation_count:
        print(f">>> 꼬리질문 끝!")
        assistant_response, st.session_state.conversation_history = ggori_chat_with_gpt3(user_message
                                                                                        , st.session_state.conversation_history
                                                                                        , st.session_state.conversation_count
                                                                                        , st.session_state.max_conversation_count
                                                                                        )
        # 해당 대화까지 내용 저장(리스트로 묶어서)
        st.session_state.all_conversation_history.append(st.session_state.conversation_history[1:]) # 시스템 프롬프트 빠짐

        # Count args 업데이트
        st.session_state.total_question_count -= 1  # 꼬리질문 마지막 파트는 건수로 세지 않음, -1
        st.session_state.initial_questions_idx += 1 # 질문 Index 하나 넘김
        st.session_state.conversation_count = 0     # 대질문 별 질문 초기화
        st.session_state.conversation_history = []  # 대질문 별 질문 히스토리 초기화

        # 신규 질문 append
        assistant_response += f"\n\n 다음 질문 준비가 되었으면 '다음' 이라고 입력해주세요."

    # Simulate stream of response with milliseconds delay, 화면 내 타이핑처럼 print되게 하는 장치
    for chunk in assistant_response.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    # assistant 히스토리 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})

## 로컬 디렉토리에 대화문 전문 저장, 전체 대화 내용들을 구분자로 나누어 저장함
## + 텍스트 내 이슈가 될만한 pattern은 삭제처리
all_conversation_history = preprocessing_conversation_history(st.session_state.all_conversation_history)

## save
save_conversation_history(ALL_CONVERSATION_SAVE_DIR,all_conversation_history)
st.session_state.all_conversation_history = load_conversation(ALL_CONVERSATION_SAVE_DIR)
## 다음 세션으로 넘어감
if st.session_state.total_question_count > st.session_state.whole_conversation_counts: # 하드코딩 값 수정 필요
    time.sleep(3) # 바로 넘어가는게 자연스럽지 못해서 추가
    # 필요사항 따라 버튼 클릭시 안내 문구 생성
    switch_page(NEXT_PAGE)