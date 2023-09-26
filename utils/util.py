from io import BytesIO
from PIL import Image
import base64
import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import os

def load_css_as_string(file_name):
    with open(file_name,'r') as f:
        css = f"""{f.read()}"""
    return css

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'''<style>{f.read()}</style>''', unsafe_allow_html=True)

def set_background(fav_image_path,logo_image_path):
    FAV = Image.open(fav_image_path)
    st.markdown(
        """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    # header, main, footer 설정
    set_index(logo_image_path)
    

def get_image_base64(image_path):
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="png")
    image_str = base64.b64encode(buffered.getvalue()).decode()
    return image_str

def set_index(logo_image_path):
    # header/footer/main_context layout css hack
    st.markdown( """ <style>
                @import url(https://cdn.rawgit.com/moonspam/NanumSquare/master/nanumsquare.css);
                header {
                    visibility : hidden;
                }
                body, body div, p, span {
                    font-family: 'Nanumsquare', 'Malgun Gothic' !important;
                }
                .css-qcqlej{
                    flex-grow:1;
                }
                footer {
                    visibility: visible;
                    background: #2D5AF0;

                }
                .css-164nlkn {
                    display : flex;
                    color : #2D5AF0;
                    max-width : 100%;
                    height : 4rem;
                    padding-top : 1rem;
                    padding-bottom : 1rem
                }
                footer a {
                    visibility: hidden;
                }
                footer {
                    font-family : "Nanumsquare";
                }
                footer:after {
                    visibility: visible; 
                    content:"ⓒ 2023. 인포스톰 All rights reserved";
                    font-weight: 700;
                    font-size: 15px;
                    color: #FFFFFF;
                    align-self : center;
                }
                .css-z5fcl4 {
                padding-left : 10%;
                padding-right : 10%;
                padding-top : 2rem !important;
                display : flex !important;  
                }

                </style> """, unsafe_allow_html=True)
    
    # Logo input & logo css hack
    # logo_img = get_image_base64('.\img\logo_char.jpg')
    logo_img = get_image_base64(logo_image_path)
    st.markdown("""<style>
                    .main-logo {
                        padding-bottom: 1rem;
                    }
                </style>""", unsafe_allow_html=True)
    st.markdown(f'''<a class="main-logo" href="/main" target="_self">
                    <img src="data:img\logo_char.jpg;base64,{logo_img}" width="240px"; height="70px";/>
                </a>''', unsafe_allow_html=True)


# 필수 요소 전부 들어있는지 체크하는 함수
def check_essential():
    '''
    이름, 지원 직무, 이력서가 있어야 합니다!
    면접관은 기본 세팅값이 있어서 괜찮!
    '''
    check_result = []
    josa =''
    if not st.session_state.user_name:
        check_result.append('이름')
        josa += '이'
    if st.session_state.selected_job == '검색 또는 선택':
        check_result.append('지원 직무')
        josa += '가'
    if not st.session_state.uploaded_resume:
        check_result.append('이력서')
        josa += '가'
    return check_result,josa

def read_sample_resume(path):
    with open(path, 'rb') as s1:
        data = s1.read()
    return data
    
def read_gif(path):
    with open(path, 'rb') as f:
        data = f.read()
        data = base64.b64encode(data).decode("utf-8")
    return data

def read_job_info_tb(path):
    job_info = pd.read_parquet(path, engine='pyarrow')
    job_info = job_info[(job_info.version == 'v2')].reset_index(drop=True)
    JOBS = ['검색 또는 선택'] + sorted(job_info['job_nm'].tolist())
    return job_info,JOBS

def read_user_job_info(job_tb,selected_job):
    job_prompt, job_kpi_dic = job_tb[(job_tb.job_nm == selected_job)][['prompt', 'job_kpi_list']].values[0]
    job_kpi_dic = eval(job_kpi_dic) # String Dic을 Dic화 시켜줌

    job_nm = st.session_state.selected_job
    job_ability = ", ".join(job_kpi_dic['핵심역량list'])

    # print(job_nm, job_ability)
    return job_nm,job_ability

def read_prompt_from_txt(path):
    with open(path,"r") as f:
        data = f.read()
    return data