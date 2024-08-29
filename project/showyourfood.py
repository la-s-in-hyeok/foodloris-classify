import os
import streamlit as st
from PIL import Image
import numpy as np
import requests
import base64
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Food Analysis",
    page_icon="🍽",
    layout="centered",
)
# Streamlit 제목 설정
st.title("Show your Food!!")



# 초기 안내 메시지 추가
st.markdown("""
            ### <이용방법>
            이 앱은 업로드한 음식 사진을 분석하여 음식의 이름과 칼로리, 영양 성분을 알려드립니다.

            1. OpenAI API Key를 입력하세요.
            2. 음식 사진을 업로드하세요.
            3. 챗봇이 자동으로 분석을 수행하고 결과를 알려드릴 것입니다.

            ‼️주의‼️: 음식 사진만 업로드해주세요. 다른 사진은 인식되지 않을 수 있습니다.
    <style>
        .reportview-container {
            background-color: #f3f4ed;
        }
        h1 {
            color: black;
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

stored_password = st.secrets["password"]
api_key = st.secrets["OPENAI_API_KEY"]

input_password = st.text_input("비밀번호를 입력하세요", type="password")

if input_password:
    if input_password == stored_password:
        st.success("비밀번호가 확인되었습니다. API Key가 자동으로 입력됩니다.")
    else:
        st.error("비밀번호가 올바르지 않습니다.")
        api_key = None
else:
    api_key = None

if api_key:
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"
    
    # Few-shot 예시 메시지 설정
    few_shot_examples = [
        {"role": "user", "content": "(질문 예시)이 사진 속 음식은 무엇인가요?"},
        {"role": "assistant", "content": "(답변 예시)음식: 김치찌개\n칼로리: 약 500kcal\n영양성분: 탄수화물 10g, 단백질 15g, 지방 20g\n잘 어울리는 음식: 공깃밥"},
        
        {"role": "user", "content": "(질문 예시)이 사진 속 음식은 무엇인가요?"},
        {"role": "assistant", "content": "(답변 예시)음식: 비빔밥\n칼로리: 약 600kcal\n영양성분: 탄수화물 85g, 단백질 20g, 지방 15g\n잘 어울리는 음식: 된장국"},
    ]
    
    system_message = ''' 
    너의 이름은 food classifier bot이야.
    너는 항상 존댓말을 하는 챗봇이야. 절대로 다나까는 쓰지말고 '요'높임말로 끝내.
    너는 음식 사진을 받으면 그 사진 속 음식이 무엇인지 한글로 대답해.
    영어로 질문을 받아도 무조건 한글로 답변해줘.
    한글이 아닌 답변일 때는 다시 생각해서 한글로 만들어줘
    음식이 아닌 사진을 받았을 때는 "음식이 아닙니다. 음식사진을 업로드해주세요" 라고 대답을 해.
    '''
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": system_message})
        st.session_state.messages.extend(few_shot_examples)  # Few-shot 예시 추가

    uploaded_file = st.file_uploader("음식 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

    # 이미지 base64로 인코딩하는 함수
    def encode_image(image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    if uploaded_file is not None:
        # 이미지 열기 및 처리
        image = Image.open(uploaded_file)
        image = image.convert("RGB")  # 이미지를 RGB로 변환

        st.image(image, caption="업로드한 이미지", use_column_width=True)

        try:
            # 이미지를 base64로 인코딩
            base64_image = encode_image(image)

            # OpenAI API 요청 준비
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            payload = {
                "model": st.session_state["openai_model"],
                "messages": st.session_state.messages + [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "이 사진속 음식은 무엇인지 말해주고 사진속 음식의 칼로리는 몇인지 대답해"
                                        "추측의 말투로 말을 하지말고 확신에 찬 말투로 대답해줘. 잘어울리는 음식은 너가 생각하기에 최고로 잘어울리는 음식으로 추천해 .대답을 할 때는"
                                        "- 음식 :  "
                                        "- 칼로리: "
                                        "- 영양성분: "
                                        "- 잘어울리는 음식:"
                                        "으로 레이블을 붙여서 한 항목씩 줄을 바꿔가며 대답해."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2  # 정밀도를 높이고 창의성을 줄이기 위한 temperature 설정
            }

            # 로딩 애니메이션 시작
            with st.spinner('이미지를 분석 중입니다...'):
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                st.write(analysis_text)

                # 피드백 기능 추가
                st.markdown("### 이 응답이 도움이 되었나요?")
                feedback = st.radio("응답에 대한 피드백을 선택하세요", ["도움이 되었어요", "더 개선이 필요해요"], index=None)

                if feedback == "더 개선이 필요해요":
                    feedback_text = st.text_area("어떤 부분을 개선하면 좋을지 알려주세요:")
                    if st.button("피드백 제출"):
                        # 피드백을 파일에 저장
                        with open("feedback.txt", "a") as f:
                            f.write(f"시간: {datetime.now()}\n")
                            f.write(f"사용자 피드백: {feedback_text}\n")
                            f.write("-" * 40 + "\n")
                        st.success("피드백이 제출되었습니다. 감사합니다!")
                elif feedback == "도움이 되었어요":
                    st.success("""감사합니다! 식사 맛있게하세요🍽️\n
                               This program was created by La-sinhyeok & Park geonsoo""")
                    with open("feedback.txt", "a") as f:
                        f.write(f"시간: {datetime.now()}\n")
                        f.write(f"사용자 피드백: {'good'}\n")
                        f.write("-" * 40 + "\n")

                # 추가 질문 옵션 추가
                st.markdown("### 추가 질문이 있나요?")
                additional_question = st.text_input("추가 질문을 입력하세요:")

                if st.button("추가 질문 보내기"):
                    st.session_state.messages.append({"role": "user", "content": additional_question})
                    st.write("질문이 제출되었습니다. 잠시만 기다려주세요...")

                    # 추가 질문을 OpenAI API로 보내고 응답 처리
                    payload = {
                        "model": st.session_state["openai_model"],
                        "messages": st.session_state.messages,
                        "temperature": 0.2  # 정밀도를 높이고 창의성을 줄이기 위한 temperature 설정
                    }

                    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        st.write(result['choices'][0]['message']['content'])
                        st.session_state.messages.append({"role": "assistant", "content": result['choices'][0]['message']['content']})
                    else:
                        st.error("추가 질문에 대한 OpenAI API 호출에 실패했습니다.")
                        st.error(f"상태 코드: {response.status_code}, 응답: {response.text}")

            else:
                st.error("OpenAI API 호출에 실패했습니다.")
                st.error(f"상태 코드: {response.status_code}, 응답: {response.text}")

        except Exception as e:
            st.error("이미지 처리에 실패했습니다. 다른 이미지를 업로드해 주세요.")
            st.error(f"오류 내용: {e}")

    for message in st.session_state.messages:
        if message["role"] not in ["system", "assistant", "user"]:  # 사용자 메시지만 표시
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("채팅을 계속하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            # OpenAI API 호출 (기본 텍스트만 처리)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            payload = {
                "model": st.session_state["openai_model"],
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                "temperature": 0.2  # 정밀도를 높이고 창의성을 줄이기 위한 temperature 설정
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                st.write(result['choices'][0]['message']['content'])
                st.session_state.messages.append({"role": "assistant", "content": result['choices'][0]['message']['content']})
            else:
                st.error("OpenAI API 호출에 실패했습니다.")
                st.error(f"상태 코드: {response.status_code}, 응답: {response.text}")
else:
    st.warning("API Key를 입력하세요.")
