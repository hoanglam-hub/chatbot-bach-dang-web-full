from langchain_community.document_loaders import DirectoryLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.loader import chunk_size, chunk_overlap
import os

direction = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_and_chunk():
    loader = DirectoryLoader(
        path=os.path.join(direction, "dataRaw"),
        glob="**/*.*",
        loader_cls = lambda path: UnstructuredLoader(
        file_path=path,
        strategy="fast",
        mode="single",
        ),
        show_progress = True,
    )
    doc = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    chunks = splitter.split_documents(doc)
    return chunks



