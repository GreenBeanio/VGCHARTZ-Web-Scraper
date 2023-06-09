#!/usr/bin/env python3
# region Import Packages
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import html5lib
import datetime
import time
import os.path

# endregion Import Packages
# region User Parameters
# Parameters to set for amount of results (The full database as of this script is 62,674 results)
pages = 63
results_per_page = 1000

# Settings to set a maximum game (The full database as of this script is 62,674 results)
use_max_game = True
max_game = 62674

# Setting to start from a specific page and game
use_specific_start = False
skipped_games = 0

# Set to true if you want to use full dates instead of just the years
full_date = True

# Set the amount of attempts you want to wait for
set_attempts = 40

# Time to wait in between attempts in seconds (The failures will most likely be because a 429 too many requests issue)
wait_time = 15

# endregion User Parameters
# region Set Parameters
# Accepted games
accepted_games = 0

# The total results
total_results = pages * results_per_page

# String for holding the output text
output_string = ""

# Main Game URL Strings
url_head = "https://www.vgchartz.com/games/games.php?"
url_pages = "page="
url_results = "&results="
url_tail = (
    "&order=Sales&ownership=Both&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&"
    "showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showvgchartzscore=1&showcriticscore=1"
    "&showuserscore=1&showshipped=1"
)
# Other URLS
hardware_url = "https://www.vgchartz.com/charts/platform_totals/Hardware.php"
software_url = "https://www.vgchartz.com/charts/platform_totals/Software.php"
tie_ratio_url = "https://www.vgchartz.com/charts/platform_totals/TieRatio.php"

# Array with unwanted values to replace with "N/A"
unwanted = np.array([np.nan, "nan", np.empty, ""])
# Array of Platform Codes (Value to replace)
codes = np.array([])
# Array of Platform Names (Value to be replace with)
platforms = np.array([])

# Create a data frame to store the output without the "All" or "Series"
df = pd.DataFrame(
    columns=[
        "Rank",
        "Name",
        "Platform",
        "Code",
        "Publisher",
        "Developer",
        "Genre",
        "VGChartz Score",
        "Critic Score",
        "User Score",
        "Total Shipped",
        "Total Sales",
        "NA Sales",
        "PAL Sales",
        "Japan Sales",
        "Other Sales",
        "Release Date",
        "Last Update",
    ]
)
# Create a copy of the empty data frame to store the output with the "All" & "Series" platforms
df_all = df.copy()
# Create a data frame to store the platforms
df_platform = pd.DataFrame(columns=["Code", "Platform"])
# Create a data frame to store the Hardware
df_hardware = pd.DataFrame(
    columns=[
        "Position",
        "Platform",
        "Code",
        "North America",
        "Europe",
        "Japan",
        "Rest of the World",
        "Global",
    ]
)
# Create a data frame to store the Software
df_software = pd.DataFrame(
    columns=[
        "Position",
        "Platform",
        "Code",
        "Global",
    ]
)
# Create a data frame to store the Tie-Ratio
df_tie_ratio = pd.DataFrame(
    columns=[
        "Position",
        "Platform",
        "Code",
        "Ratio",
    ]
)


# endregion Static Parameters
# region Conversion Functions
# Function to convert string to float, check for N/A, and remove the m for millions
def float_covert(str):
    result = ""
    # If the string contains "N/A" set it as nothing
    if "N/A" in str:
        result = np.nan
    else:
        # If the string contains "m" remove the m and convert
        if "m" in str:
            result = np.float64(str[:-1])
        # If the string contains a comma remove it and convert
        elif "," in str:
            result = np.float64(str.replace(",", ""))
        # If it doesn't contain an "m" or a "," just convert
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


