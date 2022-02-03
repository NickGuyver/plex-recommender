# plex-recommender
Description:
Get movie recommendations based on your current PleX library. It will go through each movie in the list, pull the number of recommendations you request, tally them, and then print out an ordered list of the most recommended movies based on your inputs.


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
python .\recommender-fast.py

(R)ecommended - From "recommended" list on movie page.
(S)imilar - From similar keywords and genres.
Select recommendation type (R/S):
        s
Enter number of recommendations (range 1-20):
        10
Enter TMDB API key:
        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Enter full path to Tautulli metadata output .json with guids.id field:
        ".\Library - Movies - All [1].json"


Extracting TMDB IDs from list of movies at:
        .\Library - Movies - All [1].json...

Getting 10 TMDB recommendations for each of the 1166 movie IDs...
        Progress: |██████████████████████████████| 100.00% Complete

1 movies with no recommendations:
        Zombie Cop (1991)

Total recommendations:
        8224

Top 10 recommendations:
        Movie - The Crow: Salvation (2000)
        TMDB - https://www.themoviedb.org/movie/9456
        IMDB - https://www.imdb.com/title/tt0132910/
        Recommended - 61 times

<snip>
```
