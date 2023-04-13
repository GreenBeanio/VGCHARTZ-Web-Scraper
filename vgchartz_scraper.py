#!/usr/bin/env python3
# Import Packages
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import html5lib
import datetime
import time

# Parameters to set for amount of results
pages = 15
results_per_page = 10  # 1000

# Set to true if you want to use full dates instead of just the years
full_date = False

# Accepted games
accepted_games = 0

# The total results
total_results = pages * results_per_page

# String for holding the output text
output_string = ""

# URL Strings
url_head = "https://www.vgchartz.com/games/games.php?"
url_pages = "page="
url_results = "&results="
url_tail = (
    "&order=Sales&ownership=Both&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&"
    "showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showvgchartzscore=0&showcriticscore=1"
    "&showuserscore=1&showshipped=1"
)

# Create a data frame
df = pd.DataFrame(
    columns=[
        "Rank",
        "Name",
        "Platform",
        "Publisher",
        "Developer",
        "Genre",
        "Critic Score",
        "User Score",
        "Total Shipper",
        "Total Sales",
        "NA Sales",
        "PAL Sales",
        "Japan Sales",
        "Other Sales",
        "Release Date",
        "Last Update",
    ]
)


# Function to convert string to float, check for N/A, and remove the m for millions
def float_covert(str):
    result = ""
    # If the string contains "N/A" set it as nothing
    if "N/A" in str:
        result = np.nan
    else:
        # If the string contains "m" remove the m and converts
        if "m" in str:
            result = np.float64(str[:-1])
        # If it doesn't contain "m" just convert
        else:
            result = np.float64(str)
        # if the value is 0 set it to nothing instead
        if result == 0:
            result = np.nan
    return result


# Function to convert the string to a date, as well as check for N/A
def date_covert(str):
    result = ""
    # If the string contains "N/A" set it as nothing
    if "N/A" in str:
        result = np.nan
    else:
        # Split string into it's parts
        tmp = str.split()
        day = tmp[0]
        month = tmp[1]
        year = tmp[2]
        # Add centuries (if you're using this past 2070, you'll have to figure out what to do here.
        # I could've used %y instead or %Y to use 2 digit years instead of 4, but I don't like that for the future.)
        if int(year) >= 70:
            year = "19" + year
        else:
            year = "20" + year
        # Convert into python date
        if full_date == True:
            # Combine into new string
            strs = year + "-" + month + "-" + day[:-2]
            # Convert into python date
            date = datetime.datetime.strptime(strs, "%Y-%b-%d").date()
            # Finish by converting to numpy date
            result = np.datetime64(date)
        else:
            result = year
    return result


# Function get a list from beautiful soup
def get_list(url, request_type, pages_or_game):
    # Track the number of attempts and if it worked
    attempts = 3
    worked = False
    # Global string
    global output_string
    # For storing the rest
    result = ""
    # Max number of attempts is 3 in this case (change it if you want more chances)
    while attempts > 0:
        # Increase attempt
        attempts -= 1
        # Try to get information from the website
        try:
            # Get the url information
            r = requests.get(url)
            # Beautiful soup the requested information
            soup = BeautifulSoup(r.content, "html5lib")
            # If we're getting the game information
            if request_type == "game":
                # Storing the main reults in the main table
                main_table = soup.find("div", attrs={"id": "generalBody"})
                # Finding hyperlinks in the table
                result = main_table.find_all("a")
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
            # If we're getitng the genre information
            elif request_type == "genre":
                # Find the table
                game_table = soup.find("div", attrs={"id": "gameGenInfoBox"})
                result = game_table.find_all("h2")
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
        # If we don't get the information we were looking for
        except:
            if request_type == "game":
                output_string = f"Error getting game information from page {pages_or_game}"  # need to get variable
            elif request_type == "genre":
                output_string = f"Error getting genre information from the game {pages_or_game}"  # need to get variable
            # Write to log
            write_output(False)
            # Print error
            print(output_string)
    # When the while loop finishes
    else:
        # If it didn't work crash, if it did work continue on
        if worked == False:
            # Get time of the crash
            crash = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            # Get output depending on type of crash
            if request_type == "games":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\
                            \nBecause of an error retreiving game information\
                            \n======================================================================================================================================================"
            elif request_type == "genre":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\
                            \nBecause of an error retreiving genre information\
                            \n======================================================================================================================================================"
            # Write error that the scraper stopped working
            write_output(False)
            # Print the output
            print(output_string)
            # Exit the entire script
            exit()
        # If it did work return the result
        elif worked == True:
            return result