# endregion Conversion Functions
# region Data Gathering & Processing
# Function get a list from beautiful soup
def get_list(url, request_type, pages_or_game):
    # Get attempts from the set_attempts
    attempts = set_attempts
    # Track if it worked
    worked = False
    # Global string
    global output_string
    # For storing the rest
    result = ""
    # While loop for the number of attempts
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
                # Storing the main results in the main table
                main_table = soup.find("div", attrs={"id": "generalBody"})
                # Finding hyperlinks in the table
                result = main_table.find_all("a")
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
            # If we're getting the genre information
            elif request_type == "genre":
                # Find the table
                game_table = soup.find("div", attrs={"id": "gameGenInfoBox"})
                result = game_table.find_all("h2")
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
            # If we're getting the platform information
            elif request_type == "platform":
                # Find the option table
                options_table = soup.find("select", attrs={"name": "console"})
                # Get the values that have the option tag
                consoles = options_table.find_all("option")
                # Remove the first consoles value because it's empty
                result = consoles[1:]
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
            elif (
                request_type == "hardware"
                or request_type == "software"
                or request_type == "tie-ratio"
            ):
                # Storing the main results in the main table
                general_table = soup.find("table", attrs={"id": "myTable"})
                # Finding rows in the table
                result = general_table.find_all("tr")
                # Get rid of the header row from the table
                result = result[1:]
                # Set attempt to 0
                attempts = 0
                # Set worked to true
                worked = True
        # If we don't get the information we were looking for
        except:
            if request_type == "game":
                output_string = (
                    f"Error getting game information from page {pages_or_game}"
                )
            elif request_type == "genre":
                output_string = (
                    f"Error getting genre information from the game {pages_or_game}"
                )
            elif request_type == "platform":
                output_string = f"Error getting platform information"
            elif request_type == "hardware":
                output_string = f"Error getting hardware information"
            elif request_type == "software":
                output_string = f"Error getting software information"
            elif request_type == "tie-ratio":
                output_string = f"Error getting tie-ratio information"
            # Write to log
            write_output(False, False)
            # Print error
            print(output_string)
            # Sleep between second attempt
            time.sleep(wait_time)
    # When the while loop finishes
    else:
        # If it didn't work crash, if it did work continue on
        if worked == False:
            # Get time of the crash
            crash = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            # Get output depending on type of crash
            if request_type == "games":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving game information\n\
                            ======================================================================================================================================================"
            elif request_type == "genre":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving genre information\n\
                            ======================================================================================================================================================"
            elif request_type == "platform":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving platform information\n\
                            ======================================================================================================================================================"
            elif request_type == "hardware":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving hardware information\n\
                            ======================================================================================================================================================"
            elif request_type == "software":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving software information\n\
                            ======================================================================================================================================================"
            elif request_type == "tie-ratio":
                output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has broken at {crash}\n\
                            Because of an error retrieving tie ratio information\n\
                            ======================================================================================================================================================"
            # Write error that the scraper stopped working
            write_output(False, False)
            # Print the output
            print(output_string)
            # Exit the entire script
            exit()
        # If it did work return the result
        elif worked == True:
            return result


# Function to get the platform codes and names
def get_platforms():
    # For writing output
    global output_string
    # Global values to modify the arrays
    global codes
    global platforms
    # Getting current url to search
    url = url_head + url_pages + str(1) + url_results + str(1) + url_tail
    # Call the function to get results from the webpage
    consoles = get_list(url, "platform", "don't need")
    # for every console in consoles
    for console in consoles:
        # Get the console code
        code = console.attrs["value"].strip()
        # Get the console name
        name = console.string.strip()
        # Adding the values to arrays
        codes = np.append(codes, code)
        platforms = np.append(platforms, name)
    # Add to dataframe
    df_platform["Code"] = codes.tolist()
    df_platform["Platform"] = platforms.tolist()
    # Set output string
    output_string = "Successfully got platform information"
    # Write to log
    write_output(False, False)
    # Print error
    print(output_string)


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
                # Find the genres next sibling which will have the information on it
                result = h.next_sibling.string.strip()
    # If it couldn't get the genre for some reason set it as nan
    except:
        result = np.nan
    # Return the result
    return result


