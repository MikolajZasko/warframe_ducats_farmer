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

# Global state
last_mtime = None
current_data = []
current_page = 0
ITEMS_PER_PAGE = 20

#
# button functions
#
def fetch_item_info_button_action():
    subprocess.run([sys.executable, settings.scripts_path / "item_info_json_fetch.py"])

def fetch_deals_button_action():
    # Disable button & show small sidebar spinner
    fetch_deals_button.configure(state="disabled")
    button_progress_bar.pack(padx=10, pady=(0, 5))
    button_progress_bar.start()

    thread = threading.Thread(
        target=run_prime_junk,
        daemon=True  # dies with the app, won't hang on exit
    )
    thread.start()

#
# script & UI sync functions
#
def run_prime_junk():
    # Runs full script execution
    subprocess.run([sys.executable, settings.scripts_path / "primeJunk_v4.py"])
    # Re-enable button ONLY when script completely finishes
    app.after(0, on_prime_junk_complete)

def on_prime_junk_complete():
    button_progress_bar.stop()
    button_progress_bar.pack_forget()
    fetch_deals_button.configure(state="normal")

def watch_json_file():
    global last_mtime
    path = settings.deals_json_path

    try:
        mtime = os.path.getmtime(path)
        if mtime != last_mtime:
            last_mtime = mtime
            start_json_spinner()
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            update_ui_with_data(data)
            stop_json_spinner()
    except (FileNotFoundError, PermissionError):
        # Gracefully handle file read collisions on Windows
        pass

    # check again in 10 seconds
    app.after(10000, watch_json_file)

def start_json_spinner():
    status_label.configure(text="Updating list...")
    progress_bar.pack(side="right", padx=(10, 0))
    progress_bar.start()

def stop_json_spinner():
    progress_bar.stop()
    progress_bar.pack_forget()
    status_label.configure(text="Up to date ✓")
    app.after(2000, lambda: status_label.configure(text=""))

def copy_to_clipboard(text):
    app.clipboard_clear()
    app.clipboard_append(text)
    app.update()

def update_ui_with_data(data):
    global current_data, current_page
    if isinstance(data, dict):
        current_data = [{"ducat_avg": k, "message": v} for k, v in data.items()]
    else:
        current_data = data
    current_page = 0
    populate_table()

def build_table_header():
    header_font = customtkinter.CTkFont(weight="bold")
    customtkinter.CTkLabel(table_frame, text="Ducat AVG", font=header_font).grid(
        row=0, column=0, padx=10, pady=(5, 10), sticky="w"
    )
    customtkinter.CTkLabel(table_frame, text="Message", font=header_font).grid(
        row=0, column=1, padx=10, pady=(5, 10), sticky="w"
    )

# from slide menu to pages to avoid lag when scrolling
def populate_table():
    # Remove existing row widgets (keeping headers at index 0 and 1)
    for widget in table_frame.winfo_children()[2:]:
        widget.destroy()

    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = current_data[start_idx:end_idx]

    for i, item in enumerate(page_items, start=1):
        ducat_avg = item.get("ducat_avg", "")
        message = item.get("message", "")

        customtkinter.CTkLabel(table_frame, text=str(ducat_avg)).grid(
            row=i, column=0, padx=10, pady=2, sticky="w"
        )

        message_label = customtkinter.CTkLabel(
            table_frame, text=str(message), cursor="hand2"
        )
        message_label.grid(row=i, column=1, padx=10, pady=2, sticky="w")
        message_label.bind("<Button-1>", lambda e, msg=message: copy_to_clipboard(msg))

    update_pagination_controls()

def update_pagination_controls():
    total_pages = max(1, (len(current_data) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page_info_label.configure(text=f"Page {current_page + 1} of {total_pages}")
    
    prev_page_button.configure(state="normal" if current_page > 0 else "disabled")
    next_page_button.configure(state="normal" if current_page < total_pages - 1 else "disabled")

def prev_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        populate_table()

def next_page():
    global current_page
    total_pages = (len(current_data) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if current_page < total_pages - 1:
        current_page += 1
        populate_table()

#
# app settings
#
app = customtkinter.CTk()
app.geometry("1280x720")

# --- configure main window grid ---
app.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
app.grid_columnconfigure(1, weight=1)  # Table expands
app.grid_rowconfigure(0, weight=1)     # Main content expands
app.grid_rowconfigure(1, weight=0)     # Bottom control bar fixed

# --- LEFT: sidebar with buttons ---
sidebar = customtkinter.CTkFrame(app, width=160)
sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

# Sidebar widgets
fetch_item_info_button = customtkinter.CTkButton(sidebar, text="fetch item info", command=fetch_item_info_button_action)
fetch_item_info_button.pack(fill="x", padx=10, pady=(10, 5))

fetch_deals_button = customtkinter.CTkButton(sidebar, text="fetch links", command=fetch_deals_button_action)
fetch_deals_button.pack(fill="x", padx=10, pady=5)

# Compact spinner directly under "fetch links" (width=120, height=6 prevents UI stretch)
button_progress_bar = customtkinter.CTkProgressBar(sidebar, mode="indeterminate", width=120, height=6)

# --- RIGHT: Table Frame ---
table_frame = customtkinter.CTkFrame(app)
table_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))
build_table_header()

# --- BOTTOM RIGHT: Single Merged Controls & Status Frame ---
bottom_frame = customtkinter.CTkFrame(app, fg_color="transparent")
bottom_frame.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

# Pagination controls (Left aligned)
prev_page_button = customtkinter.CTkButton(bottom_frame, text="< Prev", width=60, command=prev_page)
prev_page_button.pack(side="left", padx=(0, 5))

page_info_label = customtkinter.CTkLabel(bottom_frame, text="Page 1 of 1")
page_info_label.pack(side="left", padx=5)

next_page_button = customtkinter.CTkButton(bottom_frame, text="Next >", width=60, command=next_page)
next_page_button.pack(side="left", padx=(5, 0))

# Status & Spinner widgets for JSON updates (Right aligned inside bottom bar)
progress_bar = customtkinter.CTkProgressBar(bottom_frame, mode="indeterminate", width=120)

status_label = customtkinter.CTkLabel(bottom_frame, text="")
status_label.pack(side="right", padx=5)

app.after(0, watch_json_file)
app.mainloop()