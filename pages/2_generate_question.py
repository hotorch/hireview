import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import traceback
import os
import re
import random
from src.generate_question import (generate_llm_sub_chain,
                                   preprocess_questions,
                                   load_user_resume,
                                   save_user_resume)
from utils.util import (
                        read_user_job_info,
                        read_prompt_from_txt,
                        local_css,
                        load_css_as_string)
import base64 # gif 이미지 불러오기
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback
st.session_state.logger.info("start")
NEXT_PAGE = 'interview'

#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG
local_css('css/background.css')
local_css("css/2_generate_question.css")
st.markdown(f"""<style>
                         /* 로딩이미지 */
                         .loading_space {{
                            display : flex;
                            justify-content : center;
                            margin-top : -3rem;
                        }}
                        .loading_space img{{
                            max-width : 70%;
                        }}
                        .loading_text {{
                            /* 광고 들어오면 공간 확보 */
                            padding-top : 4rem;
                            z-index : 99;
                        }}
                        .loading_text p{{
                            font-family : 'Nanumsquare';
                            color:#4C4F6D;
                            font-size:28px ;
                            line-height:1.5;
                            word-break:keep-all;
                            font-weight:700;
                            text-align:center;
                            z-index : 99;
                        }}
                        .dots-container {{
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            height: 100%;
                            width: 100%;
                            padding-top : 2rem;
                            padding-bottom : 5rem;
                            z-index : 99;
                        }}

                        .dot {{
                            z-index : 99;
                            height: 20px;
                            width: 20px;
                            margin-right: 10px;
                            border-radius: 10px;
                            background-color: #b3d4fc;
                            animation: pulse 1.5s infinite ease-in-out;
                        }}
                        .dot:last-child {{
                            margin-right: 0;
                        }}

                        .dot:nth-child(1) {{
                            animation-delay: -0.3s;
                        }}

                        .dot:nth-child(2) {{
                            animation-delay: -0.1s;
                        }}

                        .dot:nth-child(3) {{
                            animation-delay: 0.1s;
                        }}
                        </style>
#             """,  unsafe_allow_html=True)
## set variables
MODEL_NAME = 'gpt-3.5-turbo-16k'
INTERVIEWER_NAME = {
    '0.5' : '혁신수',
    '0.7' : '정의현',
    '0.9' : '조화린'
    }

## set save dir
USER_RESUME_SAVE_DIR = os.path.join(st.session_state["save_dir"],'2_generate_question_user_resume.pdf')
BIG_QUESTION_SAVE_DIR = os.path.join(st.session_state["save_dir"],'2_generate_question_generated_big_question.txt')

## User가 선택한 직무별 [프롬프트 & 핵심역량] 가져오기
job_nm, job_ability = read_user_job_info(st.session_state.job_info,st.session_state.selected_job)
st.session_state.logger.info("read_user_job_info")
st.session_state.logger.info(f"job nm is ... {job_nm}")
st.session_state.logger.info(f"job ability is ... {job_ability}")

## read prompt
prompt1 = read_prompt_from_txt("./data/prompt/big_question_generate_prompt_1.txt")
prompt2 = read_prompt_from_txt("./data/prompt/big_question_generate_prompt_2.txt")
prompt3 = read_prompt_from_txt("./data/prompt/big_question_generate_prompt_3.txt")

# 진행률
progress_holder = st.empty() # 작업에 따라 문구 바뀌는 곳
loading_message = [f"'{INTERVIEWER_NAME[str(st.session_state.temperature)]}' 면접관이 '{st.session_state.user_name}'님의 이력서를 꼼꼼하게 읽고 있습니다. <br> 최대 3분까지 소요될 수 있습니다.",
                f"'{INTERVIEWER_NAME[str(st.session_state.temperature)]}' 면접관이 '{st.session_state.user_name}'님과의 면접을 준비하고 있습니다"]

# 로딩 그림(progress bar)
st.markdown("""<section class="dots-container">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </section>
            """,  
            unsafe_allow_html=True)

## 면접&이력서 팁
## 공간이자 이미지가 들어가면 좋을 것 같은 곳
st.markdown(f'''<div class='loading_space'>
                    <img class='tips' src="data:image/gif;base64,{st.session_state['LOADING_GIF1']}"></div>''',unsafe_allow_html=True)
