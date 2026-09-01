"""simple_ui.py

Creates a simple ui using customtkinter
"""

# imports
from pathlib import Path
import sys
import customtkinter
import subprocess
import threading
import os
import json
import time

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import settings

# variables
last_mtime = None

#
# button functions
#
def fetch_item_info_button():
    subprocess.run([sys.executable, settings.scripts_path / "item_info_json_fetch.py"])

# claude's idea
def fetch_deals_button():
    thread = threading.Thread(
        target=run_prime_junk,
        daemon=True  # dies with the app, won't hang on exit
    )
    thread.start()

#
# other functions
#
def run_prime_junk():
    subprocess.run([sys.executable, settings.scripts_path / "primeJunk_v4.py"])

def watch_json_file():
    global last_mtime
    path = settings.deals_json_path

    try:
        mtime = os.path.getmtime(path)
        if mtime != last_mtime:
            last_mtime = mtime
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            update_ui_with_data(data)
    except FileNotFoundError:
        pass  # file not written yet

    # check again in 1 second
    app.after(1000, watch_json_file)

def update_ui_with_data(data):
    # update your labels/listbox/etc here
    print("UI updated with new data:", data)

def copy_to_clipboard(text):
    app.clipboard_clear()
    app.clipboard_append(text)
    app.update()  # keeps clipboard content after the app loses focus, needed on some platforms

#
# app settings
#
app = customtkinter.CTk()
app.geometry("1280x720")

#
# configure app look - claude
#

# --- configure main window grid ---
app.grid_columnconfigure(0, weight=0)  # sidebar: fixed width
app.grid_columnconfigure(1, weight=1)  # table: expands
app.grid_rowconfigure(0, weight=1)

# --- LEFT: sidebar with buttons ---
sidebar = customtkinter.CTkFrame(app, width=160)
sidebar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
sidebar.grid_propagate(False)  # keeps sidebar width fixed even if content is smaller

#
# table functions - claude
#
def build_table_header():
    header_font = customtkinter.CTkFont(weight="bold")
    customtkinter.CTkLabel(table_frame, text="Ducat AVG", font=header_font).grid(
        row=0, column=0, padx=10, pady=(5, 10), sticky="w"
    )
    customtkinter.CTkLabel(table_frame, text="Message", font=header_font).grid(
        row=0, column=1, padx=10, pady=(5, 10), sticky="w"
    )

def populate_table(data):
    # clear old rows, but keep the header (row 0 = 2 widgets)
    for widget in table_frame.winfo_children()[2:]:
        widget.destroy()

    for i, item in enumerate(data, start=1):
        ducat_avg = item["ducat_avg"]
        message = item["message"]

        # info label - ducats
        customtkinter.CTkLabel(table_frame, text=str(ducat_avg)).grid(
            row=i, column=0, padx=10, pady=2, sticky="w"
        )

        # interactive label - messages (gets copied to clipboard when clicked)
        message_label = customtkinter.CTkLabel(
            table_frame,
            text=str(message),
            cursor="hand2"  # changes cursor to a hand on hover, signals "clickable"
            )
        message_label.grid(row=i, column=1, padx=10, pady=2, sticky="w")
        message_label.bind("<Button-1>", lambda e, msg=message: copy_to_clipboard(msg))

def update_ui_with_data(data):
    # adjust depending on your JSON's actual shape - see note below
    if isinstance(data, dict):
        rows = list(data.items())
    else:
        rows = data  # assume it's already a list of (name, value) pairs
    populate_table(rows)

#
# app elements
#
button1 = customtkinter.CTkButton(sidebar, text="fetch item info", command=fetch_item_info_button)
button1.pack(fill="x", padx=10, pady=(10, 5))

button2 = customtkinter.CTkButton(sidebar, text="fetch links", command=fetch_deals_button)
button2.pack(fill="x", padx=10, pady=5)

table_frame = customtkinter.CTkScrollableFrame(app, label_text="Items")
table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

build_table_header()

app.after(1000, watch_json_file)
app.mainloop()