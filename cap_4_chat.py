# -*- coding: utf-8 -*-
"""
@author: ncs
"""

import tkinter as tk
import subprocess
import time
from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

OLLAMA_MODEL = "deepseek-r1"
OLLAMA_EMBEDDING_MODEL = "all-minilm"

def start_ollama():
    try:
        subprocess.run(["ollama", "list"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama is already running.")
        return True
    except subprocess.CalledProcessError:
        print("Ollama is not running. Starting Ollama...")
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Error starting Ollama: {e}")
            return False

def setup_retrieval_qa(collection_name="k-10s", persist_directory="./chroma_langchain_db", embedding_model=OLLAMA_EMBEDDING_MODEL, 
                       llm_model=OLLAMA_MODEL, template="""Use the following pieces of context to answer the 
                       question at the end. If you don't know the answer, just say that you don't know, don't try to make up 
                       an answer. Use 4 sentences maximum. Keep the answer as concise as possible. {context} Question: 
                           {question} Helpful Answer:"""):
    embeddings = OllamaEmbeddings(model=embedding_model)
    db = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)
    llm = OllamaLLM(model=llm_model)
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever(search_kwargs={"k": 8}), return_source_documents=True, 
                                           chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
    return qa_chain

def process_query(qa_chain, question):
    result = qa_chain.invoke({"query": question})
    answer = result['result'].split("</think>\n\n")[1].strip()
    return result

def main():
    start_ollama()
    qa_chain = setup_retrieval_qa()
    #Add tinker here#
    def submit():
        prompt = prompt_entry.get("1.0", tk.END).strip()

        response = process_query(qa_chain, prompt)

        #This is where u can adjust result to trouble shoot
        result_text.set(f"{
            [response['source_documents'][i].metadata['ticker'] for i in range(len(response['source_documents']))]}")
        
    root = tk.Tk()
    root.title("10-K SEC LLM")
    root.geometry("600x600")
    root.configure(padx=10, pady=10)
    
    tk.Label(root, text="Enter Question:").grid(row=0, column=0, sticky="w")
    prompt_entry = tk.Text(root, height=5, width=40)
    prompt_entry.grid(row=1, column=0, columnspan=2, pady=5)
    
    tk.Button(root, text="Submit", command=submit).grid(row=5, column=0, columnspan=2, pady=10)
    
    result_frame = tk.Frame(root, height=100, width=380, relief=tk.SUNKEN, borderwidth=2)
    result_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky="nsew")
    result_frame.grid_propagate(False)

    result_text = tk.StringVar()
    result_label = tk.Label(result_frame, textvariable=result_text, wraplength=360, justify="left")
    result_label.pack(fill="both", expand=True, padx=5, pady=5)

    root.mainloop()
    
    
    
qa_chain = setup_retrieval_qa() #Delete
test=process_query(qa_chain, 'how has covid impacted our business') #Delete

if __name__ == "__main__":
    main()