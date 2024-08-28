from openai import OpenAI # openai라는 패키지에서 OpenAI라는 클래스나
                          # 객체를 가져온다는 의미.
import streamlit as st
# as st: 'as'키워드는 Python에서 모듈이나 함수에 대해 '별칭'을 지정할때 사용
# streamlit 라이브러리를 st 라는 별칭으로 사용하겠다는 의미
# 관례: 많은 개발자들이 streamlit 라이브러리를 사용할때 'st'라는 별칭을 사용하는것이
# 일반적. 다른사람들과 협업할때 코드의 일관성을 유지할 수 있음. 중요해보이네

#st.title은 웹 애플리케이션의 제목을 설정하는 역할
st.title("HealthCareBot") 

# OpenAI API 비밀 키를 안전하게 가져옵니다.
# 클라이언트 생성: client는 생성된 OpenAI 클라이언트 객체를 저장하는 변수.
# 이 객체를 통해서 OpenAI API에 요청을 보내고, 결과를 받을 수 있다.
# 예를들어, 텍스트 생성, 대화형 응답 생성등을 할 때 이 client 객체를 사용.
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


if "openai_model" not in st.session_state:#st.session_state에 openai_model 이 존재하는지 확인
    st.session_state["openai_model"] = "gpt-4o" #st.session_state["openai_model"]이라는 세션 변수에
                                                #"gpt-4o"라는 값을 할당

# 시스템 메시지를 변수로 저장하되, 사용자에게는 표시되지 않도록 함
# system_message: 챗봇의 초기설정
system_message = ''' 
너의 이름은 헬스케어봇이야.
너는 항상 존댓말을 하는 챗봇이야. 절대로 다나까는 쓰지말고 '요'높임말로 끝내.
항상 친근하게 대답해줘
영어로 질문을 받아도 무조건 한글로 답변해줘.
한글이 아닌 답변일 때는 다시 생각해서 한글로 만들어줘
'''

if "messages" not in st.session_state: # message라는 키가 st.session_state에 존재하는지?
    st.session_state.messages = [] # message키가 세션 상태에 없다면, 빈 리스트로 초기화
                                   # 이 리스트는 사용자가 주고받는 메시지의 기록을 저장하기 위한 용도로 사용됩니다.
    #초기화된 리스트에 첫 번째 메시지로 시스템 메시지를 추가합니다.
    st.session_state.messages.append({"role": "system", "content": system_message})
    #append는 리스트 메서드 중 하나로, 리스트의 마지막에 새로운 요소를 추가합니다.
    # {"role": "system", "content": system_message}은 하나의 메시지를 나타내는 dictionary입니다. 여기서:
    # "role": "system"은 이 메시지가 시스템(즉, 초기설정)을 나타낸다는 것을 의미합니다.
    #"content": system_message 는 시스템 메시지의 내용입니다. 이전에 정의된 system_message 변수를 사용하여, 챗봇의 행동을 정의하는 초기 지침을 포함합니다.


# for구문으로 메시지 시스템 전체 루프
for message in st.session_state.messages: # 'st.session_state.messages' 리스트에 저장된 모든 메시지들을 하나씩 순회하는 'for'루프입니다.
                                          #  ''는 대화기록이 저장된 리스트, 각 메시지는 dictionary 형태로 저장되어있으며
                                          # {"role": "user", "content": "안녕하세요"}와 같은 구조입니다.
    if message["role"] != "system":  # 이 조건문은 각 메시지(message)가 시스템 메시지인지 확인합니다.
                                     # 'message["role"]'은 이 메시지가 시스템에서 생성된 것인지, 사용자 또는 챗봇에서 생성된 것인지를 나타내는 값을 가져옵니다.
                                     # 이 코드에서는 "system"이 아닌 경우에만 해당 메시지를 처리하도록 설정되어 있습니다. 즉, 시스템 메시지는 화면에 표시되지 않도록.
        #with 구문은 이 메시지를 특정 스타일로 화면에 표시하기 위한 블록을 설정합니다.
        with st.chat_message(message["role"]): # 'st.chat_message' 는 Streamlit에서 대화형 메시지를 표시하기 위해 사용하는 컨텍스트 매니저입니다.
                                               # 'message["role"]은 메시지의 역할을 나타내며, 이 역할에 따라 메시지가 어떤 스타일로 표시될지 결정합니다.
            st.markdown(message["content"]) # 'st.markdown'은 'Streamlit'에서 텍스트를 화면에 표시할 때 사용하는 함수입니다.
                                            # 이 함수는 마크다운(markdown)형식을 지원하여 텍스트를 포맷팅 할 수 있습니다.
                                            # 'message["content"]는 메시지의 실제 내용을 가져와, 이를 화면에 출력합니다.
