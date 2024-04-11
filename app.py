##################################################################
# Gateway to LLMs
#
# History
# When      | Who            | What
# 15/03/2024| Tian-Qing Ye   | Created
# 21/03/2024| Tian-Qing Ye   | Further developed
##################################################################
import streamlit as st
from streamlit_javascript import st_javascript
#import streamlit_authenticator as stauth
#from streamlit.runtime.scriptrunner import get_script_run_ctx
#from st_multimodal_chatinput import multimodal_chatinput
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from langchain_community.llms import HuggingFaceHub
from langchain.chains import ConversationChain

import yaml
from yaml.loader import SafeLoader
from PIL import Image
from io import BytesIO
from gtts import gTTS, gTTSError

from langdetect import detect
import os
import sys
from datetime import datetime
from typing import List
import random, string
import json
from base64 import b64decode
from random import randint

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import libs
#from st_utils import *

HF_REPO = "mistralai"
HF_LLM_ID = "Mixtral-8x7B-Instruct-v0.1"
#HF_LLM_ID = "Mistral-7B-Instruct-v0.2"

#HF_REPO = "hfl"
#HF_LLM_ID = "chinese-mixtral-instruct"

MODEL_ID = HF_REPO + "/" + HF_LLM_ID

HF_LLM_NAME = "Mixtral-8x7B-Instruct"   # a short name for displaying in UI

os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.secrets["HF_API_Token"]
# Or using the following format
#os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_xxxxxxxxxxxxxxxxxxxxxx"

sendmail = True

class Locale:    
    ai_role_options: List[str]
    ai_role_prefix: str
    ai_role_postfix: str
    role_tab_label: str
    title: str
    language: str
    lang_code: str
    chat_tab_label: str
    chat_messages: str
    chat_placeholder: str
    chat_run_btn: str
    chat_clear_btn: str
    chat_clear_note: str
    file_upload_label: str
    login_prompt: str
    logout_prompt: str
    username_prompt: str
    password_prompt: str
    support_message: str
    select_placeholder1: str
    select_placeholder2: str
    stt_placeholder: str
    radio_placeholder: str
    radio_text1: str
    radio_text2: str
    
    def __init__(self, 
                ai_role_options, 
                ai_role_prefix,
                ai_role_postfix,
                role_tab_label,
                title,
                language,
                lang_code,
                chat_tab_label,
                chat_messages,
                chat_placeholder,
                chat_run_btn,
                chat_clear_btn,
                chat_clear_note,
                file_upload_label,
                login_prompt,
                logout_prompt,
                username_prompt,
                password_prompt,
                support_message,
                select_placeholder1,
                select_placeholder2,
                stt_placeholder,
                radio_placeholder,
                radio_text1,
                radio_text2,                
                ):
        self.ai_role_options = ai_role_options, 
        self.ai_role_prefix= ai_role_prefix,
        self.ai_role_postfix= ai_role_postfix,
        self.role_tab_label = role_tab_label,
        self.title= title,
        self.language= language,
        self.lang_code= lang_code,
        self.chat_tab_label= chat_tab_label,
        self.chat_placeholder= chat_placeholder,
        self.chat_messages = chat_messages,
        self.chat_run_btn= chat_run_btn,
        self.chat_clear_btn= chat_clear_btn,
        self.chat_clear_note= chat_clear_note,
        self.file_upload_label = file_upload_label,
        self.login_prompt= login_prompt,
        self.logout_prompt= logout_prompt,
        self.username_prompt= username_prompt,
        self.password_prompt= password_prompt,
        self.support_message = support_message,
        self.select_placeholder1= select_placeholder1,
        self.select_placeholder2= select_placeholder2,
        self.stt_placeholder = stt_placeholder,
        self.radio_placeholder= radio_placeholder,
        self.radio_text1= radio_text1,
        self.radio_text2= radio_text2,


AI_ROLE_OPTIONS_EN = [
    "helpful assistant",
    "code assistant",
    "code reviewer",
    "text improver",
]

AI_ROLE_OPTIONS_ZW = [
    "helpful assistant",
    "code assistant",
    "code reviewer",
    "text improver",
]