# Function to get the sales numbers
def get_sales(task):
    # For writing output
    global output_string
    # Getting current url to search
    if task == "hardware":
        url = hardware_url
    elif task == "software":
        url = software_url
    elif task == "tie-ratio":
        url = tie_ratio_url
    # Call the function to get results from the webpage
    rows = get_list(url, task, "don't need")
    # for every row in the table
    for row in rows:
        # Find the cells
        cells = row.find_all("td")
        # Get the position
        position = cells[0].string.strip()
        # Get the platform
        platform_full = cells[1].string.strip()
        # Split the platform name and platform code
        platform_split = platform_full.split(" ")
        platform = " ".join(platform_split[:-1]).strip()
        code = "".join(platform_split[-1:]).replace("(", "").replace(")", "").strip()
        # The different ways for the different types
        if task == "hardware":
            # Get sales numbers
            north_america = float_covert(cells[2].string.strip())
            europe = float_covert(cells[3].string.strip())
            japan = float_covert(cells[4].string.strip())
            rest = float_covert(cells[5].string.strip())
            _global = float_covert(cells[6].string.strip())
            # Adding the data to an array
            data = np.array(
                [position, platform, code, north_america, europe, japan, rest, _global]
            )
            # Adding to  the data frame
            df_hardware.loc[len(df_hardware.index)] = data
        elif task == "software":
            # Get sales numbers
            _global = float_covert(cells[2].string.strip())
            # Adding the data to an array
            data = np.array([position, platform, code, _global])
            # Adding to  the data frame
            df_software.loc[len(df_software.index)] = data
        elif task == "tie-ratio":
            # Get the ratio (sales of software per hardware)
            ratio = float_covert(cells[2].string.strip())
            # Adding the data to an array
            data = np.array([position, platform, code, ratio])
            # Adding to  the data frame
            df_tie_ratio.loc[len(df_tie_ratio.index)] = data
    # Set output string
    if task == "hardware":
        output_string = "Successfully got hardware information"
    elif task == "software":
        output_string = "Successfully got software information"
    elif task == "tie-ratio":
        output_string = "Successfully got tie-ratio information"
    # Write to log
    write_output(False, False)
    # Print error
    print(output_string)


