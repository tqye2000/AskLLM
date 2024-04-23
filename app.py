##################################################################
# Chat with Open Source LLMs
#
# History
# When      | Who            | What
# 15/03/2024| Tian-Qing Ye   | Created
# 21/03/2024| Tian-Qing Ye   | Further developed
# 16/04/2024| Tian-Qing Ye   | Add support of CodeQwen1.5-7B-Chat
# 22/04/2024| Tian-Qing Ye   | Enable search on duckduckgo
##################################################################
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from langchain_community.llms import HuggingFaceHub
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import ConversationChain

import yaml
from yaml.loader import SafeLoader
from io import BytesIO
from gtts import gTTS, gTTSError

from langdetect import detect
import os
import sys
from datetime import datetime
from typing import List
import random, string
from random import randint
import argparse

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import libs

HF_REPO = "mistralai"
HF_LLM_ID = "Mixtral-8x7B-Instruct-v0.1"

MODEL_ID = HF_REPO + "/" + HF_LLM_ID

HF_LLM_NAME = "Mixtral-8x7B-Instruct"   # a short name for displaying in UI

os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.secrets["HF_API_Token"]
HUGGINGFACEHUB_API_TOKEN = st.secrets["HF_API_Token"]
# Or using the following format
#os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_xxxxxxxxxxxxxxxxxxxxxx"

sendmail = True
EN_BASE_PROMPT = [{"role": "system", "content": "You are a helpful assistant who can answer or handle all my queries!"}]
ZW_BASE_PROMPT = [{"role": "system", "content": "You are a helpful assistant who can answer or handle all my queries! Please response in Chinese where possible!"}]

class Locale:    
    ai_role_options: List[str]
    ai_role_prefix: str
    ai_role_postfix: str
    role_tab_label: str
    title: str
    choose_language: str
    language: str
    lang_code: str
    chat_tab_label: str
    chat_messages: str
    chat_placeholder: str
    chat_run_btn: str
    chat_clear_btn: str
    clear_doc_btn: str
    enable_search_label: str
    chat_clear_note: str
    file_upload_label: str
    login_prompt: str
    logout_prompt: str
    username_prompt: str
    password_prompt: str
    choose_llm_prompt: str
    support_message: str
    select_placeholder1: str
    select_placeholder2: str
    stt_placeholder: str
    
    def __init__(self, 
                ai_role_options, 
                ai_role_prefix,
                ai_role_postfix,
                role_tab_label,
                title,
                choose_language,
                language,
                lang_code,
                chat_tab_label,
                chat_messages,
                chat_placeholder,
                chat_run_btn,
                chat_clear_btn,
                clear_doc_btn,
                enable_search_label,
                chat_clear_note,
                file_upload_label,
                login_prompt,
                logout_prompt,
                username_prompt,
                password_prompt,
                choose_llm_prompt,
                support_message,
                select_placeholder1,
                select_placeholder2,
                stt_placeholder,
                ):
        self.ai_role_options = ai_role_options, 
        self.ai_role_prefix= ai_role_prefix,
        self.ai_role_postfix= ai_role_postfix,
        self.role_tab_label = role_tab_label,
        self.title= title,
        self.choose_language = choose_language,
        self.language= language,
        self.lang_code= lang_code,
        self.chat_tab_label= chat_tab_label,
        self.chat_placeholder= chat_placeholder,
        self.chat_messages = chat_messages,
        self.chat_run_btn= chat_run_btn,
        self.chat_clear_btn= chat_clear_btn,
        self.clear_doc_btn = clear_doc_btn,
        self.enable_search_label = enable_search_label,
        self.chat_clear_note= chat_clear_note,
        self.file_upload_label = file_upload_label,
        self.login_prompt= login_prompt,
        self.logout_prompt= logout_prompt,
        self.username_prompt= username_prompt,
        self.password_prompt= password_prompt,
        self.choose_llm_prompt = choose_llm_prompt,
        self.support_message = support_message,
        self.select_placeholder1= select_placeholder1,
        self.select_placeholder2= select_placeholder2,
        self.stt_placeholder = stt_placeholder,


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
    choose_language="选择界面语言",
    language="English",
    lang_code='en',
    chat_tab_label="💬 Chat",
    chat_placeholder="Your Request:",
    chat_messages="Messages:",
    chat_run_btn="✔️ Submit",
    chat_clear_btn=":cl: New Topic",
    clear_doc_btn=":x: Clear Doc",
    enable_search_label="Enable Web Search",
    chat_clear_note="Note: \nThe information generated from each dialogue will be transferred to the AI model as temporary memory, with a limit of ten records being retained. If the upcoming topic does not relate to the previous conversation, please select the 'New Topic' button. This ensures that the new topic remains unaffected by any prior content!",
    file_upload_label="You can chat with an uploaded file (your file will never be saved anywhere)",
    login_prompt="Login",
    logout_prompt="Logout",
    username_prompt="Username/password is incorrect",
    password_prompt="Please enter your username and password",
    choose_llm_prompt="Choose Your LLM",
    support_message="Please report any issues or suggestions to tqye2006@gmail.com",
    select_placeholder1="Select Model",
    select_placeholder2="Select Role",
    stt_placeholder="Play Audio",
)

