from collections import Counter
from json import loads
from urllib.parse import quote, unquote
from urllib.request import urlopen

missing = []
unknown = set()

#get choices from user
def getUserInput():
    print('\n(R)ecommended - From "recommended" list on movie page.')
    print('(S)imilar - From similar keywords and genres.')
    recommendation_type = input('Select recommendation type (R/S):\n\t').lower()
    
    if recommendation_type.startswith('r'):
        recommendation_type = 'r'
    else:
        recommendation_type = 's'
        
    num_recommendations = int(input('Enter number of recommendations (range 1-20):\n\t'))
    
    if num_recommendations <= 0:
        num_recommendations = 1
    elif num_recommendations >= 20:
        num_recommendations = 20
    
    api_key = input('Enter TMDB API key:\n\t')
    
    return num_recommendations, api_key, recommendation_type

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
def getMovieList():
    from json import load
    
    #using set to ensure no duplicates
    id_set = set()
    
    #added replace because Windows drag&drop added quotes which broke filename as read by Python
    tautulli_file = input('Enter full path to Tautulli metadata output .json with guids.id field:\n\t').replace('"', '')
    print(f'\n\nExtracting TMDB IDs from list of movies at:\n\t{tautulli_file}...')
    
    with open(tautulli_file, newline='', encoding = 'utf-8') as tautulli:
        tautulli_json = load(tautulli)
        
        #filter out and only get TMDB id
        for result in tautulli_json:
            for guid in result['guids']:
                if guid['id'].startswith('tmdb'):
                    id_set.add(result['guids'][1]['id'].split('//')[1])

    return id_set

#get recommendations from id
def getRecommendations(movie_id):
    #using list to track frequency of duplicates
    recommend_list = []
    
    #generate tmdb api get similar movies query
    if recommendation_type == 'r':
        tmdb_query = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}'
    
    #generate tmdb api get recommended movies query
    else:
        tmdb_query = f'https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={api_key}'
    
    with urlopen(tmdb_query) as response:
        html = response.read().decode('utf-8')
        tmdb_json = loads(html)
        
        for results in range(num_recommendations):
            try:
                tmdb_rec = f"{tmdb_json['results'][results]['id']}"
                
                if tmdb_rec not in owned:
                    recommend_list.append(tmdb_rec)
            
            #some movies have no recommendations
            except IndexError:
                return 0
    
    return recommend_list

#get movies details from recommended list
def getMovie(movie_id, frequency):
    #generate tmdb api get movie details query
    tmdb_query = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'

    with urlopen(tmdb_query) as response:
        html = response.read().decode('utf-8')
        tmdb_json = loads(html)
        
        print(f"\tMovie - {tmdb_json['title']} ({tmdb_json['release_date'].split('-')[0]})")
        print(f'\tTMDB - https://www.themoviedb.org/movie/{movie_id}')
        print(f"\tIMDB - https://www.imdb.com/title/{tmdb_json['imdb_id']}/")
        print(f'\tRecommended - {frequency} times\n')
        
    return


num_recommendations, api_key, recommendation_type = getUserInput()

owned = list(getMovieList())

print(f"\nGetting {num_recommendations} TMDB recommendations for each of the {len(owned)} movie IDs...")

for index in progressBar(range(len(owned))):
    found = getRecommendations(owned[index])
    
    if found:
        missing.extend(found)
    
    else:
        tmdb_query = f'https://api.themoviedb.org/3/movie/{owned[index]}?api_key={api_key}'

        with urlopen(tmdb_query) as response:
            html = response.read().decode('utf-8')
            tmdb_json = loads(html)
            
            unknown.add(f"\t{tmdb_json['title']} ({tmdb_json['release_date'].split('-')[0]})")
    
if unknown:
    print(f"\n{len(unknown)} movies with no recommendations:")
    
    for index in unknown:
        print(index)

missing_counter = Counter(missing).most_common(num_recommendations)
recommendation_count = f'{len(missing)}'

print(f'\nTotal recommendations:\n\t{recommendation_count}')
print(f"\nTop {num_recommendations} recommendations:")

for index in range(0, len(missing_counter)):
    getMovie(missing_counter[index][0], f'{missing_counter[index][1]}')