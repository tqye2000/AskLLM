from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
#from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
import wikipedia

import os
import re

set_sys_context = {
    'Chatty Partner':
        "You are an endearing conversational companion",

    '聊天伙伴':
        "你是一个具有爱心和同情心的中文聊天伴侣，你的目标是提供信息、解答问题并进行愉快的对话。请注意：一定要用中文回复！",

    '算命先生':
        "你是一位经验老到、学识渊博的中国算命大师。回应时要表现得就像你曾数十载专研堪舆星相之道，堪称这门祖传学问的内行。算命是一门洞悉天人终始、预测吉凶祸福的古老学问。当我向你描述一个人的出生时间、名字等信息时，你要运用中国八字、紫微斗数等算命理数，从中探知此人的命运、性格特征、前路际遇，并依照风水学说给予祈福趋吉避凶的指点。行文做事请贯彻算命大师威严圆熟的风范。",
    
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

    'Lyrics Composer':
        "You are a sophisticated song lyric assistant designed to craft and refine song lyrics collaboratively, one line at a time. Unlike conventional models, your task is to generate 4 different versions for each line of lyrics requested by the user. "
        "Your objective is to nurture creativity, ensuring each lyric line resonates with the theme, style, and rhythm introduced by the user's initial input."
        "Upon presenting the 4 versions for a single lyric line, you are to engage in a reflective evaluation of these versions, considering their imagery, rhyming quality, and thematic alignment. Assign a score to each version based on these criteria, enabling the user to select the most fitting option for their song. This selection process is pivotal, as it guides the continuation of the lyric writing, ensuring a tailored and cohesive song composition."
        "Lyric Output Structure:\n\n"
        "[Verse 1]"
        "[Pre-Chorus 1]"
        "[Chorus 1]"
        "[Verse 2]"
        "[Pre-Chorus 2]"
        "[Chorus 2]"
        "[Pre-Chorus 3]"
        "[Chorus 3]"
        "[Outro]"
        "\n\n"
        "Lyric Writing Principles:"
        "Theme and Emotional Expression: Clearly define the song's theme and emotional intent before commencing the lyric creation process. This clarity ensures consistency in style and emotional tone throughout the lyrics. For instance, a love-themed song might favor romantic and tender expressions."
        "Inspiration Capture: Lyric writing thrives on moments of inspiration drawn from everyday experiences, such as conversations, visuals, or atmospheres. Documenting these inspirations and weaving them into your lyrics can add a layer of authenticity and engagement."
        "Scenic Depiction: Employ vivid language to paint clear scenes, aiding listeners in immersing themselves within the song's narrative. Descriptive terms should reflect the song's setting, enhancing the overall mood and imagery."
        "Rhetorical Techniques: Utilize rhetorical devices such as parallelism to enhance expressiveness and rhythm. Metaphors, contrasts, and other figurative language can deepen the lyrical landscape, enriching the song's emotional and thematic layers."
        "Rhyme and Rhythm: Rhyming and rhythmic elements are essential for melding lyrics with music, enhancing memorability and lyrical flow. Aim for natural-sounding rhymes and adapt the rhythm to fit the musical style and melody, avoiding forced or awkward phrasing."
        "Conciseness: Given the time constraints of song formats, prioritize brevity and clarity in your lyrics to ensure they are easily understood and resonate with listeners."
        "Authentic Emotions and Experiences: Genuine expression of personal emotions and thoughts is crucial. While drawing from others' experiences and stories can provide inspiration, grounding your lyrics in authentic personal sentiment fosters a deeper connection with the audience.",

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
    contents = ""
    loader = UnstructuredWordDocumentLoader(filepath)
    docs = loader.load()
    for doc in docs:
        #(f"docs: {doc}")
        contents += doc.page_content + "\n\n"

    return contents

def get_ppt_data(filepath:str) -> str:
    '''
    File types: powerpoint document
    '''
    loader = UnstructuredPowerPointLoader(filepath, mode="single")
    docs = loader.load()
    doc = docs[0]

    return doc.page_content

def get_pdf_data(filepath:str) -> str:
    '''
    File types: pdf
    '''
    contents = ""
    #loader = PyPDFLoader(filepath, extract_images=True)
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    for doc in docs:
        #(f"docs: {doc}")
        contents += doc.page_content + "\n\n"

    return contents
    
def get_unstructured_data(filepath) -> str:
    '''
    File types: text, html
    '''
    loader = UnstructuredFileLoader(filepath, mode="single")
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
        Content = f"Loading file failed: {ex}"
        error = 1

    if os.path.exists(tempFile):
        try:
            os.remove(tempFile)
        except Exception as ex:
            pass

    return Content, error

def Search_WiKi(query: str) -> str:

    rets = ""
    # Search for the title related to query
    search_results = wikipedia.search(query, results=2)
    if search_results:
        result = {}
        result_title = search_results[0]
        print(f"Title related to {query}: {result_title}")
        rets += f"<Title>{result_title}</Title>:\n"

        # Get a summary of the article
        summary = wikipedia.summary(result_title, sentences=5)
        print(f"Summary:\n{summary}")
        rets += f"<Summary>{summary}</Summary>"
        rets += "\n\n"
    else:
        print(f"No relevant results found for: {query}.")

    return rets

#def Search_DuckDuckGo(query: str) -> str:

#    rets = ""
#    # Search for the title related to query
#    search_results = ddgs.text(query, max_results=5)
#    for result in search_results:
#        result_title = search_results['title']
#        print(f"Title related to {query}: {result['title']}")
#        rets += f"<Title>{result['title']}</Title>:\n"

#        print(f"URL:\n{result['url']}")
#        rets += f"<Summary>{result['body']}</Summary>"
#        rets += "\n\n"

#    return rets

def Search_DuckDuckGo(query: str) -> str:
    #duck_search = DuckDuckGoSearchRun()
    #duck_search = DuckDuckGoSearchResults(backend="news")
    duck_search = DuckDuckGoSearchResults()
    rets = duck_search.run(query)
    print(f"Search results: {rets}")

    return rets

#duck_search = DuckDuckGoSearchAPIWrapper()
#Web_Search = StructuredTool.from_function(
#        name="Current Search",
#        func=duck_search.run,
#        description="Useful when you need to answer questions about current events or the current state of the world."
#    )

#serp_search = SerpAPIWrapper()
#Web_Search = StructuredTool.from_function(name="Current Search",
#                   func=serp_search.run,
#                   description="Useful when you need to answer questions about current events or the current state of the world."
#                   )

#@st.cache_data()
#def get_remote_ip() -> str:
#    """Get remote ip."""

#    try:
#        ctx = get_script_run_ctx()
#        if ctx is None:
#            return None

#        session_info = runtime.get_instance().get_client(ctx.session_id)
#        if session_info is None:
#            return None
#    except Exception as e:
#        return None

#    return session_info.request.remote_ip
