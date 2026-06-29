from markitdown import MarkItDown
import os
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

def markitdown_loader():
    md = MarkItDown()
    direction = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataRaw")
    docs = []
    for file in os.listdir(direction):
        file_path = os.path.join(direction, file)
        result = md.convert(file_path)
        # chuyển result thành dạng Document của langchain để có thể split (vì result đang ở dạng của markitdown nên không split trực tiếp được)
        document = Document(page_content = result.text_content, metadata = {"source": file})
        docs.append(document)
        logger.info("process loader done!")
    return docs
