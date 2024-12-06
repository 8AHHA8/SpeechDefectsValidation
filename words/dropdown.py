import tkinter as tk
from tkinter import StringVar, ttk

def styled_dropdown(master, word_options):
    selected_word = StringVar(value=word_options[0])

    style = ttk.Style()
    style.configure("TCombobox", padding=5, relief="flat", font=("Helvetica", 12))

    word_dropdown = ttk.Combobox(
        master=master,
        values=word_options, 
        state='readonly', 
        width=25
    )
    word_dropdown.pack(pady=5)

    return selected_word