# Function to get the genre of a game
def get_genre(url, game):
    # Call the function to get results from the webpage
    h2 = get_list(url, "genre", game)
    # To store the result
    result = ""
    # Try to get the genre
    try:
        # Search through all the headers to find the Genre
        for h in h2:
            if h.string == "Genre":
                # Find the genres next sibling which will have the infroamtion on it
                result = h.next_sibling.string.strip()
    # If it couldn't get the genre for some reason set it as nan
    except:
        result = np.nan
    # Return the result
    return result


# Function to get games
def get_games():
    # Global variables
    global output_string
    global accepted_games
    # Running totals
    elapsed_pages = 0
    elapsed_games = 0
    # Getting start time
    total_start_time = time.time()
    # Loop for every page you want to search
    for page in range(1, pages + 1):
        # Getting time
        page_start_time = time.time()
        # Elapse Page (Pretty sure this could just be page, it's not like the games ocunter, oh well doesn't really matter)
        elapsed_pages += 1
        # Getting current url to search
        url = (
            url_head
            + url_pages
            + str(page)
            + url_results
            + str(results_per_page)
            + url_tail
        )
        # Call the function to get results from the webpage
        all_hyperlinks = get_list(url, "game", elapsed_pages)
        # Finding hyperlinks that contain games
        game_hyperlinks = []
        for i in all_hyperlinks:
            if "href" in i.attrs:
                if i.attrs["href"].startswith("https://www.vgchartz.com/game/"):
                    game_hyperlinks.append(i)

        # Getting stats for each game
        for game in game_hyperlinks:
            # Track if game is kept
            kept_game = False
            # Get game start time
            game_start_time = time.time()
            # Elapse game
            elapsed_games += 1
            # Get the parent information
            parent_information = game.parent.parent.find_all("td")
            # Get platform information (From the images alt text)
            platform = parent_information[3].find("img").attrs["alt"].strip()
            # Checking if the platform is one of the platform types I don't want ("Series" and "All". They're not useful to analyze individual video games)
            # If the data isn't a "Series" or "All" continue, if not then just skip it
            if ("Series" not in platform) and ("All" not in platform):
                # Note that it was kept
                kept_game = True
                # Get position based on when it was accepted (can't use position from the data set anymore because it's tainted)
                accepted_games += 1
                # rank = parent_information[0].string.strip()
                # Get box art information (from the image alt text, this is useless, but you can include it if you want)
                ##box_art = parent_information[1].find("img").attrs["alt"]
                # Get the game name (From the game object, not the parent, but I'll leave that option here as well)
                game_name = game.string.strip()
                ##game_name = parent_information[2].find("a").string.strip()
                # Get publisher information (Simply from the string)
                publisher = parent_information[4].string.strip()
                # Get developer information (Simply from the string)
                developer = parent_information[5].string.strip()
                # Get the genre (Using a function, also I'll leave how to get the link from parent instead of the game object)
                game_link = game.attrs["href"].strip()
                ##game_link= parent_information[2].find("a").attrs["href"].strip()
                genre = get_genre(game_link, game_name)
                # Get critic score (by using a function to test for N/A and convert to float)
                critic_score = float_covert(parent_information[6].string.strip())
                # Get user score (by using a function to test for N/A and convert to float)
                user_score = float_covert(parent_information[7].string.strip())
                # Get total shipped (by using a function to test for N/A and convert to float)
                total_shipped = float_covert(parent_information[8].string.strip())
                # Get total sales (by using a function to test for N/A and convert to float)
                total_sales = float_covert(parent_information[9].string.strip())
                # Get north america sales (by using a function to test for N/A and convert to float)
                na_sales = float_covert(parent_information[10].string.strip())
                # Get pal sales (by using a function to test for N/A and convert to float)
                pal_sales = float_covert(parent_information[11].string.strip())
                # Get japan sales (by using a function to test for N/A and convert to float)
                japan_sales = float_covert(parent_information[12].string.strip())
                # Get other sales (by using a function to test for N/A and convert to float)
                other_sales = float_covert(parent_information[13].string.strip())
                # Get release date (by using a function to test for N/A and convert to date)
                release_date = date_covert(parent_information[14].string.strip())
                # Get last update date (by using a function to test for N/A and convert to date)
                last_update = date_covert(parent_information[15].string.strip())

                # Creating a data array
                data = np.array(
                    [
                        accepted_games,
                        game_name,
                        platform,
                        publisher,
                        developer,
                        genre,
                        critic_score,
                        user_score,
                        total_shipped,
                        total_sales,
                        na_sales,
                        pal_sales,
                        japan_sales,
                        other_sales,
                        release_date,
                        last_update,
                    ]
                )

                # Adding to  the data frame
                df.loc[len(df.index)] = data

            # Either way print times
            # Get elapsed times
            current_time = time.time()
            elapsed_game_time = current_time - game_start_time
            elapsed_game_print = time.strftime(
                "%H:%M:%S", time.gmtime(elapsed_game_time)
            )
            elapsed_page_time = current_time - page_start_time
            elapsed_page_print = time.strftime(
                "%H:%M:%S", time.gmtime(elapsed_page_time)
            )
            total_elapsed_time = current_time - total_start_time
            elapsed_total_print = time.strftime(
                "%H:%M:%S", time.gmtime(total_elapsed_time)
            )
            # Output string
            output_string = f"Page: {elapsed_pages}/{pages} | Game: {elapsed_games}/{total_results} | Kept Games: {accepted_games}\{elapsed_games} | Game Took: {elapsed_game_print} | Page: Took: {elapsed_page_print} | Total Elapsed: {elapsed_total_print}"
            # Write to log
            if kept_game == True:
                # Write to csv if the game was kept
                write_output(True)
            else:
                # Only write to log if the game wasn't kept
                write_output(False)
            # Printing the output
            print(output_string)
    # Write the final output string if it didn't crash before this
    finsihed = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    output_string = f"======================================================================================================================================================\n\
                    The scrape finished at: {finsihed} with the follow stats\
                    Page: {elapsed_pages}/{pages}\nGame: {elapsed_games}/{total_results}\nKept Games: {accepted_games}\{elapsed_games}\nTotal Elapsed: {elapsed_total_print}"
    write_output(False)


