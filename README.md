# canada-negotech-scraper
CLI interface for scraping data from https://negotech.service.canada.ca/search/index.html

## Before running the script
- Download python 3 (recommended 3.6 and newer)
- Install the requests library 
	```pip install requests```
## How to start script
In the project, there are two files - 'main.py' and 'main_full.py'.
### main.py
The 'main.py' working faster, but don't support filters. For start this script you need  execute script in cmd or bash.
### main_full.py
main_full.py support filters. For show all filters write command:
``` python main_full.py -h```
## Control variables
By default, the script creates JSON files with 100 items and doesn't download PDF files (assessments). However, you can change this behavior.
-   Set 'need_download' to 'True' if you want to download all PDF files.
-   Adjust the 'count' variable if you need to scrape more or fewer assessments per request. I do not recommend setting this value higher than 1000.
