"""ui_app.py"""
from pathlib import Path
import sys
import customtkinter
import subprocess
import threading
import os
import json

# Path setup
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
from config import settings

class DucatFarmerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")
        self.title("Warframe Ducat Farmer")

        # App State
        self.last_mtime = None
        self.current_data = []
        self.current_page = 0
        self.ITEMS_PER_PAGE = 20

        self.setup_ui()
        self.after(0, self.watch_json_file)

    def setup_ui(self):
        # --- Grid Config ---
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # --- LEFT: Sidebar ---
        self.sidebar = customtkinter.CTkFrame(self, width=160)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.btn_info = customtkinter.CTkButton(self.sidebar, text="fetch item info", command=self.fetch_item_info_action)
        self.btn_info.pack(fill="x", padx=10, pady=(10, 5))

        self.btn_deals = customtkinter.CTkButton(self.sidebar, text="fetch links", command=self.fetch_deals_action)
        self.btn_deals.pack(fill="x", padx=10, pady=5)

        self.btn_progress = customtkinter.CTkProgressBar(self.sidebar, mode="indeterminate", width=120, height=6)

        # --- RIGHT: Table Frame ---
        self.table_frame = customtkinter.CTkFrame(self)
        self.table_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))
        self.build_table_header()

        # --- BOTTOM RIGHT: Controls ---
        self.bottom_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

        # Pagination controls
        self.btn_prev = customtkinter.CTkButton(self.bottom_frame, text="< Prev", width=60, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=(0, 5))

        self.page_info_label = customtkinter.CTkLabel(self.bottom_frame, text="Page 1 of 1")
        self.page_info_label.pack(side="left", padx=5)

        self.btn_next = customtkinter.CTkButton(self.bottom_frame, text="Next >", width=60, command=self.next_page)
        self.btn_next.pack(side="left", padx=(5, 10))

        # Go-To Page Controls
        self.goto_entry = customtkinter.CTkEntry(self.bottom_frame, width=45, placeholder_text="#")
        self.goto_entry.pack(side="left", padx=(0, 5))
        
        self.btn_goto = customtkinter.CTkButton(self.bottom_frame, text="Go", width=40, command=self.goto_page)
        self.btn_goto.pack(side="left")

        # Status & Spinner
        self.progress_bar = customtkinter.CTkProgressBar(self.bottom_frame, mode="indeterminate", width=120)
        self.status_label = customtkinter.CTkLabel(self.bottom_frame, text="")
        self.status_label.pack(side="right", padx=5)

        # --- KEYBOARD BINDINGS ---
        self.goto_entry.bind("<Return>", self.goto_page)
        self.bind("<Left>", self.prev_page)
        self.bind("<Right>", self.next_page)

    # --- Actions & Threads ---
    def fetch_item_info_action(self):
        subprocess.run([sys.executable, settings.scripts_path / "item_info_json_fetch.py"])

    def fetch_deals_action(self):
        self.btn_deals.configure(state="disabled")
        self.btn_progress.pack(padx=10, pady=(0, 5))
        self.btn_progress.start()
        threading.Thread(target=self.run_prime_junk, daemon=True).start()

    def run_prime_junk(self):
        subprocess.run([sys.executable, settings.scripts_path / "primeJunk_v4.py"])
        self.after(0, self.on_prime_junk_complete)

    def on_prime_junk_complete(self):
        self.btn_progress.stop()
        self.btn_progress.pack_forget()
        self.btn_deals.configure(state="normal")

    # --- JSON Watching ---
    def watch_json_file(self):
        path = settings.deals_json_path
        try:
            mtime = os.path.getmtime(path)
            if mtime != self.last_mtime:
                self.last_mtime = mtime
                self.start_json_spinner()
                self.update_idletasks()
                
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.update_ui_with_data(data)
                self.after(600, self.stop_json_spinner)
        except (FileNotFoundError, PermissionError):
            pass
        self.after(10000, self.watch_json_file)

    def start_json_spinner(self):
        self.status_label.configure(text="Updating list...")
        self.progress_bar.pack(side="right", padx=(10, 0))
        self.progress_bar.start()

    def stop_json_spinner(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_label.configure(text="Up to date ✓")
        self.after(2000, lambda: self.status_label.configure(text=""))

    # --- Data & Table Management ---
    def update_ui_with_data(self, data):
        if isinstance(data, dict):
            self.current_data = [{"ducat_avg": k, "message": v} for k, v in data.items()]
        else:
            self.current_data = data

        # Remember page logic: prevent current_page from exceeding new data bounds
        total_pages = max(1, (len(self.current_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1

        self.populate_table()

    def build_table_header(self):
        header_font = customtkinter.CTkFont(weight="bold")
        customtkinter.CTkLabel(self.table_frame, text="Ducat AVG", font=header_font).grid(row=0, column=0, padx=10, pady=(5, 10), sticky="w")
        customtkinter.CTkLabel(self.table_frame, text="Message", font=header_font).grid(row=0, column=1, padx=10, pady=(5, 10), sticky="w")

    def populate_table(self):
        for widget in self.table_frame.winfo_children()[2:]:
            widget.destroy()

        start_idx = self.current_page * self.ITEMS_PER_PAGE
        end_idx = start_idx + self.ITEMS_PER_PAGE
        page_items = self.current_data[start_idx:end_idx]

        for i, item in enumerate(page_items, start=1):
            msg = item.get("message", "")
            customtkinter.CTkLabel(self.table_frame, text=str(item.get("ducat_avg", ""))).grid(row=i, column=0, padx=10, pady=2, sticky="w")
            
            msg_lbl = customtkinter.CTkLabel(self.table_frame, text=str(msg), cursor="hand2")
            msg_lbl.grid(row=i, column=1, padx=10, pady=2, sticky="w")
            msg_lbl.bind("<Button-1>", lambda e, m=msg: self.copy_to_clipboard(m))

        self.update_pagination_controls()

    # --- Pagination & Utilities ---
    def update_pagination_controls(self):
        total_pages = max(1, (len(self.current_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
        self.page_info_label.configure(text=f"Page {self.current_page + 1} of {total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")

    def prev_page(self, event=None):
        # Ignore global arrow key presses if the user is typing in the entry box
        if event and self.focus_get() == self.goto_entry:
            return
            
        if self.current_page > 0:
            self.current_page -= 1
            self.populate_table()

    def next_page(self, event=None):
        # Ignore global arrow key presses if the user is typing in the entry box
        if event and self.focus_get() == self.goto_entry:
            return
            
        total_pages = (len(self.current_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.populate_table()

    def goto_page(self, event=None):
        try:
            target = int(self.goto_entry.get()) - 1
            total_pages = max(1, (len(self.current_data) + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)
            if 0 <= target < total_pages:
                self.current_page = target
                self.populate_table()
        except ValueError:
            pass  # Ignore invalid string inputs
        finally:
            self.goto_entry.delete(0, "end")
            
        # Optional: Drop focus from the entry box after hitting Enter so arrow keys work again immediately
        if event:
            self.focus_set()

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()