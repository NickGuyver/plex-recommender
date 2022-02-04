# plex-recommender
Description:
Get movie/tv recommendations based on your current PleX library. It will go through each item in the list, pull the number of recommendations you request, tally them, and then print out an ordered list of the most recommended items based on your inputs.


Notes:
In order for it to work you will need a TMDB API key, which is free.

The script uses no external libraries, and is built for Python 3. There is little in the way for error checking bad user input.


Creating .json:
I recommend using Tautulli to create the main .json for ingestion, the script is built around this specific export format. To do that, go to the library you want to export, choose 'Export Metadata' and set the following different from default:
 - Data File Format: JSON
 - Custom Metadata Fields: guids.id
 - Media Info Export Level: Level 0 - None / Custom

From there, all you have to do is run the script and select the previously created .json. 


Example usage and output:
```
python .\recommender.py

(R)ecommended - From "recommended" list on media page.
(S)imilar - From similar keywords and genres.
Select recommendation type (R/S):
        s
Enter media type (Movie/TV):
        m
Enter number of recommendations (range 1-20):
        10
Enter TMDB API key:
        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Enter full path to Tautulli metadata output .json with guids.id field:
        ".\Library - Movies - All [1].json"


Extracting TMDB IDs from list of media at:
        .\Library - Movies - All [1].json...

Getting 10 TMDB recommendations for each of the 1166 IDs...
        Progress: |██████████████████████████████| 100.00% Complete

1 titles with no recommendations:
        Zombie Cop (1991)

Total recommendations:
        7947

Top 10 recommendations:
        Movie - Death Race (2008)
        TMDB - https://www.themoviedb.org/movie/10483
        IMDB - https://www.imdb.com/title/tt0452608/
        Recommended - 125 times

<snip>
```