en = Locale(
    ai_role_options=AI_ROLE_OPTIONS_EN,
    ai_role_prefix="You are an assistant",
    ai_role_postfix="Answer as concisely as possible.",
    role_tab_label="🤖 Sys Role",
    title="Ask LLM",
    language="English",
    lang_code='en',
    chat_tab_label="💬 Chat",
    chat_placeholder="Your Request:",
    chat_messages="Messages:",
    chat_run_btn="Submit",
    chat_clear_btn="New Topic",
    chat_clear_note="Note: \nThe information generated from each dialogue will be transferred to the AI model as temporary memory, with a limit of ten records being retained. If the upcoming topic does not relate to the previous conversation, please select the 'New Topic' button. This ensures that the new topic remains unaffected by any prior content!",
    file_upload_label="Please upload a file",
    login_prompt="Login",
    logout_prompt="Logout",
    username_prompt="Username/password is incorrect",
    password_prompt="Please enter your username and password",
    support_message="Please report any issues or suggestions to tqye2006@gmail.com",
    select_placeholder1="Select Model",
    select_placeholder2="Select Role",
    stt_placeholder="Play Audio",
    radio_placeholder="UI Language",
    radio_text1="English",
    radio_text2="中文",
)

zw = Locale(
    ai_role_options=AI_ROLE_OPTIONS_ZW,
    ai_role_prefix="You are an assistant",
    ai_role_postfix="Answer as concisely as possible.",
    role_tab_label="🤖 AI角色",
    title="Ask LLM",
    language="中文·",
    lang_code='zh-CN',
    chat_tab_label="💬 会话",
    chat_placeholder="请输入你的问题或提示:",
    chat_messages="聊天内容:",
    chat_run_btn="提交",
    chat_clear_btn="新话题",
    chat_clear_note="注意：\n每条对话产生的信息将作为临时记忆输入给AI模型，并保持至多十条记录。若接下来的话题与之前的不相关，请点击“新话题”按钮，以确保新话题不会受之前内容的影响，同时也有助于节省字符传输量。谢谢！",
    file_upload_label="请上传一个文件",
    login_prompt="登陆：",
    logout_prompt="退出",
    username_prompt="用户名/密码错误",
    password_prompt="请输入用户名和密码",
    support_message="如遇什么问题或有什么建议，请电 tqye2006@gmail.com",
    select_placeholder1="选择AI模型",
    select_placeholder2="选择AI的角色",
    stt_placeholder="播放",
    radio_placeholder="选择界面语言",
    radio_text1="English",
    radio_text2="中文",
)

st.set_page_config(page_title="Ask LLM", 
                   initial_sidebar_state="expanded", 
                   layout='wide',
                   menu_items={
                    'Report a bug': "mailto:tqye2006@gmail.com",
                    'About': "# For Experiment Only.Feb-2024"}
    )

st.markdown(
    """
        <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

                .sidebar .sidebar-content {{
                    width: 40px;
                }}

        </style>""".format(padding_top=0, padding_bottom=1),
        unsafe_allow_html=True,
)

# maximum messages remembered
MAX_MESSAGES = 20

current_user = "**new_chat**"

if "user" not in st.session_state:
    st.session_state.user = ""


if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "user_text" not in st.session_state:
    st.session_state.user_text = ""

if "model_response" not in st.session_state:
    st.session_state.model_response = ""

if "code_section" not in st.session_state:
    st.session_state.code_section = ""

if 'total_tokens' not in st.session_state:
    st.session_state["total_tokens"] = 0

# system messages and/or context
set_context_all = {"General Assistant": ""}
set_context_all.update(libs.set_sys_context)

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def callback_fun(arg):
    try:
        st.session_state[arg + current_user + "value"] = st.session_state[arg + current_user]

        sys_msg = ""
        for ctx in [
            set_context_all[st.session_state["context_select" + current_user]],
            st.session_state["context_input" + current_user],
        ]:
            if ctx != "":
                sys_msg += ctx + '\n'
    except Exception as ex:
        sys_msg = ""


    if len(sys_msg.strip()) > 10:
        SYS_PROMPT = [{"role": "system", "content": sys_msg}]
    else:
        SYS_PROMPT = [{"role": "system", "content": "You are a helpful assistant who can answer or handle all my queries!"}]

    st.session_state.messages = SYS_PROMPT

@st.cache_data()
def get_app_folder():
    app_folder = os.path.dirname(__file__)

    return app_folder

@st.cache_resource()
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    f.close()

def get_client_ip():
    '''
    workaround solution, via 'https://api.ipify.org?format=json' for get client ip
    
    example:
    ip_address = client_ip()  # now you have it in the host...
    st.write(ip_address)  # so you can log it, etc.    
    '''
    url = 'https://api.ipify.org?format=json'

    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')

    try:
        result = st_javascript(script)

        if isinstance(result, dict) and 'ip' in result:
            return result['ip']

    except:
        pass

