# -*- coding: utf-8 -*-
"""
@author: ncs
"""

import glob
import re
from bs4 import BeautifulSoup
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
import os
import subprocess

def start_ollama():
    """Starts the Ollama server."""
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama server started.")
    except FileNotFoundError:
        print("Error: Ollama not found. Make sure it's installed and in your PATH.")
        exit(1)
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        exit(1)

def process_html_file(file_path, embeddings, vector_store):
    """Processes a single HTML file, extracts text, and adds it to the vector store."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        text_list = []
        for div in soup.find_all('div'):
            if not div.find('table'):
                text_list.append(div.get_text(strip=True))

        text_list = [re.sub(r'\xa0', ' ', text) for text in text_list[1:]]

        seen = set()
        to_docs = []
        for text in text_list:
            text = text.lower()
            if text and len(text) > 3 and text not in seen:
                seen.add(text)
                to_docs.append(text)

        ticker = os.path.basename(os.path.dirname(file_path))

        documents_to_add = []
        for tod in to_docs:
            if len(tod) > 50:
                doc = Document(page_content=tod, metadata={"ticker": ticker, "file": file_path})
                documents_to_add.append(doc)

        if documents_to_add:
            vector_store.add_documents(documents_to_add)
            print(f"Added {len(documents_to_add)} documents from {file_path} to vector store.")
        else:
            print(f"Warning: No valid documents found in {file_path}.")

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Main function to process HTML files and add them to the vector store."""
    try:
        start_ollama()
        htm_files = glob.glob('filings/**/*.htm', recursive=True)

        embeddings = OllamaEmbeddings(model="all-minilm")

        vector_store = Chroma(
            collection_name="k-10s",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db")

        for file in htm_files:
            process_html_file(file, embeddings, vector_store)

        print("HTML processing completed.")
    except Exception as e:
        print(f"Critical error in main function: {e}")

if __name__ == "__main__":
    main()