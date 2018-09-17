import http.client
import json
from time import sleep
from csv import writer

# Get 300 movies from TMDb
# Comedy after release year 2000 : ID=35
# 40 requests per 10 seconds
# Retrieve movie-ID,movie-name as sv

def get_movie_results(conn, api_key, page):
    """Queries the results for Comedies after 2000 for a specific page"""
    payload = "{}"
    
    conn.request("GET", "/3/discover/movie?with_genres=35&primary_release_date.gte=2000" \
                 "&page={0}&include_video=false&include_adult=false&sort_by=popularity.desc" \
                 "&language=en-US&api_key={1}".format(page, api_key), payload)
    
    res = conn.getresponse()
    movies = res.read().decode("utf-8")
    movies = json.loads(movies)
    results = movies['results']
    
    return results

def get_similar_movie_IDs(conn, api_key, ID):

    payload = "{}"
    conn.request("GET", "/3/movie/{0}/similar?page=1"\
                        "&language=en-US&api_key={1}".format(ID, api_key), payload)
    
    res = conn.getresponse()
    
    movies = res.read().decode("utf-8")
    movies = json.loads(movies)
    results = movies['results'][:5]
        
    return [i['id'] for i in results]

def query_timeout(sleep_time_s=10):
    sleep(sleep_time_s)
    return 0
    

def get_csv(api_key, n_items=300, create_csv=True):
    """Creaets a csv of n_items with each row containing movie_id,movie_title"""
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    page = 1
    queries = 0
    if create_csv: f =  writer(open("movie_ID_name.csv", "w"))
    while n_items > 0:
        
        if queries == 40: queries = query_timeout(10)
            
        else:
            results = get_movie_results(conn, api_key, page)
            queries += 1
            
            for movie in results:
                f.writerow([movie['id'], movie['title']])
                n_items -= 1
                
                if n_items == 0:
                    break
            page += 1
    
    if create_csv == False: print("Complete") # debugging
    
def get_similar_movies(csv_file, api_key, update_csv=True):
    """Return 5 similar movies per movie in csv_file. 
    Will skip repeated IDs"""    
    with open(csv_file, 'r', newline='') as f:
        csv = f.read()
        
    if update_csv: f =  writer(open("movie_ID_sim_movie_ID.csv", "w"))
    csv_file_movie_ids = [i.split(',')[0] for i in csv.split('\n')[:-1]] # last element is a new line
    movie_ids = []
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    queries = 1
    
    for ID in csv_file_movie_ids:
        # query timeout @ 40
        if queries >= 40: queries = query_timeout(10)
            
        else:
            results = get_similar_movie_IDs(conn, api_key, ID)
            queries +=1
            
            for ID_new in results:
                if (str(ID_new), ID) not in movie_ids: # this is literally disgusting, fix it if you have the time
                    movie_ids.append((ID, str(ID_new))) 
                    f.writerow([ID, ID_new])
                
                    
    if update_csv == False: print("Complete")                    

    with open("./movie_ID_sim_movie_ID.csv", 'r') as f:
        csv = f.read()  
    
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Parser to generate movie CSVs")
    parser.add_argument("API_key", type=str)
    
    args = parser.parse_args()
 
    get_csv(str(args.API_key))
    sleep(10) # ensure that the csv is generated
    get_similar_movies("./movie_ID_name.csv", args.API_key)
  
    
        
        
        
        
        
        
        
        
        
        