@st.cache_data()
def get_remote_ip() -> str:
    """Get remote ip."""

    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

@st.cache_data(show_spinner=False)
def save_log(query, res, total_tokens):
    '''
    Log an event or error
    '''
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    app_folder = get_app_folder()
    f = open(app_folder + "/LLM.log", "a", encoding='utf-8',)
    f.write(f'[{date_time}] {st.session_state.user}:():\n')
    f.write(f'[You]: {query}\n')
    f.write(f'[{HF_LLM_ID}]: {res}\n')
    f.write(f'[Tokens]: {total_tokens}\n')
    f.write(f"User ip: {st.session_state.user_ip}")
    f.write(100 * '-' + '\n\n') 

    try:
        if sendmail == True:
            send_mail(query, res, total_tokens)
    except Exception as ex:
        f.write(f'Sending mail failed {ex}\n')
        pass

    f.close()

    print(f'[{date_time}]: {st.session_state.user}\n')
    print(res+'\n')

@st.cache_data(show_spinner=False)
def send_mail(query, res, total_tokens):
    '''
    '''
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    remote_ip = get_remote_ip()
    message = f'[{date_time}] {st.session_state.user}:({remote_ip}):\n'
    message += f'[You]: {query}\n'
    message += f'[Claude]: {res}\n'
    message += f'[Tokens]: {total_tokens}\n'

    # Set up the SMTP server and log into your account
    smtp_server = "smtp.gmail.com"
    port = 587
    # sender_email = "your_email@gmail.com"
    # password = "your_password"
    sender_email = st.secrets["gmail_user"]
    password = st.secrets["gmail_passwd"]

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)

    # Create the MIMEMultipart message object and load it with appropriate headers for From, To, and Subject fields
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = st.secrets["receive_mail"]
    msg['Subject'] = f"Chat from {st.session_state.user}"

    # Add your message body
    body = message
    msg.attach(MIMEText(body, 'plain'))

    try:
        filename, file_extension = os.path.splitext(res)
        if file_extension == ".png":
            # Open the image file in binary mode
            with open(res, 'rb') as fp:
                # Create a MIMEImage object with the image data
                img = MIMEImage(fp.read())

            # Attach the image to the MIMEMultipart object
            msg.attach(img)
    except Exception as e:
        print(f"Error: {str(e)}", 0)

    # Send the message using the SMTP server object
    server.send_message(msg)
    server.quit()


@st.cache_resource()
def Main_Title(text: str) -> None:

    st.markdown(f'<p style="background-color:#ffffff;color:#049ca4;font-weight:bold;font-size:24px;border-radius:2%;">{text}</p>', unsafe_allow_html=True)

def Show_Audio_Player(ai_content: str) -> None:
    sound_file = BytesIO()
    try:
        lang = detect(ai_content)
        print("Language:", lang)
        if lang in ['zh', 'zh-cn', 'en', 'de', 'fr'] :
            tts = gTTS(text=ai_content, lang=lang)
            #if st.session_state['locale'] is zw:
            #    tts = gTTS(text=ai_content, lang='zh')
            #else:
            #    tts = gTTS(text=ai_content, lang='en')
            tts.write_to_fp(sound_file)
            st.session_state.gtts_placeholder.write(st.session_state.locale.stt_placeholder)
            st.session_state.gtts_placeholder.audio(sound_file)
    except gTTSError as err:
        #st.session_state.gtts_placeholder.error(err)
        save_log("Error", str(err), 0)
    except Exception as ex:
        #st.session_state.gtts_placeholder.error(err)
        save_log("Error", str(ex), 0)

def Login() -> str:
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    random_key = randomword(10)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        random_key,
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login(st.session_state.locale.login_prompt[0], 'main')

    if authentication_status:
        if name:
            authenticator.logout(st.session_state.locale.logout_prompt[0], 'main')
            st.write(f'Welcome *{name}*')
    #        st.title('Some content')
        else:
            authentication_status = None
            st.warning(st.session_state.locale.password_prompt[0])
            name = ""
    elif authentication_status == False:
        st.error(st.session_state.locale.username_prompt[0])
        name = "invalid"
    elif authentication_status == None:
        st.warning(st.session_state.locale.password_prompt[0])
        name = ""
    else:
        st.warning(st.session_state.locale.password_prompt[0])
        name = ""
    

    return name, authentication_status, username