with progress_holder:
    for i in range(2):
        ### step1 : 대질문 생성 및 추출, step2 : 전처리(time.sleep(3))
        progress_holder.markdown(f'''<div class="loading_text">
                                        <p>{loading_message[i]}</p></div>''', unsafe_allow_html=True)
        if st.session_state.big_q_progress:
            ### 이력서 Pre-process
            st.session_state.logger.info("resume process ")
            ### uploaded_file는 streamlit의 file_uploader에서 반환된 객체
            uploaded_file = st.session_state.uploaded_resume
            ### 저장
            save_user_resume(USER_RESUME_SAVE_DIR,uploaded_file)
            st.session_state.logger.info("save resume")
            ### 불러오기
            user_resume = load_user_resume(USER_RESUME_SAVE_DIR)
            st.session_state.logger.info("user total resume import")
            ### 대질문 프롬프트 만들기
            st.session_state.logger.info("generate big question start")
            ### 모델 세팅
            llm = ChatOpenAI(temperature=st.session_state.temperature
                            , model_name=MODEL_NAME
                            #, openai_api_key=OPENAI_API_KEY
                            )
            st.session_state.logger.info("create llm object")
            ### 1. sub chain 생성

            ### chain 1: input= 대질문 생성 조건  /  output= 모델 이해 여부(실제 결과값에는 활용 X)
            chain_1 = generate_llm_sub_chain(llm, 
                                            prompt1, 
                                            output_key="preprocessed_resume")
            st.session_state.logger.info("create chain_1 object")
            ### chain 2. big_question 이력서 프롬프트 생성
            chain_2 = generate_llm_sub_chain(llm, 
                                            prompt2, 
                                            output_key="generated_big_question_lst")
            st.session_state.logger.info("create chain_2 object")
            ### chain 3. 생성된 질문들을 파악하고 상관성 낮은 역량 6개를 추출함
            chain_3 = generate_llm_sub_chain(llm, 
                                            prompt3,
                                            output_key="core_competencies")
            st.session_state.logger.info("create chain_3 object")
            
            ### setup input/output variables
            input_var_nm = ["job_nm", "job_ability", "user_resume"]
            input_variables = [job_nm, job_ability, user_resume]
            input_variables_dic = dict(zip(input_var_nm, input_variables))
            output_variables = ["preprocessed_resume", "generated_big_question_lst", "core_competencies"]
            st.session_state.logger.info("setup input/output variables")

            ### create SequentialChain
            overall_chain = SequentialChain(
                chains=[chain_1, chain_2, chain_3],
                input_variables=input_var_nm,
                output_variables=output_variables,
                verbose=True
            )
            st.session_state.logger.info("create SequentialChain")
            
            start = time.time()
            with get_openai_callback() as callback:
                result = overall_chain(input_variables_dic)
            end = time.time()
            st.session_state.logger.info(f"generate big question run time is ... {(end-start)/60:.3f} 분 ({(end-start):0.1f}초)")
            ### 3. 결과물 및 Token 사용량 저장
            ### 결과 텍스트 저장
            with open(BIG_QUESTION_SAVE_DIR, 'a', encoding='utf-8') as file:
                file.write(f">>> 교정된 이력서: \n{'='*30}\n{result['preprocessed_resume']}\n{'='*30}\n") # 후에 삭제되어야 함
                file.write(f">>> 생성된 대질문: \n{result['generated_big_question_lst']}\n")
                file.write(f">>> 선택된 핵심 역량: \n{result['core_competencies']}\n")
            st.session_state.logger.info(f"save big question result")
            ### Token 사용량 기록
            st.session_state.logger.info(f"Total tokens used: {callback.total_tokens}")
            st.session_state.logger.info(f"Prompt tokens: {callback.prompt_tokens}") 
            st.session_state.logger.info(f"Completion tokens: {callback.completion_tokens}")

            ### User pdf파일 삭제
            try:
                os.remove(USER_RESUME_SAVE_DIR)
            except Exception as e:
                st.session_state.logger.info(f"User resume delete Error: \n{e}")
                print(">>> User resume delete Error: \n{e}")

            st.session_state.big_q_progress = False ### 대질문 생성 끝
        else :
            ### step2. 질문 다듬고 정리
            ### 3. 생성 질문 전처리
            print('generated_big_question_lst : ',result['generated_big_question_lst'])
            main_question,add_question,core_competencies = preprocess_questions(result)
            st.session_state.logger.info(f"preprocess_questions")
            
            ### 주요 역량 생성
            main_job_ability = ', '.join(core_competencies)

            ### 최종 대질문/추가질문 저장
            with open(BIG_QUESTION_SAVE_DIR, 'a', encoding='utf-8') as file:
                file.write(f">>> 최종 선택 main_question: \n{main_question}\n")
                file.write(f">>> 최종 선택 add_question: \n{add_question}\n")

            ### 다음 세션으로 값 넘기기
            st.session_state.main_question = main_question
            st.session_state.add_question = add_question
            st.session_state.main_job_ability = main_job_ability
            st.session_state.logger.info(f"main_question : {main_question}")
            st.session_state.logger.info(f"add_question: {add_question}") 
            st.session_state.logger.info(f"main_job_ability: {main_job_ability}")
            time.sleep(3)
            ####
            switch_page(NEXT_PAGE)