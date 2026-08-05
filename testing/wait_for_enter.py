import sys
from pathlib import Path

# gemini's way to get modules "up" in a directory
# 1. Get the path of the current file, go UP one directory to the root ('project/')
parent_dir = Path(__file__).resolve().parent.parent

# 2. Add that parent directory to Python's path list
sys.path.append(str(parent_dir))

# modules
from config import settings
from config import helper_functions

helper_functions.wait_for_enter_and_quit()