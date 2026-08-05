# activate virtual environment
.\venv\Scripts\activate.bat

# gather links using the first python script
python primeJunk_get_links.py

# scrape the market in search of best deals
python primeJunk_v3.py

# deactivate virtual environment
deactivate