# ':='은 표현식 안에서 값을 변수에 할당하고, 동시에 그 값을 사용할 수 있도록 홰줍니다.
if prompt := st.chat_input("keep chat going..."): # 'st.chat_input("What is up?")'은 사용자로부터 입력을 받는 Streamlit의 함수입니다.
                                           # 이 함수는 텍스트 입력란을 화면에 표시하고, 사용자가 텍스트를 입력하면 그 값을 'prompt'변수에 저장합니다.
                                           # 'if prompt := ...' 는 입력된 값이 존재할 경우(빈값이 아닌경우) 그 값을 'prompt'변수에 할당하고, 조건문 안의 코드를 실행합니다.
    st.session_state.messages.append({"role": "user", "content": prompt}) # 사용자가 입력한 메시지를 대화 기록 'st.session_state.messages'에 추가합니다.
                                            # "role"은 메시지가 사용자(user)로붜 온것임을 나타내고, 'content'는 사용자가 입력한 실제 내용을 저장합니다.
    with st.chat_message("user"): # with st.chat._message("user")는 메시지를 사용자의 메시지 스타일로 화면에 표시하기 위한 컨텍스트 블록을 만듭니다.
        st.markdown(prompt) # st.markdown.(prompt) 는 사용자가 입력한 텍스트를 화면에 표시합니다.
# OpenAI API 호출 및 응답처리
    with st.chat_message("assistant"): # 이 블록은 챗봇의 응답을 화면에 표시하기 위한 컨텍스트를 설정합니다.
                            # ㄴ> "assistant" 역할로 '응답'을 표시합니다.
        stream = client.chat.completions.create( # 'client.chat.completions.create(...)'은 OpenAI의 GPT모델을 사용하여 챗봇의 응답을 생성하는 API호출("Completions"엔드포인트 호출)을 수행합니다. 
            model=st.session_state["openai_model"],# 'model=st.session_state["openai_model"]' 은 사용할 모델을 지정합니다. 이 경우 "gpt-4o" 모델이 사용됩니다.
            messages=[ # 'messages = [...]' 는 대화의 전체 기록을 API에 전달하여, 그 맥락에 맞는 응답을 생성하도록 합니다.
                        # ↓ 'm'은 st.session_state.messages의 리스트 내의 각 요소를 순회할 때 사용되는 변수입니다. 구체적으로는 리스트 내의 각 메시지를 가리키는 변수입니다.
                {"role": m["role"], "content": m["content"]} # 'm["role"]'는 현재 메시지의 역할을 가져오고, 'm["content"]는 그 메시지의 내용을 가져옵니다.
                                                             # 이 정보를 바탕으로 새로운 사전을 생성합니다.
                for m in st.session_state.messages
            ],
            stream=True,# 응답을 스트리밍 방식으로 받아올 수 있도록  합니다.
        )
        response = st.write_stream(stream) # 스트리밍 방식으로 받은 응답을 실시간으로 화면에 출력합니다.
    st.session_state.messages.append({"role": "assistant", "content": response})
    # 챗봇이 생성한 응답을 대화 기록에 추가합니다.
    #{"role": "assistant", "content": response}라는 사전(dictionary) 형태로 응답을 저장하며, role은 이 메시지가 챗봇(assistant)으로부터 온 것임을 나타내고, content는 챗봇의 응답 내용을 저장합니다.