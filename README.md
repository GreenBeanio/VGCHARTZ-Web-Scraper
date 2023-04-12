# VGCHARTZ Web Scraper

## What Does It Do?

This scrapes the VGCHARTZ website to get information about video game sales.

# Reason For Creation

 I made this for an assignment in one of my Data Science courses. I made it because the [Kaggle database](https://www.kaggle.com/datasets/gregorut/videogamesales) that I was going to use was from 2016, with full years only up to 2015. I was able to find the code used to scrape the [original data set](https://github.com/GregorUT/vgchartzScrape). However, it was also outdated, and I wasn't able to get it to work. I haven't made a web scraper before, and I wanted to try and make one; so, I did. Note that the scrape will take quite a long time depending on the amount of requests you wish to pull.

# Which Script Should I Use?

I would recommend using the "vgchartz_scraper.py" script instead of "vgchartz_scraper_full.py". "vgchartz_scraper.py" filters out the games that are actually "Series" and "All". Meaning that it filters out video games that aren't actually a single video game. If you want to have statistics for a total Series and a single game across all platforms, it's published on consolidated into one entry then use "vgchartz_scraper_full.py". If you want to have statistics for **only** the actual individual video games on individual platforms, then use "vgchartz_scraper.py".

# Shout-Out

Shout-out to [Gregory Smith](https://github.com/GregorUT) for making the original data set and inspiring this web scraper.

# Running The Python Scripts

### Windows

- Initial Run
  - cd /your/folder
  - python3 -m venv env
  - call env/Scripts/activate.bat
  - python3 -m pip install -r requirements.txt
  - Depending on which script
    - python3 vgchartz_scraper.py
    - python3 vgchartz_scraper_full.py
- Running After
  - cd /your/folder
  - Depending on which script
    - call env/Scripts/activate.bat && python3 vgchartz_scraper.py
    - call env/Scripts/activate.bat && python3 vgchartz_scraper_full.py
- Running Without Terminal Staying Around
  - Change the file type from py to pyw
  - You should just be able to click the file to launch it
  - May need to also change python3 to just python if it doesn't work after the change
    - In the first line of the code change python3 to python

### Linux

- Initial Run
  - cd /your/folder
  - python3 -m venv env
  - source env/bin/activate
  - python3 -m pip install -r requirements.txt
  - Depending on which script
    - python3 vgchartz_scraper.py
    - python3 vgchartz_scraper_full.py
- Running After
  - cd /your/folder
  - Depending on which script
    - source env/bin/activate && python3 vgchartz_scraper.py
    - source env/bin/activate && python3 vgchartz_scraper_full.py
- Running Without Terminal Staying Around
  - Run the file with nohup
  - May have to set executable if it's not already
    - chmod +x vgchartz_scraper.py
    - chmod +x vgchartz_scraper_full.py
