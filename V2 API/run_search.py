from full_search import search_tweets

bearer_token = ""

search_url = "https://api.twitter.com/2/tweets/search/all"


query=''

query_until = ''
most_recent_t = '' 

data_path = ""
f_n = ''


u,v,n=search_tweets(query, query_until, most_recent_t, 500, data_path, f_n, bearer_token, search_url, n=1000)
