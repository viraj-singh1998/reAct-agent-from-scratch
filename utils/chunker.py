from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import PythonCodeTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import Document
from pathlib import Path
from langchain.schema import Document
from typing import List
import ast
import pandas as pd
from glob import glob
import os
from pprint import pprint

def extract_code_blocks(file_content: str):
    """
    Decompose code into logical units (functions, classes)
    """
    tree = ast.parse(file_content)
    blocks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', None)
            if end_line:
                block = file_content.splitlines()[start_line - 1:end_line]
                blocks.append("\n".join(block))
    return blocks

def load_and_chunk_python_files_with_ast(directory_path: str, chunk_size: int = 2000, chunk_overlap: int = 500):
    print(f'directory_path: {directory_path}')
    loader = DirectoryLoader(directory_path, glob="**/*.py", loader_cls=TextLoader)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print('.py files found:')
    pprint([doc.metadata["source"] for doc in documents])

    chunked_docs = []
    for doc in documents:
        file_content = doc.page_content
        source_file = Path(doc.metadata["source"]).name

        # Preprocess into logical units
        blocks = extract_code_blocks(file_content)
        for block in blocks:
            chunks = splitter.split_text(block)
            for chunk in chunks:
                chunked_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": source_file}
                    )
                )
    return chunked_docs

def load_and_chunk_csv_files(directory_path, chunk_size=2000, chunk_overlap=500):
    """
    Chunking csvs files (one or more) present in the specified directory
    
    Args:
    directory_path (str): path containing csv files

    Returns:
    chunked_docs (list): list of langchain.schema.Document objects
    """
    csv_files = glob(os.path.join(os.path.abspath(directory_path), "**/*.csv"), recursive=True)
    print('CSV files found:')
    pprint(csv_files)
    chunked_docs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file).fillna('')
        for index, row in df.iterrows():
            chunk = Document(
                    page_content=row.to_json(),  
                    metadata={
                        "source_file": csv_file, 
                        "row_index": index
                        }
                    )
            chunked_docs.append(chunk)
    return chunked_docs

def load_and_chunk_pdf_files(directory_path: str, chunk_size: int = 2000, chunk_overlap: int = 500):
    """
    Load and chunk PDF files from the specified directory.

    Args:
    directory_path (str): Path containing PDF files.
    chunk_size (int): Maximum size of each chunk.
    chunk_overlap (int): Overlap between chunks.

    Returns:
    list: List of langchain.schema.Document objects.
    """
    pdf_files = glob(os.path.join(os.path.abspath(directory_path), "**/*.pdf"), recursive=True)
    print("PDF files found:")
    pprint(pdf_files)

    chunked_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        documents = loader.load()

        for doc in documents:
            chunks = splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunked_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": pdf_file}
                    )
                )
    return chunked_docs

def load_and_chunk_text_files(directory_path: str, chunk_size: int = 2000, chunk_overlap: int = 500):
    """
    Load and chunk plain text files from the specified directory.

    Args:
    directory_path (str): Path containing text files.
    chunk_size (int): Maximum size of each chunk.
    chunk_overlap (int): Overlap between chunks.

    Returns:
    list: List of langchain.schema.Document objects.
    """
    txt_files = glob(os.path.join(os.path.abspath(directory_path), "**/*.txt"), recursive=True)
    print("Text files found:")
    pprint(txt_files)

    chunked_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    for txt_file in txt_files:
        loader = TextLoader(txt_file)
        documents = loader.load()

        for doc in documents:
            chunks = splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunked_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": txt_file}
                    )
                )
    return chunked_docs

def load_and_chunk_all_files(directory_path: str, chunk_size: int = 2000, chunk_overlap: int = 500):
    chunked_docs = []
    chunked_docs.extend(load_and_chunk_csv_files(directory_path=directory_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    chunked_docs.extend(load_and_chunk_python_files_with_ast(directory_path=directory_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    chunked_docs.extend(load_and_chunk_pdf_files(directory_path=directory_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    chunked_docs.extend(load_and_chunk_text_files(directory_path=directory_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
    return chunked_docs