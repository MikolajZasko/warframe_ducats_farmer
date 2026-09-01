# activate virtual environment
.\.venv\Scripts\activate

# prep console script
python scripts/console_prep.py

# gather items info using the first python script
python scripts/item_info_json_fetch.py

# # gather links using the second python script
# python scripts/primeJunk_get_links.py

# scrape the market in search of best deals
python scripts/primeJunk_v4.py

# deactivate virtual environment
deactivate