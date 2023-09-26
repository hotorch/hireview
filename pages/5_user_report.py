import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import traceback
from streamlit_modal import Modal
import json
import os
import pdfkit
from utils.util import (set_background,
                        read_gif,
                        load_css_as_string,
                        local_css)
from ast import literal_eval
st.session_state.logger.info("start")
#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG
style_html = f"""
        <style>
        body {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;  
        }}
        .inputtext {{
            color:#4C4F6D;
            font-size:24px;
            line-height:1.5;
            word-break:keep-all;
            font-weight:700;
            text-align:center;
            padding:2rem;
        }}
        .css-xb8f9c {{
            position: absolute;
        }}
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section > div.block-container.css-1y4p8pa.e1g8pov64 > div:nth-child(1) > div > div:nth-child(3) > div > button{{
        display:none;
        }}
        .centered-area {{
            display: flex; /* Flexbox 적용 */
            flex-flow: row nowrap;
            justify-content: center;
        }}
        .vertical-area {{
            display: flex;
            flex-direction: row; /* 수평 방향으로 요소들을 배치합니다. */
            flex-wrap: nowrap;
            justify-content: space-between; /* 요소들 사이에 공간을 동일하게 배분합니다. */
            align-items: center;
            gap: 4rem;
            width: 95%;
        }}
        .radar-chart {{
            background:#ffffff;
            margin-right:30px;
            display: flex;
            width:300px;
            height:100%;
        }}
        .summary {{
            font-size: 16px;
            float: left;
            padding: 2rem;
            height: auto;
            border: 3px solid #2D5AF0;
            border-radius: 39px;
            width:90% ;

        }}
        .feedback-summary-area {{
            width : 90%;
        }}
        .feedback-title {{
            border: 3px solid #2D5AF0;
            border-radius: 10px;
            width:200px;
            text-align: center;
            justify-content: center;
            margin-left:5px;
            margin-bottom:2px;
            background: #2D5AF0;
            display: flex;
            color: #FFFFFF;
            font-weight: bold;
        }}
        [data-testid="stVerticalBlock"] .element-container:nth-child(1) button {{
            width: 150px !important;
            height: 50px;
            display: flex;
            background: #2D5AF0;
            border: 3px solid #2D5AF0;
            margin-top: -150px;
            color: #FFFFFF;
            font-weight: bold;
        }}
        [data-testid="stVerticalBlock"] .element-container:nth-child(1) button:hover {{
            background: #FFFFFF;
            color:#2D5AF0;
        }}
        .stButton {{
            width:150px !important;
        }}
        .stButton:hover {{
            background: #FFFFFF;
            color:#2D5AF0;
        }}        
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.ea3mdgi5 > div.block-container.css-z5fcl4.ea3mdgi4 > div:nth-child(1) > div > div:nth-child(9) > div > div > div > button {{
            width: 150px !important;
            height: 50px;
            display: flex;
            background: #2D5AF0;
            border: 3px solid #2D5AF0;
            margin-top: -170px;
            margin-left: calc(69vw) !important;
            color: #FFFFFF;
            font-weight: bold;
        }}
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.ea3mdgi5 > div.block-container.css-z5fcl4.ea3mdgi4 > div:nth-child(1) > div > div:nth-child(9) > div > div > div > button:hover {{
            background: #FFFFFF;
            color:#2D5AF0;
        }}
        .stDownloadButton {{
            display:flex;
        }}
        .feedback-summary {{
            height:auto;
            margin-bottom: 200px !important;
            border: 3px solid #2D5AF0;
            border-radius: 39px;
        }}
        .table-container {{
            display: flex;
            justify-content: center;
            margin:20px !important;
        }}
        .table-container th {{
            white-space: nowrap;
            vertical-align: middle;
            text-align: center;
        }}
        .table-container th:first-child,
        .table-container td:first-child {{
            border-left: 0;
        }}
        .table-container th:last-child,
        .table-container td:last-child {{
            border-right: 0;
        }}
        .table-container tr:first-child {{
            border-top: 2px solid #CED4DA;
            border-bottom: 2px solid #CED4DA;
            background-color: #E9ECEF
        }}
        .table-container tr:not(:first-child) {{
            border-bottom: 2px solid #CED4DA
            ;
        }}
        .feedback-summary .extra {{
            font-size: 22px;
            font-weight: bold;
            padding-left: 2rem;
            padding-top: 1rem;
        }}
        .extra-table-container {{
            display: flex;
            justify-content: left;
            margin:20px !important;
            margin-top:5px;
            margin-bottom:5px;
        }}
        .extra-table-container th {{
            white-space: nowrap;
            vertical-align: middle;
            font-size:16px;
            text-align: center;
        }}
        .extra-table-container td {{
            font-weight:normal;
            font-size:16px;
        }}
        .extra-table-container th:first-child,
        .extra-table-container td:first-child {{
            border-left: 0;
        }}
        .extra-table-container th:last-child,
        .extra-table-container td:last-child {{
            border-right: 0;
        }}
        .extra-table-container tr:first-child {{
            border-top: 2px solid #CED4DA;
            border-bottom: 2px solid #CED4DA;
            background-color: #E9ECEF
        }}
        .extra-table-container tr:not(:first-child) {{
            border-bottom: 2px solid #CED4DA
            ;
        }}
        
        </style>      
"""

