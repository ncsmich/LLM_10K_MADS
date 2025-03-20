# WHILE HEAVILY EDITED, MOST OF THIS CODE WAS WRITTEN BY CHAT-GPT
import tkinter as tk
from tkinter import ttk
import csv
import os
from datetime import datetime


def llm_function(prompt, ticker, model, num_docs):
    return (f"{ticker} ___ {model} ___ {num_docs} ___ {prompt}", ['aapl_1','aapl_2','aapl_3'], ['AAPL','AAPL','AAPL'])


def submit():
    prompt = prompt_entry.get("1.0", tk.END).strip()
    ticker = ticker_var.get()
    model = model_var.get()
    num_docs = num_docs_var.get()

    response, docs_ids, docks_ticker = llm_function(prompt = prompt, ticker = ticker, model = model, num_docs = num_docs)

    result_text.set(f"{response}")  # Simulated response

    # Log result to CSV
    file_exists = os.path.isfile("llm_results.csv")
    with open("llm_results.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Prompt", "Ticker", "Model", "Num_Docs","Doc_Ids","Doc_Ticker", "Response", "Time"])
        writer.writerow([prompt, ticker, model, num_docs, docs_ids, docks_ticker, response, datetime.now()])



# Initialize main window
root = tk.Tk()
root.title("10-K SEC LLM")
root.geometry("400x300")
root.configure(padx=10, pady=10)

# Prompt label and text box
tk.Label(root, text="Enter Question:").grid(row=0, column=0, sticky="w")
prompt_entry = tk.Text(root, height=5, width=40)
prompt_entry.grid(row=1, column=0, columnspan=2, pady=5)

# Ticker selection
tk.Label(root, text="Select Ticker (ALL if want to look at all documents):").grid(row=2, column=0, sticky="w")
ticker_var = tk.StringVar()
ticker_dropdown = ttk.Combobox(root, textvariable=ticker_var, values=["ALL", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])
ticker_dropdown.grid(row=2, column=1, pady=5)
ticker_dropdown.current(0)

# Model selection
tk.Label(root, text="Select LLM Model):").grid(row=3, column=0, sticky="w")
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(root, textvariable=model_var, values=["GPT-4", "Claude 3", "Gemini 1.5", "Mistral 7B"])
model_dropdown.grid(row=3, column=1, pady=5)
model_dropdown.current(0)

# Number of documents selection
tk.Label(root, text="Number of Documents To Retrieve:").grid(row=4, column=0, sticky="w")
num_docs_var = tk.IntVar(value=5)
tk.Spinbox(root, from_=1, to=100, textvariable=num_docs_var, width=5).grid(row=4, column=1, pady=5)

# Submit button
tk.Button(root, text="Submit", command=submit).grid(row=5, column=0, columnspan=2, pady=10)

# Result display
result_frame = tk.Frame(root, height=100, width=380, relief=tk.SUNKEN, borderwidth=2)
result_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky="nsew")
result_frame.grid_propagate(False)

result_text = tk.StringVar()
result_label = tk.Label(result_frame, textvariable=result_text, wraplength=360, justify="left")
result_label.pack(fill="both", expand=True, padx=5, pady=5)


root.mainloop()


#%%
