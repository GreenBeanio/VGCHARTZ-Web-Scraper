# VGCHARTZ Web Scraper

## What Does It Do?

This scrapes the VGCHARTZ website to get information about video game sales.

# Reason For Creation

 I made this for an assignment in one of my Data Science courses. I made it because the [Kaggle database](https://www.kaggle.com/datasets/gregorut/videogamesales) that I was going to use was from 2016, with full years only up to 2015. I was able to find the code used to scrape the [original data set](https://github.com/GregorUT/vgchartzScrape). However, it was also outdated, and I wasn't able to get it to work. I haven't made a web scraper before, and I wanted to try and make one; so, I did. Note that the scrape will take quite a long time depending on the amount of requests you wish to pull.

# How to Set it Up

You should be able to run it straight without making any changes. However, you may want to change the following parameters.

- pages
  - This sets the amount of pages you will request.
  - I would try to keep it around a maximum of 1,000 requests per page, but I'm not sure if there's actually a limit on the website. Just so that it isn't too large per page download.
- results_per_page
  - This is how many results will show up per page.
  - Like I said I'd keep it at a maximum of 1,000 requests per page. The websites controls only go up to 200, but I haven't had any trouble requesting 1,000 and it's a large enough size for me.
- use_max_game
  - This is used to toggle True or False if you want the script to end after a certain amount of "All" games.
  - I have this set to True by default, because I am unsure if the script will crash once it reaches the end of the database.
- max_game
  - This is used to set the max number of games that the script will scan if use_max_game is set to True.
  - I have this set at 62,674, because that is the number of entries on the database at the time of this script being written.
  - Note that this will be the number of "All" games not "Kept" games.
- use_specific_start
  - This is used to True or False or True if you want the script to start from a specific "All" game in the database.
- skipped_games
  - This is used to set the amount of games to be skipped if use_specific_start is set to True.
  - Note that this will be the number of "All" games not "Kept" games.
- full_date
  - This is used to toggle True or False if you want the dates to be recorded as YYYY-MM-DD or just YYYY respectively.
- set_attempts
  - This is the amount of attempts that it will make before it crashes.
  - I have this at 40, but if you want it larger or smaller go ahead. If your internet is prone to going out I'd put it up a lot higher so that you don't crash when the internet goes out.
- wait_time
  - This is how long in seconds the script will wait between attempts.
  - I have this set at 15, just because it seems to work so far.
  - The failures that I've had with the script have come from 429 errors. Which is sending too many requests to the website. Increase this time if you're crashing, or the amount of attempts, or both,

# Outputs

This script will output 7 different files to the directory "Output". All numerical units are in millions, except for the tie ratio.

- kept_games.csv
  - This is a csv file will all the games in the database, except for games with the platform "All" and "Series". I don't personally think that seeing the statistics for a game across "All" the platforms on is useful for my purposes. I also don't think it's useful to have the statistics for the game "Series" as a whole.
- all_games.csv
  - This is a csv file with all of the games that where in the database.
- log.txt
  - This is a log of all the events and errors that occurred in the script. As well as how long they took.
- platforms.csv
  - This is a csv of all the codes the website uses to represent the various platforms. As well as the actual platform names that accompany them.
- hardware.csv
  - This is a csv of the sales information of the different hardware platforms.
- software.csv
  - This is a csv of the sales information of the different software for the platforms.
- tie_ratio.csv
  - This is a csv of the tie-ratio for the hardware and software of the platforms.
  - The tie-ratio is how many pieces of software were sold for each piece of hardware.

# I Crashed! What Do I Do?

Fear not! I have added functionality to continue after a crash with hopefully no lost data.

- Open your "all_games.csv" file and find the last "Rank" in it.
  - Make sure that it's "all_games.csv" and not "kept_games.csv" or you will end up with duplicates.
- In the code set the "skipped_games" value to that number.
- Set "use_specific_start" to True.

That should start scraping the website back at the next game.

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
    - python3 vgchartz_scrape.py
- Running After
  - cd /your/folder
  - Depending on which script
    - call env/Scripts/activate.bat && python3 vgchartz_scrape.py
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
    - python3 vgchartz_scrape.py
- Running After
  - cd /your/folder
  - Depending on which script
    - source env/bin/activate && python3 vgchartz_scrape.py
- Running Without Terminal Staying Around
  - Run the file with nohup
    - nohup python3 vgchartz_scrape.py > /dev/null &
  - May have to set executable if it doesn't work
    - chmod +x vgchartz_scrape.py