## set sample data
with open('./data/test/final_report.txt','r') as f:
    SAMPLE_FINAL_REPORT = f.readlines()
with open('./data/test/kpi_report.txt','r') as f:
    kpi_report = f.readlines()
    SAMPLE_KPI_REPORT = literal_eval(kpi_report[0])
with open('./data/test/add_question.txt','r') as f:
    add_question = f.read()
    add_question = literal_eval(add_question)
    
if "final_report" not in st.session_state:
    st.session_state['final_report'] = SAMPLE_FINAL_REPORT
if "kpi_report" not in st.session_state:
    st.session_state['kpi_report'] = SAMPLE_KPI_REPORT
if "user_name" not in st.session_state:
    st.session_state['user_name'] = '아무개'
if "selected_job" not in st.session_state:
    st.session_state['selected_job'] = 'NLP엔지니어'
if 'add_question' not in st.session_state:
    st.session_state['add_question'] = add_question

## 유저 피드백 불러오기
all_feedback = st.session_state.final_report

## 핵심역량 리스트 불러오기
kpi_list = [x['핵심 역량'] for x in st.session_state.kpi_report]     
st.session_state.logger.info(f"kpi list : {kpi_list}")
kpi_pos_feedback = [x['긍정적인 측면'] for x in st.session_state.kpi_report]
st.session_state.logger.info(f"kpi_pos_feedback : {kpi_pos_feedback}")
kpi_neg_feedback = [x['개선해야할 측면'] for x in st.session_state.kpi_report]
st.session_state.logger.info(f"kpi_neg_feedback : {kpi_neg_feedback}")
keys = list(st.session_state.add_question.keys())
values = list(st.session_state.add_question.values())

extra_question_html = ""
for i in range(len(keys)):
    for j in range(len(values[i])):
        if j == 0 :
            extra_question_html += f"""<tr><th rowspan="{len(values[i])}">{keys[i]}</th><td>{values[i][0]}</td></tr>"""
        else :
            extra_question_html += f"""
                                <tr><td>{values[i][j]}</td></tr>"""

div_html1 = f"""
    <div class="inputtext">'{st.session_state.user_name}'님의 '{st.session_state.selected_job}'지원 직무의 면접결과 리포트입니다. </div>
    <div class="centered-area">
    <div class="vertical-area">
        <div class="radar-chart"><img src="data:image/png;base64,{st.session_state.selected_job}" /></div>
        <div class="summary">{all_feedback}</div>
    </div>
    </div>
    <div class="feedback-summary-area">
    <dis class="feedback-title"> 역량별 피드백 </div>
    <div class="feedback-summary"> 
        <div class="table-container">
        <table>
            <tr>
            <th> KPI </th><th>긍정적인 점</th><th>개선해야할 점</th>
            </tr>
            <tr>
            <th>{kpi_list[0]}</th><td>{kpi_pos_feedback[0]}</td><td>{kpi_neg_feedback[0]}</td>
            </tr>
            <tr>
            <th>{kpi_list[1]}</th><td>{kpi_pos_feedback[1]}</td><td>{kpi_neg_feedback[1]}</td>
            </tr>
            <tr>
            <th>{kpi_list[2]}</th><td>{kpi_pos_feedback[2]}</td><td>{kpi_neg_feedback[2]}</td>
            </tr>
            <tr>
            <th>{kpi_list[3]}</th><td>{kpi_pos_feedback[3]}</td><td>{kpi_neg_feedback[3]}</td>
            </tr>
            <tr>
            <th>{kpi_list[4]}</th><td>{kpi_pos_feedback[4]}</td><td>{kpi_neg_feedback[4]}</td>
            </tr>
            <tr>
            <th>{kpi_list[5]}</th><td>{kpi_pos_feedback[5]}</td><td>{kpi_neg_feedback[5]}</td>
            </tr>
        </table>
        </div>
        <div class="extra">이런 질문도 받을 수 있어요.
    <div class="extra-table-container">
        <table>
            <tr>
            <th> KPI </th><th> 예상질문 </th>
            </tr>
            {extra_question_html}
        </table>
            </div>
        </div>
    </div>
    """

st.markdown(style_html, unsafe_allow_html=True)
st.markdown(div_html1, unsafe_allow_html=True)
    
## downlad html

div_html_button = f"""
    <style>
    body {{
    margin: 100px; /* 여백 크기를 조정하려면 필요한 크기로 변경하세요 */
    }}
    .feedback-summary {{
        margin-left: calc(10vw);
        margin-right: calc(10vw);
        display: flex;
    flex-flow: column;
    }}
    .feedback-summary {{
        width: 90%;
    }}
    .summary {{
        width: 75% !important;
    }}
    </style>
        """

file_path = os.path.join(st.session_state.save_dir,"all_conversation_history.txt")
with open(file_path, "r", encoding='utf-8') as file:
    ## 파일의 모든 내용을 읽어서 lines 리스트에 저장
    lines = file.readlines()

