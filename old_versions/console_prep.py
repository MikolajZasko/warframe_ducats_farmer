"""console_prep.py

Preps the console - first script lauched from the ps1 file - main entry point
"""

# imports
from pathlib import Path
import sys

# Get the root directory (parent of config and scripts directories) and add it to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# modules
from config import helper_functions

helper_functions.prep_console()