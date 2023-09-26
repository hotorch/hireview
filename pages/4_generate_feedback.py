import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import traceback
from ast import literal_eval
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from streamlit_extras.switch_page_button import switch_page
from utils.util import (read_gif,
                        read_prompt_from_txt,
                        local_css)
import base64 # gif 이미지 불러오기
from src.generate_report import (kpi_radar_chart,
                                 conversation_output_parsing,
                                 kpi_output_parsing,
                                 load_conversation,
                                 generate_report,
                                 save_report)
import os
import json
st.session_state.logger.info("start")

NEXT_PAGE = 'user_report'
#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG
local_css("css/background.css")
local_css("css/4_generate_feedback.css")

## set variables
USER_REPORT_SAVE_DIR = os.path.join(st.session_state["save_dir"],'4_generate_feedback_user_report.json')
USER_KPI_REPORT_SAVE_DIR = os.path.join(st.session_state["save_dir"],'4_generate_feedback_user_kpi_report.json')
USER_FINAL_REPORT_SAVE_DIR = os.path.join(st.session_state["save_dir"],'4_generate_feedback_user_final_report.json')
MODEL_NAME_LLM_CONVERSATION = 'gpt-3.5-turbo-16k'
MODEL_NAME_LLM_TOTAL = 'gpt-3.5-turbo-16k'
st.session_state.report_dir = USER_REPORT_SAVE_DIR

## read prompt
question_prompt = read_prompt_from_txt("./data/prompt/question_report.txt")
total_prompt = read_prompt_from_txt("./data/prompt/total_report.txt")

## create llm object
llm_conversation = ChatOpenAI(temperature=0,
                              model=MODEL_NAME_LLM_CONVERSATION)
llm_total = ChatOpenAI(temperature=0,
                       model=MODEL_NAME_LLM_TOTAL)
st.session_state.logger.info(f"create llm object")


st.markdown(f"""
        <div class="loading_text">
            <p>'{st.session_state.user_name}'님의 면접 피드백 리포트 생성 중입니다. <br> 최대 5분까지 소요될 수 있습니다.</p>
        </div>
        <section class="dots-container">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            </section>

        """,  unsafe_allow_html=True)
# 피드백 팁
st.markdown(f'''<div class='loading_space'>
                    <img class='tips' src="data:image/gif;base64,{st.session_state['LOADING_GIF2']}"></div>''', unsafe_allow_html=True)
time.sleep(2)

## dummy input
if 'selected_job' not in st.session_state:
    st.session_state['selected_job'] = "NLP엔지니어"
    st.session_state.logger.info(f"load sample selected_job")
    
if 'main_job_ability' not in st.session_state:
    with open("./data/test/main_job_ability.txt","r") as f:
        data = f.read()
    st.session_state['main_job_ability'] = literal_eval(data) 
    st.session_state.logger.info(f"load sample main_job_ability")
    
if "all_conversation_history" not in st.session_state:
    st.session_state['all_conversation_history'] = load_conversation('./data/test/all_conversation_history.txt')
    st.session_state.logger.info(f"load sample all_conversation_history")

job_nm = st.session_state.selected_job
main_job_ability = st.session_state.main_job_ability
st.session_state.logger.info(f"load job nm, main job ability")

## generate report
user_report, callback = generate_report(llm_conversation = llm_conversation,
                                        llm_total = llm_total,
                                        all_conversation_history_lst = st.session_state.all_conversation_history,
                                        job_nm = st.session_state.selected_job,
                                        main_job_ability = st.session_state.main_job_ability,
                                        question_prompt = question_prompt,
                                        total_prompt = total_prompt
                                        )
st.session_state.logger.info(f"generate report")
## Token 사용량 기록
st.session_state.logger.info(f"Total tokens used: {callback.total_tokens}")
st.session_state.logger.info(f"Prompt tokens: {callback.prompt_tokens}")
st.session_state.logger.info(f"Completion tokens: {callback.completion_tokens}")
## save report
with open(st.session_state.report_dir,"w",encoding='utf-8') as f:
    json.dump(user_report,f)
st.session_state['user_report'] = user_report
st.session_state.logger.info(f"save user report")

## report parsing
text_list = conversation_output_parsing(user_report)
kpi_report, final_report = kpi_output_parsing(user_report)
st.session_state.logger.info("create kpi_report, final_report")
## save report
save_report(USER_KPI_REPORT_SAVE_DIR,kpi_report)
save_report(USER_FINAL_REPORT_SAVE_DIR,final_report)
st.session_state.logger.info("save kpi_report, final_report")
## to session state
st.session_state['kpi_report'] = kpi_report
st.session_state['final_report'] = final_report
st.session_state.logger.info(f"kpi report : {kpi_report}")
st.session_state.logger.info(f"final report : {final_report}")
## create radar data
radar_data = kpi_radar_chart(kpi_report)
st.session_state['radar_data'] = radar_data
st.session_state.logger.info(f"create radar data")

switch_page(NEXT_PAGE)