zw = Locale(
    ai_role_options=AI_ROLE_OPTIONS_ZW,
    ai_role_prefix="You are an assistant",
    ai_role_postfix="Answer as concisely as possible.",
    role_tab_label="🤖 AI角色",
    title="Ask LLM",
    choose_language="Choose UI Language",
    language="中文·",
    lang_code='zh-CN',
    chat_tab_label="💬 会话",
    chat_placeholder="请输入你的问题或提示:",
    chat_messages="聊天内容:",
    chat_run_btn="✔️ 提交",
    chat_clear_btn=":cl: 新话题",
    clear_doc_btn="❌ 清空文件",
    enable_search_label="开通搜索",
    chat_clear_note="注意：\n每条对话产生的信息将作为临时记忆输入给AI模型，并保持至多十条记录。若接下来的话题与之前的不相关，请点击“新话题”按钮，以确保新话题不会受之前内容的影响，同时也有助于节省字符传输量。谢谢！",
    file_upload_label="你可以询问一个上传的文件（文件内容只在内存，不会被保留）",
    login_prompt="登陆：",
    logout_prompt="退出",
    username_prompt="用户名/密码错误",
    password_prompt="请输入用户名和密码",
    choose_llm_prompt="请选择您想使用的AI模型",
    support_message="如遇什么问题或有什么建议，请电 tqye2006@gmail.com",
    select_placeholder1="选择AI模型",
    select_placeholder2="选择AI的角色",
    stt_placeholder="播放",
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

@st.cache_data()
def parse_args(args):
    parser = argparse.ArgumentParser('AskLLM')
    parser.add_argument('--local', required=False)
    parser.add_argument('--seed', help='Seed for random generator', default=37, required=False)
    return parser.parse_args(args)

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
        if st.session_state.locale is zw:
            SYS_PROMPT = [{"role": "system", "content": "You are a helpful assistant who can answer or handle all my queries! Please reply in Chinese where possible!"}]
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

    ip_address = ""
    try:
        result = st_javascript(script)

        if isinstance(result, dict) and 'ip' in result:
            ip_address = result['ip']
        else:
            ip_address = "unknown_ip"
    except:
        pass

    return ip_address

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
    message = f'[{date_time}] {st.session_state.user}:({st.session_state.user_ip}):\n'
    message += f'[You]: {query}\n'
    message += f'[{HF_LLM_ID}]: {res}\n'
    message += f'[Tokens]: {total_tokens}\n'

    # Set up the SMTP server and log into your account
    smtp_server = "smtp.gmail.com"
    port = 587
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
    st.session_state.messages = []
    if st.session_state.locale == zw:
        st.session_state.messages = ZW_BASE_PROMPT
    else:
        st.session_state.messages = EN_BASE_PROMPT
        
    st.session_state.user_text = ""
    st.session_state.loaded_content = ""

    st.session_state["context_select" + current_user + "value"] = 'General Assistant'
    st.session_state["context_input" + current_user + "value"] = ""

    st.session_state.key += "1"     # HACK use the following two lines to reset update the file_uploader key
    st.rerun()


def Delete_Files():

    st.session_state.loaded_content = ""
    st.session_state.key += "1"     # HACK use the following two lines to reset update the file_uploader key
    st.rerun()

def Show_Messages(msg_placeholder):

    messages_str = []
    for _ in st.session_state["messages"][1:]:
        if(_['role'] == 'user'):
            role = '**You**'
        elif (_['role'] == 'assistant'):
            role = '**AI**'
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
    

@st.cache_data()
def Create_LLM(model_id:str, max_new_tokens:int):

    llm_hf = None
    if "Mixtral" in model_id:
        llm_hf = HuggingFaceEndpoint(
            repo_id=model_id, 
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            token=HUGGINGFACEHUB_API_TOKEN,
        )
    elif "Qwen" in model_id:
        llm_hf = HuggingFaceEndpoint(
            repo_id=model_id, 
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            token=HUGGINGFACEHUB_API_TOKEN,
        )
    else:
        llm_hf = HuggingFaceHub(
            repo_id=model_id,
            model_kwargs={"temperature": 0.7, 
                          "max_new_tokens": max_new_tokens, 
                          "return_full_text": False, 
                          "repetition_penalty" : 1.2}
        )

    return llm_hf

@st.cache_data()
def Create_Model_Chain(model_id:str, max_new_tokens:int):

    llm_hf = Create_LLM(model_id, max_new_tokens)

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

    args = parse_args(sys.argv[1:])
    st.session_state.is_local = args.local
    
    Main_Title(st.session_state.locale.title[0] + " (v0.0.2)")

    if st.session_state.locale == en:
        if st.session_state.is_local:
            version = st.selectbox(st.session_state.locale.choose_llm_prompt[0], ("Mixtral-8x7B-Instruct", "CodeQwen1.5-7B-Chat"))
        else:
            version = st.selectbox(st.session_state.locale.choose_llm_prompt[0], ("Mixtral-8x7B-Instruct",)) # CodeQwen cannot be deployed on streamlit space -(
    else:
        if st.session_state.is_local:
            version = st.selectbox(st.session_state.locale.choose_llm_prompt[0], ("CodeQwen1.5-7B-Chat", "Mixtral-8x7B-Instruct", ))
        else:
            version = st.selectbox(st.session_state.locale.choose_llm_prompt[0], ("Mixtral-8x7B-Instruct", ))
    
    if version == "Mixtral-8x7B-Instruct":
        # Use Mixtral model
        st.session_state.llm = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        st.session_state.max_new_tokens = 4096
    elif version.startswith("CodeQwen"):
        st.session_state.llm = "Qwen/CodeQwen1.5-7B-Chat"
        st.session_state.max_new_tokens = 4096
    else:
        # Use Mixtral model
        st.session_state.llm = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        st.session_state.max_new_tokens = 4096


    # ====== Build Model Chain ========
    chain = Create_Model_Chain(st.session_state.llm, st.session_state.max_new_tokens)

    ## ----- AI Role  --------
    st.session_state.role_placeholder = st.empty()        # showing system role selected
    st.session_state.role_placeholder = st.info(st.session_state.locale.role_tab_label[0] + ": **" + st.session_state["context_select" + current_user + "value"] + "**")

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

    ## ----- Chat Tab  --------
    with tab_chat:
        msg_placeholder = st.empty()

        ## ----- Show Previous Chats if Any --------
        Show_Messages(msg_placeholder)
        st.session_state.gtts_placeholder = st.empty()

        st.session_state.uploading_file_placeholder = st.empty()
        st.session_state.buttons_placeholder = st.empty()
        st.session_state.input_placeholder = st.empty()

        with st.session_state.uploading_file_placeholder:
            col1, col2 = st.columns(spec=[4,1])
            with col1:
                uploaded_file = st.file_uploader(label=st.session_state.locale.file_upload_label[0], type=['docx', 'txt', 'pdf', 'csv'],key=st.session_state.key, accept_multiple_files=False,)
                if uploaded_file is not None:
                    #bytes_data = uploaded_file.read()
                    st.session_state.loaded_content = libs.GetContexts(uploaded_file)
                    st.session_state.enable_search = False
            with col2:
                st.write("")
                st.write("")
                st.write("")
                st.session_state.clear_doc_button = st.button(label=st.session_state.locale.clear_doc_btn[0], key="clearDoc", on_click=Delete_Files)

        with st.session_state.buttons_placeholder:
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.new_topic_button = st.button(label=st.session_state.locale.chat_clear_btn[0], key="newTopic", on_click=Clear_Chat)
####### UNABLE to RUN on streamlit.app ##########################
#            with c2:
#                st.session_state.enable_search = st.checkbox(label=st.session_state.locale.enable_search_label[0], value=st.session_state.enable_search)
#################################################################
        with st.session_state.input_placeholder.form(key="my_form", clear_on_submit = True):
            user_input = st.text_area(label=st.session_state.locale.chat_placeholder[0], value=st.session_state.user_text, max_chars=6000)
            send_button = st.form_submit_button(label=st.session_state.locale.chat_run_btn[0])

        if send_button :
            print(f"{st.session_state.user}: {user_input}")
            user_input = user_input.strip()
            if(user_input != ''):
                lang = detect(user_input)
                if st.session_state.enable_search:
                    #st.session_state.loaded_content = libs.Search_WiKi(user_input)
                    st.session_state.loaded_content = libs.Search_DuckDuckGo(user_input)
                    #print(st.session_state.loaded_content)
                if st.session_state.loaded_content != "":
                    prompt = f"<CONTEXT>{st.session_state.loaded_content}</CONTEXT>\n\n {user_input}"
                else:
                    prompt = user_input
                    
                if lang in ['zh', 'zh-cn']:
                    prompt = "The human can only understand Chinese. Please provide your response in Chinese!\n\n" + prompt
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
                Show_Audio_Player(generated_text)

                save_log(user_input.strip(), generated_text, st.session_state.total_tokens)

##############################
if __name__ == "__main__":

    # Initiaiise session_state elements
    if "locale" not in st.session_state:
        st.session_state.locale = en

    if "lang_index" not in st.session_state:
        st.session_state.lang_index = 0
        
    if "user_ip" not in st.session_state:
        st.session_state.user_ip = get_client_ip()

    if "is_local" not in st.session_state:
        st.session_state.is_local = False

    if "loaded_content" not in st.session_state:
        st.session_state.loaded_content = ""

    if "enable_search" not in st.session_state:
        st.session_state.enable_search = False

    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    if 'max_new_tokens' not in st.session_state:
        st.session_state.max_new_tokens = 1024

    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0

    if 'key' not in st.session_state:
        st.session_state.key = str(randint(1000, 10000000))    

    if "messages" not in st.session_state:
        st.session_state.messages = EN_BASE_PROMPT
    
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

    language = st.sidebar.selectbox(st.session_state.locale.choose_language[0], ("English", "中文"), index=st.session_state.lang_index)
    if language == "English":
        st.session_state.locale = en
        st.session_state.lang_index = 0
    else:
        st.session_state.locale = zw
        st.session_state.lang_index = 1
        
    #st.sidebar.button(st.session_state.locale.chat_clear_btn[0], on_click=Clear_Chat)
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


    