all_conv_text = ''
for line in lines:
    all_conv_text += line.strip()  #

all_conv_text = all_conv_text.replace('user',f'</b></br>[A]')
all_conv_text = all_conv_text.replace('assistant',f'</br><b>[Q]')
all_conv_text = all_conv_text.split('$$$$$$$$$$')
conv_log_html = """<div class="list-container">"""

text = ''
for i in range(len(all_conv_text)) :
    index = all_conv_text[i].find('</br>')
    ## Remove the leading "</br>" from the text
    if index != -1:
        all_conv_text[i] = all_conv_text[i][index + len('</br>'):]
    if i % 2 == 0 :
        text += f'<div class="list1"><p>{all_conv_text[i]}</b></p></div>'
    else :
        text += f'<div class="list2"><p>{all_conv_text[i]}</b></p></div>'
        
conv_log_html = conv_log_html + text + "</div>"
conv_log_style = """<style>
                    .list1 {
                        background:#e5edfb;
                        margin-top:2px;
                        line-height:2;  
                    }
                    .list1 p {
                        font-size:18px;
                    }
                    .list2 {
                        margin-top:2px;
                        line-height:2;
                        
                    }
                    .list2 p {
                        font-size:18px;
                    }
                    .list-container {
                        margin-left: 50px;
                        margin-right: 50px;
                    }
                    div[data-modal-container='true'][key='Demo Key'] > div:first-child > div:first-child {
                        overflow: scroll !important; 
                        max-height: calc(80vh);
                    }
                    .css-5rimss p {
                        margin:20px;
                    }
                    div[data-modal-container='true'][key='Demo Key'] > div > div:nth-child(2) > div > button {
                        margin-top: 60px;
                        margin-left: 1330px;
                        border: 3px solid #2D5AF0;
                        background: #2D5AF0;
                        color: #FFFFFF;
                        position: absolute;
                    }
                    .css-10trblm {
                        margin-left:5rem;
                    }
            </style>
"""
## download 버전
conv_log_download_html = """
                        <div class="feedback-summary-area">
                        <dis class="feedback-title"> 면접 대화 로그 </div>
                        <div class="feedback-summary"> """ + text + "</div></div></div>"
conv_log_download_style = """<style>
                    .vertical-area {
                        margin : 0px;;
                        padding : 0rem;
                        height:300px;
                    }
                    .list1 {
                        background:#e5edfb !important;
                        margin:15px;
                        line-height:2;  
                    }
                    .list1 p {
                        font-size:14px;
                    }
                    .list2 {
                        margin:15px;
                        line-height:2;
                        
                    }
                    .list2 p {
                        font-size:14px;
                    }
                    .list-container {
                        margin-left: 50px;
                        margin-right: 50px;
                        font-size:14px;
                    }
                    .feedback-summary {
                        font-size:14px;
                        margin-bottom: 80px !important;
                        margin-left: calc(10vw);
                        margin-right: calc(10vw);
                        display: flex;
                    flex-flow: column;
                    }
                    .feedback-title{
                        font-size:16px;
                        width:200px !important;
                        padding-left: 1rem !important;
                        padding-right: 1rem !important;
                        margin-left: 0px !important;
                    }
                    .summary {
                        font-size:14px;
                        width:700px !important;
                        # margin-left: 400px;
                        # margin-top: -200px; 
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                    }
                    th, td {
                        padding: 8px;
                        border: 1px solid #CED4DA;
                        font-size:14px;
                    }
                    .extra-table-container th, td{
                        font-size:14px !important;
                    }
            </style>
"""

with st.container() :
    modal = Modal(key="Demo Key",title="면접 대화 로그")
    open_modal = st.button("대화로그보기")

if open_modal:
    modal.open()
if modal.is_open():
    with modal.container():
            st.markdown(f"""
                    {conv_log_html + conv_log_style}
                """,  unsafe_allow_html=True)
            
all_download_html = style_html + conv_log_download_style + div_html1  + conv_log_download_html

## Add custom font CSS
font_css = """
<style>
    /* Replace 'YourFontFamily' with the desired font family name */
    body {
        font-family: 'Nanumsquare', sans-serif;
    }
</style>
"""

## Combine the font CSS with the existing HTML content
all_download_html = font_css + all_download_html
    

options = {
    'page-size':'Letter',
    'margin-top': '0.5in',
    'margin-bottom': '0.5in',
    'margin-right': '0.3in',
    'margin-left': '0.3in',
    'encoding': "UTF-8",
    # 'custom-header' : [
    #     ('Accept-Encoding', 'gzip')
    # ],
    'no-outline': None,
}

feedback_path = os.path.join(st.session_state.user_unique_path,'feedback.pdf')
pdfkit.from_string(all_download_html, feedback_path, options=options)
with open(feedback_path, "rb") as pdf_file:
    PDFbyte = pdf_file.read()
    
with st.container() :
    st.download_button(label="DOWNLOAD",
                        data=PDFbyte,
                        file_name='feedback.pdf',
                        mime='application/octet-stream')    
    
st.session_state.logger.info('>>> 면접 및 피드백 생성 최종 종료!')