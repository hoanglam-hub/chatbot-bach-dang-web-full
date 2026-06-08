from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.loader import chunk_size, chunk_overlap
import os

direction = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_and_chunk():
    loader = PyPDFDirectoryLoader(
        path=os.path.join(direction, "dataRaw"),
        glob="**/*.*",
    )
    doc = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunks = splitter.split_documents(doc)
    return chunks



