from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.callbacks import get_openai_callback
from langchain.prompts import (PromptTemplate,
                               ChatPromptTemplate,
                               SystemMessagePromptTemplate,
                               HumanMessagePromptTemplate)
import json
import re
import random
def generate_llm_sub_chain(llm, template, output_key: str):
    """
    주어진 LLM(Language Model)과 템플릿을 사용하여 LLM 체인을 생성합니다.

    :param llm: LLM 모델 객체
    :type llm: LLM (Language Model) 객체

    :param template: 프롬프트 템플릿 (템플릿 문자열 또는 PromptTemplate 객체)
    :type template: str 또는 PromptTemplate

    :param output_key: 생성된 체인의 출력을 저장할 출력 키
    :type output_key: str

    :return: 생성된 LLM 체인 객체
    :rtype: LLMChain 객체
    """
    if type(template)==str:
        # 프롬프트 템플릿 정의
        prompt_template = PromptTemplate.from_template(template)
    else:
        prompt_template = template
    # 프롬프트와 출력 키를 사용하여 LLM 체인 생성
    sub_chain = LLMChain(llm=llm, prompt=prompt_template, output_key=output_key)
    return sub_chain

def preprocess_questions(result):
    """
    질문 데이터를 전처리하는 함수입니다.

    :param result: 질문 데이터가 포함된 결과 객체
    :type result: dict

    :return: 전처리된 주요 질문과 추가 질문을 담은 두 개의 딕셔너리
    :rtype: tuple (main_question: dict, add_question: dict)
    """
    total_question = eval(result['generated_big_question_lst'])
    core_competencies = eval(result['core_competencies'])

    ### 질문 앞단에 숫자가 등장하는 경우 전처리 진행
    for key in total_question:
        total_question[key] = re.sub(r'\d+\.', '', total_question[key])

    ### 질문 전처리
    ### Create main_question dictionary with core_competencies as keys
    main_question = {key: value.split(';') for key, value in total_question.items() if key in core_competencies}
    ### Create add_question dictionary with remaining keys from total_question
    add_question = {key: value.split(';') for key, value in total_question.items() if key not in core_competencies}
    ### Randomly select one question for each competency in main_question
    main_question = {key: random.choice(value) for key, value in main_question.items()}
    
    return main_question,add_question,core_competencies

def load_user_resume(USER_RESUME_SAVE_DIR):
    """
    사용자 이력서를 로드하는 함수입니다.

    :param USER_RESUME_SAVE_DIR: 사용자 이력서가 저장된 디렉토리 경로
    :type USER_RESUME_SAVE_DIR: str

    :return: 사용자 이력서의 내용을 하나의 문자열로 합친 결과
    :rtype: str
    """
    loader = PyPDFLoader(USER_RESUME_SAVE_DIR)
    pages = loader.load()
    print(len(pages), print(pages[0].page_content[0:500]), pages[0].metadata)

    ### User Total 이력서 Import
    user_resume_lst = [n.page_content for n in pages]
    user_resume = " \n ".join(user_resume_lst)
    return user_resume

def save_user_resume(USER_RESUME_SAVE_DIR,uploaded_file):
    with open(USER_RESUME_SAVE_DIR, 'wb') as f:
        f.write(uploaded_file.getbuffer())