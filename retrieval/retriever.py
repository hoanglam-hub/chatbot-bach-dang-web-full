from langchain_community.vectorstores import FAISS

def get_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.2})
    return retriever
