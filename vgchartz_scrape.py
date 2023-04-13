#!/usr/bin/env python3
# Import Packages
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import html5lib

# URL
url = (
    "https://www.vgchartz.com/games/games.php?page=1&results=1"
    "&order=Sales&ownership=Both&direction=DESC&showtotalsales=1"
    "&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1"
    "&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1"
    "&showvgchartzscore=0&showcriticscore=1&showuserscore=1&showshipped=1"
)


# Create a data frame
df = pd.DataFrame(columns=["Code", "Platform"])


# Get the platform codes and names
def Get_Platforms():
    # Get the website information
    r = requests.get(url)
    # Beautiful soup the requested information
    soup = BeautifulSoup(r.content, "html5lib")
    # Find the section with the option boxes
    options_table = soup.find("select", attrs={"name": "console"})
    # Get the values that have the option tag
    consoles = options_table.find_all("option")
    # Remove the first consoles value because it's empty
    consoles = consoles[1:]
    # for every console in consoles
    for console in consoles:
        # Get the console code
        code = console.attrs["value"].strip()
        # Get the console name
        name = console.string.strip()
        # Creating an array
        data = np.array([code, name])
        # Adding to the data frame
        df.loc[len(df.index)] = data
    # Save to a csv
    Save_Platforms()


# Saving what we collected to a csv
def Save_Platforms():
    df.to_csv(
        "platforms.csv",
        sep=",",
        encoding="utf-8-sig",
        index=False,
        header=True,
        na_rep="N/A",
        mode="w",
    )


# Run it
Get_Platforms()
