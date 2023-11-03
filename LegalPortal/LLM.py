from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from embedchain import App
from dotenv import load_dotenv
import os

def llm():
    load_dotenv('key.env')
    model = OpenAI(openai_api_key="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")

    return model

def embeddings():
    load_dotenv('key.env')
    embeddings = OpenAIEmbeddings(openai_api_key="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")

    return embeddings

def app():
    os.environ["OPENAI_API_KEY"] = "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"
    bot = App()
    return bot