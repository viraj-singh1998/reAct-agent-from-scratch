from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.schema import Document
import tempfile
from typing import List

def store_chunks_in_vector_store(chunks: List[Document]):
    persist_dir = tempfile.mkdtemp()
    print(f'vector store temporarily persisted at {persist_dir}')
    # embedding_model = CohereEmbeddings(model="embed-english-v3.0")
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    # embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    # embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
    # embedding_model = GPT4AllEmbeddings()
    vector_store = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    vector_store.add_texts(texts=texts, metadatas=metadatas)
    vector_store.persist()
    return vector_store