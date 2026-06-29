from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config.loader import llm_model
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

def generation(retriever, prompt, question):
    template = ChatPromptTemplate.from_template(prompt)
    llm = ChatGoogleGenerativeAI(
        model = llm_model,
        temperature = 0.1,
        google_api_key = os.getenv("GEMINI_API_KEY")
    )
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | template
        | llm
        | StrOutputParser()
    )
    return rag_chain.invoke(question)

