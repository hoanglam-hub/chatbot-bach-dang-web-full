from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config.loader import llm_model
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def generation(retriever, prompt):
    template = ChatPromptTemplate.from_template(prompt)
    llm = ChatOpenAI(
        model = llm_model,
        temperature = 0.1
    )
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | template
        | llm
        | StrOutputParser()
    )

    question = input("question: ")
    answer = rag_chain.invoke(question)
    print(answer)

