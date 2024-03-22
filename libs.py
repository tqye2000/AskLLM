from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
import os
import re

set_sys_context = {
    'Chatty Partner':
        "You are an endearing conversational companion",

    '聊天伙伴':
        "你是一个具有爱心和同情心的中文聊天伴侣，你的目标是提供信息、解答问题并进行愉快的对话。请注意：一定要用中文回复！",

    'Python Programmer':
        "You are a Coding Assistant that can generate Python code for data analysis and visualization. "
        "You can use libraries such as pandas, numpy, matplotlib, seaborn, etc. "
        "You should provide clear and concise code that follows the PEP 8 style guide. You should also display the output of the code cells, such as plots or tables. "
        "You should ask for clarification or confirmation from the user if the task is ambiguous or complex.",

    'Python Intepreter':
        'I want you to act like a Python interpreter. I will give you Python code, and you will execute it. Do not '
        'provide any explanations. Do not respond with anything except the output of the code.',

    'Regex Generator':
        "I want you to act as a regex generator. Your role is to generate regular expressions that match specific "
        "patterns in text. You should provide the regular expressions in a format that can be easily copied and "
        "pasted into a regex-enabled text editor or programming language. Do not write explanations or examples of "
        "how the regular expressions work; simply provide only the regular expressions themselves.",

    'Prompt Engineer':
        "You are a Prompt Engineer. You should help me to improve and translate the prompt I provided to English.",

    'English Teacher':
        "I want you to act as an English teacher and improver." 
        "You should correct my grammar mistakes, typos, repahse the sentences with better english, etc.",
    
    'English-Chinese translator':
        "I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one "
        "language and your task is to accurately and academically translate the paragraphs only into the other "
        "language."
        "Do not repeat the original provided paragraphs after translation. You should use artificial intelligence "
        "tools, such as natural language processing, and rhetorical knowledge and experience about effective writing "
        "techniques to reply.",

    "Academic Paper Editor":
        "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, improve the "
        "spelling, grammar, clarity, concision and overall readability."
        "When necessary, rewrite the whole sentence. Furthermore, list all modification and explain the reasons to do "
        "so in markdown table.",

    '英文翻译与改进':
        "在这次会话中，我想让你充当英语翻译员、拼写纠正员和改进员。我会用任何语言与你交谈，你会检测语言，并在更正和改进我的句子后用英语回答。"
        "我希望你用更优美优雅的高级英语单词和句子来替换我使用的简单单词和句子。保持相同的意思，但使它们更文艺。我要你只回复更正、改进，不要写任何解释。",

}

#----------------------------------- 
def get_docx_data(filepath:str) -> str:
    '''
    File types: docx
    '''
    loader = UnstructuredWordDocumentLoader(filepath)

    data = loader.load()
    doc = data[0]

    return doc.page_content

def get_ppt_data(filepath:str) -> str:
    '''
    File types: powerpoint document
    '''
    loader = UnstructuredPowerPointLoader(filepath)
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def get_pdf_data(filepath:str) -> str:
    '''
    File types: pdf
    '''
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def get_unstructured_data(filepath) -> str:
    '''
    File types: text, html
    '''
    loader = UnstructuredFileLoader(filepath)
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def text_preprocessing(filepath:str) -> str:
    '''
    Reading plain text file
    '''
    text =""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    return text

def remove_contexts(input_string):
    # Use regular expression to find and replace content between <S> and </S>
    cleaned_string = re.sub(r"<CONTEXT>.*?</CONTEXT>", "{...}", input_string, flags=re.DOTALL)
    return cleaned_string

def extract_code(text):
    code_regex = r"```(.*?)```"
    code_matches = re.findall(code_regex, text, re.DOTALL)
    print (f"Code extracted: {code_matches}")

    return code_matches

def Read_From_File(filepath:str) -> dict:
    '''
    This function reads file of types [.docx, .pdf, .pptx] or any plain text file, and returns the content of the file.

    Parameters
    ----------
    filepath : str
        The full file path to the file to be read 

    Returns
    -------
    ret : dict
        a dictionary containing the error code and the content of the file
    '''
    ret = {}
    ret['Error'] = 0

    if os.path.exists(filepath):
        try:
            if filepath.split(".")[-1] in ['docx', 'DOCX']:
                ret['Conent'] = get_docx_data(filepath)
                ret['Error'] = 0
            elif filepath.split(".")[-1] in ['pdf', 'PDF']:
                ret['Conent'] = get_pdf_data(filepath)
                ret['Error'] = 0
            elif filepath.split(".")[-1] in ['pptx', 'PPTX']:
                ret['Conent'] = get_ppt_data(filepath)
                ret['Error'] = 0
            else:
                ret['Conent'] = text_preprocessing(filepath)
                ret['Error'] = 0
        except Exception as ex:
            ret['Error'] = f"Failed to read file {filepath}: {ex}"
    else:
        ret['Error'] = f"{filepath} does not exist."

    return ret

from tempfile import NamedTemporaryFile

def GetContexts(uploaded_file):

    Content = ""
    error = 0
    tempFile = ""
    filepath = uploaded_file.name
    try:
        if filepath.split(".")[-1] in ['docx', 'DOCX']:
            with NamedTemporaryFile(suffix="docx", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_docx_data(temp.name)
        elif filepath.split(".")[-1] in ['pdf', 'PDF']:
            with NamedTemporaryFile(suffix="pdf", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_pdf_data(temp.name)
        elif filepath.split(".")[-1] in ['pptx', 'PPTX']:
            with NamedTemporaryFile(suffix="pptx", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = get_ppt_data(temp.name)
        else:
            with NamedTemporaryFile(suffix="txt", delete=False) as temp:
                temp.write(uploaded_file.getbuffer())
                tempFile = temp.name
                Content = text_preprocessing(temp.name)
    except Exception as ex:
        print(f"Loading file content failed: {ex}")
        Content = ""
        error = 1

    if os.path.exists(tempFile):
        try:
            os.remove(tempFile)
        except Exception as ex:
            pass

    return Content