def Clear_Chat() -> None:
    st.session_state.past = []
    st.session_state.messages = []
    st.session_state.messages = BASE_PROMPT
    st.session_state.user_text = ""
    st.session_state.loaded_content = ""
    #st.session_state.locale = zw

    st.session_state["context_select" + current_user + "value"] = 'General Assistant'
    st.session_state["context_input" + current_user + "value"] = ""

    st.session_state.key += "1"     # HACK use the following two lines to reset update the file_uploader key
    st.rerun()

def Show_Images(placeholder, desc, img_url):

	# msg = f"![{desc}]({img_url})"
	# placeholder.markdown(msg, unsafe_allow_html=True)

    image = Image.open(img_url)
    placeholder.image(image, caption=desc)

def Show_Messages(msg_placeholder):

    messages_str = []
    for _ in st.session_state["messages"][1:]:
        if(_['role'] == 'user'):
            role = '**You**'
        elif (_['role'] == 'assistant'):
            role = '**Bot**'
        else:
            role = _['role']

        text = f"{_['content']}"
        if role == '**You**':
            print("Orignal text:", text)
            text_s = libs.remove_contexts(text)
            print("New text:", text_s)
            messages_str.append(f"{role}: {text_s}")
        else:
            messages_str.append(f"{role}: {text}")
    
    msg = str("\n\n".join(messages_str))
    msg_placeholder.markdown(msg, unsafe_allow_html=True)
    
def Show_Plot(plot_placeholder):

    if len(st.session_state.code_section[0]) > 10:
        print(st.session_state.code_section[0])
        try:
            exec(st.session_state.code_section[0])
            plot_placeholder.pyplot(exec(st.session_state.code_section[0]))
        except Exception as ex:
            print(f"Unable to execute code: {ex}")
            plot_placeholder.warning("Unable to execute the code")


@st.cache_resource
def Create_LLM():
    llm_hf = HuggingFaceHub(
        repo_id=MODEL_ID, 
        model_kwargs={"temperature": 0.7, "max_new_tokens": 4096, "return_full_text": False, "repetition_penalty" : 1.2}
    )

    return llm_hf


def Create_Model_Chain():

    llm_hf = Create_LLM()

    chain = ConversationChain(llm=llm_hf)

    return chain

def LLM_Completion(chain, inputs):
    '''
    '''

    if(len(inputs) > MAX_MESSAGES+1):
        inputs.pop(1)
        inputs.pop(1)

    #print("=============== FOR DEBUG ==============================")
    #print(f"Inputs for Model: {inputs}")
    #print("================ END DEBUG =============================")

    response1 = chain.predict(input=inputs)

    print(f"Outputs from the Model: {response1}")
    ret_context = response1
    
    return ret_context

