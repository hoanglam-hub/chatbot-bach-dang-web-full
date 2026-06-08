import yaml
import os

direction = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(direction, "config/config.yaml"), "r") as f:
    cfg = yaml.safe_load(f)

embedding_model = cfg["EMBEDDING"]["model"]
llm_model = cfg["LLM"]["model"]
chunk_size = cfg["CHUNKING"]["size"]
chunk_overlap = cfg["CHUNKING"]["overlap"]
vectorstore_path = cfg["VECTORSTORE"]["path"]