# Writing Output Files
def write_output(write_csv):
    # Write csv if true
    if write_csv == True:
        # Replace unwanted empty values in the last row (also leaving the old code option that did the entire data frame)
        df.loc[df.index[-1] :].replace(
            [np.nan, "nan", np.empty, ""], "N/A", inplace=True, regex=True
        )
        # df.replace([np.nan, "nan", np.empty, ""], "N/A", inplace=True)
        # Write the df to csv
        df.loc[df.index[-1] :].to_csv(
            "raw.csv",
            sep=",",
            encoding="utf-8-sig",
            index=False,
            header=False,
            na_rep="N/A",
            mode="a",
        )
        # df.to_csv(
        #     "raw.csv",
        #     sep=",",
        #     encoding="utf-8-sig",
        #     index=False,
        #     header=False,
        #     na_rep="N/A",
        #     mode="a",
        # )
    # Write simple statistics to text file either way
    with open("stats.txt", "a") as f:
        f.write("\n" + output_string)


# Run the scrape with a keybaord interrupt
try:
    # Run the main function
    get_games()
# If you need to stop for some reason all wont be lost if you do ctl + c
except KeyboardInterrupt:
    # Write output saying the user cancelled it
    cancelled = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    output_string = f"======================================================================================================================================================\n\
                    The user has cancelled the scrape of VGCHARTZ at {cancelled}"
    write_output(False)