##############################################
################ MAIN ########################
##############################################
def main(argv):

    Main_Title(st.session_state.locale.title[0] + " (v0.0.1)")

    st.session_state.info_placeholder = st.expander(f"Interface to LLM ({HF_LLM_NAME})")
    st.session_state.role_placeholder = st.empty()        # showing system role selected

    app_info = "This application is hosted locally, however the AI model is centrally hosted by Hugging Face."
    st.session_state.info_placeholder.write(app_info)

    st.session_state.role_placeholder = st.info(st.session_state.locale.role_tab_label[0] + ": **" + st.session_state["context_select" + current_user + "value"] + "**")

    # Build Model Chain
    chain = Create_Model_Chain()

    ## ----- Start --------
    tab_chat, tab_context = st.tabs([st.session_state.locale.chat_tab_label[0], st.session_state.locale.role_tab_label[0]])

    with tab_context:
        set_context_list = list(set_context_all.keys())
        context_select_index = set_context_list.index(
            st.session_state["context_select" + current_user + "value"]
        )
        st.selectbox(
            label="Role Setting",
            options=set_context_list,
            key="context_select" + current_user,
            index=context_select_index,
            on_change=callback_fun,
            args=("context_select",),
        )
        st.caption(set_context_all[st.session_state["context_select" + current_user]])

        st.text_area(
            label="Add or Pre-define Role Message：",
            key="context_input" + current_user,
            value=st.session_state["context_input" + current_user + "value"],
            on_change=callback_fun,
            args=("context_input",),
        )

    with tab_chat:
        msg_placeholder = st.empty()
        plot_placeholder = st.empty()

        Show_Messages(msg_placeholder)
        st.session_state.gtts_placeholder = st.empty()

        st.session_state.new_topic_button = st.button(label=st.session_state.locale.chat_clear_btn[0], key="newTopic", on_click=Clear_Chat)
        st.session_state.uploaded_file_placehoilder = st.empty()
        st.session_state.input_placeholder = st.empty()

        with st.session_state.uploaded_file_placehoilder:
            uploaded_file = st.file_uploader(label=st.session_state.locale.file_upload_label[0], type=['docx', 'txt', 'pdf', 'csv'],key=st.session_state.key, accept_multiple_files=False, label_visibility="collapsed")
            if uploaded_file is not None:
                #bytes_data = uploaded_file.read()
                st.session_state.loaded_content = libs.GetContexts(uploaded_file)
                #print("====================================================================")
                #print(st.session_state.loaded_content)
                #print("====================================================================")

        with st.session_state.input_placeholder.form(key="my_form", clear_on_submit = True):
            user_input = st.text_area(label=st.session_state.locale.chat_placeholder[0], value=st.session_state.user_text, max_chars=6000)
            send_button = st.form_submit_button(label=st.session_state.locale.chat_run_btn[0])

        if send_button :
            print(f"{st.session_state.user}: {user_input}")
            if(user_input.strip() != ''):
                if st.session_state.loaded_content.strip() != "":
                    prompt = f"<CONTEXT>{st.session_state.loaded_content.strip()}</CONTEXT>" + "\n\n" + user_input.strip()
                else:
                    prompt = user_input.strip()
                st.session_state.messages += [{"role": "user", "content": prompt}]
                
                with st.spinner('Wait ...'):
                    st.session_state.model_response = LLM_Completion(chain, st.session_state["messages"])
                    st.session_state.code_section = libs.extract_code(st.session_state.model_response)
                generated_text = st.session_state.model_response + '\n'
                st.session_state.messages += [{"role": "assistant", "content": generated_text}]
                #st.session_state["messages"] += [generated_text]

				# counting the number of messages
                st.session_state.message_count += 1
                #st.session_state.total_tokens += tokens
                Show_Messages(msg_placeholder)
                if len(st.session_state.code_section) > 1:
                    if len(st.session_state.code_section[0]) > 10:
                        Show_Plot(plot_placeholder)

                Show_Audio_Player(generated_text)

                save_log(prompt, generated_text, st.session_state.total_tokens)

##############################
if __name__ == "__main__":

    # Initiaiise session_state elements
    if "locale" not in st.session_state:
        st.session_state.locale = en

    if "user_ip" not in st.session_state:
        st.session_state.user_ip = get_client_ip()

    if "loaded_content" not in st.session_state:
        st.session_state.loaded_content = ""

    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0

    if 'key' not in st.session_state:
        st.session_state.key = str(randint(1000, 10000000))    

    BASE_PROMPT = [{"role": "system", "content": "You are a helpful assistant who can answer or handle all my queries!"}]
    if "messages" not in st.session_state:
        st.session_state.messages = BASE_PROMPT
    
    st.markdown(
            """
                <style>
                    .appview-container .block-container {{
                        padding-top: {padding_top}rem;
                        padding-bottom: {padding_bottom}rem;
                    }}
                    .sidebar .sidebar-content {{
                        width: 200px;
                    }}
                </style>""".format(padding_top=1, padding_bottom=10),
            unsafe_allow_html=True,
    )

    local_css("style.css")

    st.sidebar.button(st.session_state.locale.chat_clear_btn[0], on_click=Clear_Chat)
    st.sidebar.markdown(st.session_state.locale.chat_clear_note[0])
    st.sidebar.markdown(st.session_state.locale.support_message[0])

    #st.button(st.session_state.locale.new_reg_btn[0], on_click=New_User)
    
    #st.session_state.user, st.session_state.authentication_status, st.session_state.user_id = Login()
    #if st.session_state.user != None and st.session_state.user != "" and st.session_state.user != "invalid":
    #    current_user = st.session_state.user_id

    #    if "context_select" + current_user + "value" not in st.session_state:
    #        st.session_state["context_select" + current_user + "value"] = 'General Assistant'

    #    if "context_input" + current_user + "value" not in st.session_state:
    #        st.session_state["context_input" + current_user + "value"] = ""

    current_user = st.session_state.user
    if "context_select" + current_user + "value" not in st.session_state:
        st.session_state["context_select" + current_user + "value"] = 'General Assistant'    
    if "context_input" + current_user + "value" not in st.session_state:
        st.session_state["context_input" + current_user + "value"] = ""
    
    main(sys.argv)
    # else:
        # print(f"user: {st.session_state.user}")
        # print(f"auth_status: {st.session_state.authentication_status}")


    
