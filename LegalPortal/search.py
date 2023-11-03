from langchain.llms import OpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.chains import LLMChain
import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from .LLM import llm,embeddings,app
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from embedchain import App
from string import Template
from embedchain.config import LlmConfig
from langchain.utilities import SerpAPIWrapper


params = {
    "engine": "google",
    "gl":"in",
    "serpapi_api_key": "4192c4adf2893f3987b111e7779bc9fdf6fea8fcca47a502739bfe844aed2583"
}
search = SerpAPIWrapper(params=params,serpapi_api_key="4192c4adf2893f3987b111e7779bc9fdf6fea8fcca47a502739bfe844aed2583")
bot = app()

llm_config = LlmConfig(system_prompt="You are a legal assistant and tell citizens of India about the laws & acts in India. Your task is to explain the law in a simplified manner from the text you have received.  Only answer question pertaining to the domain of laws & regualtions in India, do not answer any other questions and for such questions prompt the user - 'Ask Questions pertaining to legal issues'.")

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a legal assistant and advice people on legal issues according to the laws of India. Your task is to answer the following question delimited by triple backticks. Strictly answer question pertaining to the domain of legal issue in India, do not answer any other question and for such questions prompt the user - 'Ask Questions pertaining to legal issues'."), # The persistent system prompt
    MessagesPlaceholder(variable_name="chat_history"), # Where the memory will be stored.
    HumanMessagePromptTemplate.from_template("{human_input}"), # Where the human input will injected
])

memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True,k=2)

model = llm()
chat_llm_chain = LLMChain(
    llm=model,
    prompt=prompt,
    verbose=True,
    memory=memory,
)
current_date = datetime.date.today()
current_date = str(current_date)

def predict_unofficial(query):
    global memory
    web_results = search.run(query)
    prompt = f"""
    Question:
    ```{query}```

    For the answer to the question:
    Always try to use your existing knowledge to answer the question if possible. If the question does not need the search results to be answered, just answer it directly.
    It's possible that the question, or just a portion of it, requires relevant
    information from the internet to give a satisfactory answer.
    The relevant search results provided below, delimited by triple backticks,
    are the necessary information already obtained from the internet.
    The search results set the context for addressing the question,
    so you don't need to access the internet to answer the question.

    If the search results lack the needed details, and you're unsure about the answer,
    just respond 'Invalid search results.
    Consider rephrasing your question or adjusting search options like the number of results or the search engine used.
    If the question requires the search results, use the following
    Search results:
    ```{web_results}```

    For your reference, today's date is {current_date}.

    ---

    Use the following format for the answer:
    <answer to the question>

    ---
    Make the answer as short as possible, ideally no more than 200 words."""
    try:
        answer=chat_llm_chain.predict(human_input=prompt)
    except:
        # memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True,k=2)
        answer=chat_llm_chain.predict(human_input=prompt)
    return answer

from serpapi import GoogleSearch

def serpAPIsearch(params):
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results["organic_results"]
    for i in range(len(organic_results)):
        if ("gov.in" in organic_results[i]["link"]) or ("nic.in" in organic_results[i]["link"]):
            return organic_results[i]
        
    return None

def info_finder(query):
    params = {
    "engine": "google",
    "q": query,
    "gl":"in",
    "api_key": "4192c4adf2893f3987b111e7779bc9fdf6fea8fcca47a502739bfe844aed2583" #api key for serp API
    }
    return serpAPIsearch(params)

def desc(query,link):
    bot.add(link)
    # llm_config = LlmConfig(template=einstein_chat_template, system_prompt="You are Albert Einstein.")
    # response = einstein_chat_bot.query(query, config=llm_config)
    question = f"The question asked by the user is: '{query}'. Mention the date on which it was made effective. Then give a simple 2 line description of the law."
    response = bot.query(question, config=llm_config)
    return response

def predict(query):
    info=info_finder(query)
    print(info)
    resposeDict = {}
    if info!=None:
        resposeDict['link'] = info['link']
        resposeDict['description'] = desc(query,info['link'])    #see what is to be returned
    else:
        info=predict_unofficial(query)
        resposeDict['link'] = None
        resposeDict['description'] = info
    return resposeDict

def get_chain(pages):
    embedding = embeddings()
    vectorstore = Chroma.from_documents(pages, embedding)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')
    qa2 = ConversationalRetrievalChain.from_llm(model, vectorstore.as_retriever(),return_source_documents=True,
                                                memory=memory)
    return qa2