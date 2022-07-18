from collections import Counter
from json import loads
from urllib.parse import quote, unquote
from urllib.request import urlopen

missing = []
unknown = set()

#get choices from user
def getUserInput():
    print('\n(R)ecommended - From "recommended" list on media page.')
    print('(S)imilar - From similar keywords and genres.')
    recommendation_type = input('Select recommendation type (R/S):\n\t').lower()
    
    if recommendation_type.startswith('r'):
        recommendation_type = 'r'
    else:
        recommendation_type = 's'
        
    media_type = input('Enter media type (Movie/TV):\n\t').lower()
    
    if media_type.startswith('m'):
        media_type = 'movie'
    else:
        media_type = 'tv'
        
    num_recommendations = int(input('Enter number of recommendations (range 1-20):\n\t'))
    
    if num_recommendations <= 0:
        num_recommendations = 1
    elif num_recommendations >= 20:
        num_recommendations = 20
    
    api_key = input('Enter TMDB API key:\n\t')
    
    return num_recommendations, api_key, recommendation_type, media_type

#progress bar from https://stackoverflow.com/a/34325723
def progressBar(iterable):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = f'{100 * (iteration / float(total)):.2f}'
        filled_length = int(30 * iteration // total)
        bar = f'{"█" * filled_length}{"-" * (30 - filled_length)}'
        
        print(f'\r\tProgress: |{bar}| {percent}% Complete', end = '\r')

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

#get list of titles and years
def getMediaList():
    from json import load
    
    #using set to ensure no duplicates
    id_set = set()
    
    #added replace because Windows drag&drop added quotes which broke filename as read by Python
    tautulli_file = input('Enter full path to Tautulli metadata output .json with guids.id field:\n\t').replace('"', '')
    print(f'\n\nExtracting TMDB IDs from list of media at:\n\t{tautulli_file}...')
    
    with open(tautulli_file, newline='', encoding = 'utf-8') as tautulli:
        tautulli_json = load(tautulli)
        
        #filter out and only get TMDB id
        for result in tautulli_json:
            for guid in result['guids']:
                if guid['id'].startswith('tmdb'):
                    id_set.add(guid['id'].split('//')[1])

    return id_set

#get recommendations from id
def getRecommendations(media_id, num_recommendations):
    #using list to track frequency of duplicates
    recommend_list = []
    
    #generate tmdb api get similar movie/tv query
    if recommendation_type == 'r':
        tmdb_query = f'https://api.themoviedb.org/3/{media_type}/{media_id}/recommendations?api_key={api_key}'
    
    #generate tmdb api get recommended movie/tv query
    else:
        tmdb_query = f'https://api.themoviedb.org/3/{media_type}/{media_id}/similar?api_key={api_key}'
    
    with urlopen(tmdb_query) as response:
        html = response.read().decode('utf-8')
        tmdb_json = loads(html)
        
        total_results = int(tmdb_json['total_results'])
        
        #some media has no recommendations
        if total_results == 0:
            return [], total_results
        
        #only go up to the number of results if less than the requested recommendations
        elif total_results <= num_recommendations:
            num_recommendations = total_results
        
        for results in range(num_recommendations):
            #total_results returned from tmdb api is not always correct
            try:
                tmdb_rec = f"{tmdb_json['results'][results]['id']}"
            except IndexError:
                print(tmdb_query)
                total_results = results
                break
            
            if tmdb_rec not in owned:
                recommend_list.append(tmdb_rec)
    
    return recommend_list, total_results

#get movies details from recommended list
def getMovie(media_id, frequency):
    #generate tmdb api get movie details query
    tmdb_query = f'https://api.themoviedb.org/3/movie/{media_id}?api_key={api_key}'

    with urlopen(tmdb_query) as response:
        html = response.read().decode('utf-8')
        tmdb_json = loads(html)
        
        print(f"\tMovie - {tmdb_json['title']} ({tmdb_json['release_date'].split('-')[0]})")
        print(f'\tTMDB - https://www.themoviedb.org/movie/{media_id}')
        print(f"\tIMDB - https://www.imdb.com/title/{tmdb_json['imdb_id']}/")
        print(f'\tRecommended - {frequency} times\n')
        
    return
    
#get movies details from recommended list
def getShow(media_id, frequency):
    #generate tmdb api get tv details query
    tmdb_query = f'https://api.themoviedb.org/3/tv/{media_id}?api_key={api_key}'

    with urlopen(tmdb_query) as response:
        html = response.read().decode('utf-8')
        tmdb_json = loads(html)
        
        print(f"\tShow - {tmdb_json['name']} ({tmdb_json['first_air_date'].split('-')[0]})")
        print(f'\tTMDB - https://www.themoviedb.org/tv/{media_id}')
        print(f'\tRecommended - {frequency} times\n')
        
    return


num_recommendations, api_key, recommendation_type, media_type = getUserInput()

owned = list(getMediaList())

print(f"\nGetting {num_recommendations} TMDB recommendations for each of the {len(owned)} IDs...")

for index in progressBar(range(len(owned))):
    found, total_results = getRecommendations(owned[index], num_recommendations)
    
    #add to the missing list if there were recommendations found
    if total_results > 0:
        missing.extend(found)
    
    #if no recommendations came back, pull the media details and let the user know
    else:
        tmdb_query = f'https://api.themoviedb.org/3/{media_type}/{owned[index]}?api_key={api_key}'
        
        with urlopen(tmdb_query) as response:
            html = response.read().decode('utf-8')
            tmdb_json = loads(html)
            
            #tv shows use slightly different key naming 
            if media_type == 'movie':
                unknown.add(f"\t{tmdb_json['title']} ({tmdb_json['release_date'].split('-')[0]})")
            
            else:
                unknown.add(f"\t{tmdb_json['name']} ({tmdb_json['first_air_date'].split('-')[0]})")
if unknown:
    print(f"\n{len(unknown)} titles with no recommendations:")
    
    for index in unknown:
        print(index)

missing_counter = Counter(missing).most_common(num_recommendations)
recommendation_count = f'{len(missing)}'

print(f'\nTotal recommendations:\n\t{recommendation_count}')
print(f"\nTop {num_recommendations} recommendations:")

if media_type == 'movie':
    for index in range(0, len(missing_counter)):
        getMovie(missing_counter[index][0], f'{missing_counter[index][1]}')
        
else:
    for index in range(0, len(missing_counter)):
        getShow(missing_counter[index][0], f'{missing_counter[index][1]}')