# Function to get games
def get_games():
    # Global variables
    global output_string
    global accepted_games
    # Running totals
    elapsed_pages = 0
    elapsed_games = 0
    # For keeping totals with skipped
    total_pages = 0
    total_games = 0
    # Set current value defaults (that will be changed if using a specific start)
    current_pages = pages
    end_page = pages
    current_games = total_results
    show_total_results = total_results
    # Getting start time
    total_start_time = time.time()
    # Calling the function to get the platforms
    get_platforms()
    # Calling the function to get the other types of sales
    get_sales("hardware")
    get_sales("software")
    get_sales("tie-ratio")
    # Save the platforms and other sales
    save_platforms()
    # Variable to indicate starting page (0 by default) and games to skip (0 by default)
    start_page = 0
    games_skip = 0
    # If using a max game
    if use_max_game == True:
        # Set show total results to the max_game
        show_total_results = max_game
        # Set current_games
        current_games = show_total_results
        # Set the total pages to the xxx
        end_page = int(np.ceil(show_total_results / results_per_page))

    # Set starting page if you're starting from a specific point
    if use_specific_start == True:
        # Get the amount of pages to skip
        page_skip_parts = np.modf(skipped_games / results_per_page)
        # Change the start page if using it (Have to subtract 1 because it adds one later)
        start_page = int(page_skip_parts[1])
        # Set the games_skip if using it
        games_skip = int(page_skip_parts[0] * results_per_page)
        # Setting total counts
        total_pages = start_page
        total_games = games_skip + (results_per_page * total_pages)
        current_pages = end_page - start_page
        current_games = show_total_results - total_games
        # Check that it wouldn't be past the max games
        if use_max_game == True and total_games + 1 >= max_game:
            finished = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            output_string = f"======================================================================================================================================================\n\
                            The scrape of VGCHARTZ has finished at {finished}\n\
                            You silly goose you're skipping more than your max!\n\
                            ======================================================================================================================================================"
            write_output(False, False)
            print(output_string)
            exit()
    # Loop for every page you want to search
    for page in range(start_page + 1, end_page + 1):
        # Getting time
        page_start_time = time.time()
        # Elapse Pages
        elapsed_pages += 1
        # Increasing total pages
        total_pages += 1
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
        all_hyperlinks = get_list(
            url, "game", total_pages
        )  ## I think total not elapsed
        # Finding hyperlinks that contain games
        game_hyperlinks = []
        for i in all_hyperlinks:
            if "href" in i.attrs:
                if i.attrs["href"].startswith("https://www.vgchartz.com/game/"):
                    game_hyperlinks.append(i)
        # If you're skipping games remove some games from the results, if not leave it alone
        if elapsed_pages == 1 and use_specific_start == True:
            # Remove the amount to skip games from the result
            game_hyperlinks = game_hyperlinks[games_skip:]
        # Getting stats for each game
        for game in game_hyperlinks:
            # Track if game is kept
            kept_game = False
            # Get game start time
            game_start_time = time.time()
            # Elapse game
            elapsed_games += 1
            # Elapse total games
            total_games += 1
            # Get the parent information
            parent_information = game.parent.parent.find_all("td")
            # Code to debug and test what is what in the game results
            # for x in range(0, len(parent_information)):
            #     try:
            #         print(f"{x}: {parent_information[x]}")
            #     except:
            #         print(f"{x}: ERROR")
            # Get the overall rank (Used for the "All" and "Series" data frame)
            rank = parent_information[0].string.strip()
            # Get box art information (from the image alt text, this is useless, but you can include it if you want)
            ##box_art = parent_information[1].find("img").attrs["alt"]
            # Get the game name (From the game object, not the parent, but I'll leave that option here as well)
            game_name = game.string.strip()
            ##game_name = parent_information[2].find("a").string.strip()
            # Get the genre (Using a function, also I'll leave how to get the link from parent instead of the game object)
            game_link = game.attrs["href"].strip()
            ##game_link= parent_information[2].find("a").attrs["href"].strip()
            genre = get_genre(game_link, game_name)
            # Get platform code (From the images alt text)
            platform_code = parent_information[3].find("img").attrs["alt"].strip()
            # Getting the platform name (By replacing the platform code with it's full name)
            platform = pd.Series(np.array([platform_code]))
            platform = platform.replace(codes, platforms)
            platform = platform[0]
            # Get publisher information (Simply from the string)
            publisher = parent_information[4].string.strip()
            # Get developer information (Simply from the string)
            developer = parent_information[5].string.strip()
            # Get the VGChartz Score (by using a function to test for N/A and convert to float)
            vgchartz_score = float_covert(parent_information[6].string.strip())
            # Get critic score (by using a function to test for N/A and convert to float)
            critic_score = float_covert(parent_information[7].string.strip())
            # Get user score (by using a function to test for N/A and convert to float)
            user_score = float_covert(parent_information[8].string.strip())
            # Get total shipped (by using a function to test for N/A and convert to float)
            total_shipped = float_covert(parent_information[9].string.strip())
            # Get total sales (by using a function to test for N/A and convert to float)
            total_sales = float_covert(parent_information[10].string.strip())
            # Get north america sales (by using a function to test for N/A and convert to float)
            na_sales = float_covert(parent_information[11].string.strip())
            # Get pal sales (by using a function to test for N/A and convert to float)
            pal_sales = float_covert(parent_information[12].string.strip())
            # Get japan sales (by using a function to test for N/A and convert to float)
            japan_sales = float_covert(parent_information[13].string.strip())
            # Get other sales (by using a function to test for N/A and convert to float)
            other_sales = float_covert(parent_information[14].string.strip())
            # Get release date (by using a function to test for N/A and convert to date)
            release_date = date_covert(parent_information[15].string.strip())
            # Get last update date (by using a function to test for N/A and convert to date)
            last_update = date_covert(parent_information[16].string.strip())
            # Creating a data array for the "All" and "Series" data frame
            # Creating a data array
            data_all = np.array(
                [
                    rank,
                    game_name,
                    platform,
                    platform_code,
                    publisher,
                    developer,
                    genre,
                    vgchartz_score,
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
            # Adding to  the data frame ("All" & "Series"). Replacing the first row, because we only need to store one row at a time.
            # Instead of adding it to a new row like I did do before. I'm changing this to hopefully save on needed memory.
            df_all.loc[0] = data_all
            #df_all.loc[len(df_all.index)] = data_all

            # Checking if the platform is one of the platform types I don't want ("Series" and "All". They're not useful to analyze individual video games)
            # If the data isn't a "Series" or "All" continue, if not then just skip it
            # I have changed my mind on that, instead I will just save it to 2 csv, one with them and one without.
            # I'm not worried too much about speed. I can just run it when I sleep one night. I could  filter out the unwanted rows at the end and
            # save computing time, but I'm not. Boo hoo.
            if ("Series" not in platform) and ("All" not in platform):
                # Note that it was kept
                kept_game = True
                # Get position based on when it was accepted (can't use position from the data set anymore because it's tainted)
                accepted_games += 1
                # Creating a data array
                data = np.array(
                    [
                        accepted_games,
                        game_name,
                        platform,
                        platform_code,
                        publisher,
                        developer,
                        genre,
                        vgchartz_score,
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
                # Adding to  the data frame (Same change as above)
                df.loc[0] = data
                #df.loc[len(df.index)] = data

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
            output_string = f"Pages: {elapsed_pages}/{current_pages} | Total Pages: {total_pages}/{end_page} | Games: {elapsed_games}/{current_games} | Total Games: {total_games}/{show_total_results} | Kept Games: {accepted_games}\{elapsed_games} | Game Took: {elapsed_game_print} | Page: Took: {elapsed_page_print} | Total Elapsed: {elapsed_total_print}"
            # Write to log
            if kept_game == True:
                # Write to both csv if the game was kept
                write_output(True, True)
            else:
                # Only write to log and all games if the game wasn't kept
                write_output(True, False)
            # Printing the output
            print(output_string)
            # If using a max game (stop the program now)
            if use_max_game == True and total_games == max_game:
                finished = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(time.time())
                )
                output_string = f"======================================================================================================================================================\n\
                    The scrape finished at: {finished} with the follow stats\n\
                    Pages: {elapsed_pages}/{current_pages} | Total Pages: {total_pages}/{end_page} | Games: {elapsed_games}/{current_games} | Total Games: {total_games}/{show_total_results} | Kept Games: {accepted_games}\{elapsed_games} | Game Took: {elapsed_game_print} | Page: Took: {elapsed_page_print} | Total Elapsed: {elapsed_total_print}"
                write_output(False, False)
                print(output_string)
                exit()
    # Write the final output string if it didn't crash before this
    finished = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    output_string = f"======================================================================================================================================================\n\
                    The scrape finished at: {finished} with the follow stats\n\
                    Pages: {elapsed_pages}/{current_pages} | Total Pages: {total_pages}/{end_page} | Games: {elapsed_games}/{current_games} | Total Games: {total_games}/{show_total_results} | Kept Games: {accepted_games}\{elapsed_games} | Game Took: {elapsed_game_print} | Page: Took: {elapsed_page_print} | Total Elapsed: {elapsed_total_print}"
    write_output(False, False)
    print(output_string)


# endregion Data Gathering & Processing
# region Outputs
# Writing Output Files
def write_output(write_csv, keep_games):
    # Write csv if true
    if write_csv == True:
        # If we're writing to a game we kept
        if keep_games == True:
            # Replace the unwanted values with "N/A"
            # "0" could be "df.index[-1]"" to get the last row, but since there's only 1 row using 0 should save a fraction of time not doing a calculation every time.
            df.loc[0 :] = df.loc[0 :].replace(unwanted, "N/A")
            #df.loc[df.index[-1] :] = df.loc[df.index[-1] :].replace(unwanted, "N/A")
            # Write the df to csv
            df.loc[0 :].to_csv(
                "Output/kept_games.csv",
                sep=",",
                encoding="utf-8-sig",
                index=False,
                header=False,
                na_rep="N/A",
                mode="a",
            )
        # Writing to the all csv either way
        # Replace platform codes with names. Same thing with the "0" as above
        df_all.loc[0 :] = df_all.loc[0 :].replace(
            unwanted, "N/A"
        )
        # Write the df to csv
        df_all.loc[0 :].to_csv(
            "Output/all_games.csv",
            sep=",",
            encoding="utf-8-sig",
            index=False,
            header=False,
            na_rep="N/A",
            mode="a",
        )
    # Write simple statistics to text file either way
    with open("Output/log.txt", "a") as f:
        f.write("\n" + output_string)


# Saving what we collected to a csv
def save_platforms():
    # Write starting line to the log
    with open("Output/log.txt", "a") as f:
        f.write(
            "======================================================================================================================================================"
        )
    # Save the platform information
    save_platform = df_platform.replace(unwanted, "N/A")
    save_platform.to_csv(
        "Output/platforms.csv",
        sep=",",
        encoding="utf-8-sig",
        index=False,
        header=True,
        na_rep="N/A",
        mode="w",
    )
    # Save the hardware information
    save_hardware = df_hardware.replace(unwanted, "N/A")
    save_hardware.to_csv(
        "Output/hardware.csv",
        sep=",",
        encoding="utf-8-sig",
        index=False,
        header=True,
        na_rep="N/A",
        mode="w",
    )
    # Save the software information
    save_software = df_software.replace(unwanted, "N/A")
    save_software.to_csv(
        "Output/software.csv",
        sep=",",
        encoding="utf-8-sig",
        index=False,
        header=True,
        na_rep="N/A",
        mode="w",
    )
    # Save the tie-ratio information
    save_tie_ratio = df_tie_ratio.replace(unwanted, "N/A")
    save_tie_ratio.to_csv(
        "Output/tie_ratio.csv",
        sep=",",
        encoding="utf-8-sig",
        index=False,
        header=True,
        na_rep="N/A",
        mode="w",
    )
    # Save the initial csv (if they don't exist) for the other csv as well (so that they'll have headers)
    # For the kept games
    if os.path.isfile("Output/kept_games.csv") == False:
        df.to_csv(
            "Output/kept_games.csv",
            sep=",",
            encoding="utf-8-sig",
            index=False,
            header=True,
            na_rep="N/A",
            mode="w",
        )
    # For the all csv
    if os.path.isfile("Output/all_games.csv") == False:
        df_all.to_csv(
            "Output/all_games.csv",
            sep=",",
            encoding="utf-8-sig",
            index=False,
            header=True,
            na_rep="N/A",
            mode="w",
        )


# endregion Outputs
# region Starting Point
# Run the scrape with a keyboard interrupt
try:
    # Check for the output directory, and create it if it doesn't exist.
    if os.path.exists("Output") == False:
        os.mkdir("Output")
    # Get the games
    get_games()
# If you need to stop for some reason all wont be lost if you do ctl + c
except KeyboardInterrupt:
    # Write output saying the user cancelled it
    cancelled = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    output_string = f"\n======================================================================================================================================================\n\
                    The user has cancelled the scrape of VGCHARTZ at {cancelled}"
    print(output_string)
    write_output(False, False)
# endregion Starting Point
