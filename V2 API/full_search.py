import requests
import json
import pandas as pd
import datetime, time
import numpy as np

# returns tweets in reverse chronological order

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    # make query
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200: # not ok
        raise Exception(response.status_code, response.text)
    return response.json()


def process_tweets(t):
    try:
        # save user info

        users = []
        for u in t['includes']['users']:
            users.append(u)

        # save_tweet_info
        tweets = []
        for u in t['data']:
            tweets.append(u)

        return(users, tweets)
    except:
        return(np.nan, np.nan)
    
def search_tweets(q, query_until, most_recent_t,N, data_path, file_name, bearer_token, search_url, n = 5000, n_token = None):
    a=0
    if N>500:
        print('N needs to be equal too or less than 500.')
        return np.nan
    elif N<10:
        print('N needs to be equal too or greater than 10.')
        return np.nan
    count = 0 # file number
     #number of tweets per file
    tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
    users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])

    if n_token == None:
        # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
        # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
        query_params = {'query': q,
                        'tweet.fields': 'author_id,created_at,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,geo,entities,attachments', 
                        'user.fields':'description,created_at,location,pinned_tweet_id,protected,public_metrics,url',
                        'expansions':'author_id,referenced_tweets.id.author_id',
                        'end_time':most_recent_t, # where search starts from
                        'max_results':N}
        #                'since_id':s_id}

        headers = create_headers(bearer_token)
        json_response = connect_to_endpoint(search_url, headers, query_params)
        t=json_response #json.dumps(json_response, sort_keys=True)

        n_token = t['meta']['next_token']
    #     s_id = t['meta']['newest_id']

        u, tw = process_tweets(t)

        oldest_t = tw[-1:][0]['created_at']

        tweets_save=tweets_save.append(tw)
        users_save=users_save.append(u)
        
    else:
        oldest_t = most_recent_t
        # run over times
    while datetime.datetime.fromisoformat(oldest_t.replace("Z", ""))>datetime.datetime.fromisoformat(query_until.replace("Z", "")): # while we are before start time
#     for i in tqdm(range(1440)):
        try:
            # errors = []
            
            query_params = {'next_token':n_token,
                'query': q,
                'tweet.fields': 'author_id,created_at,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,geo,entities,attachments', 
                'user.fields':'description,created_at,location,pinned_tweet_id,protected,public_metrics,url',
                'expansions':'author_id,referenced_tweets.id.author_id',
                'end_time':most_recent_t, # where search starts from
                'max_results':N}

            headers = create_headers(bearer_token)
            json_response = connect_to_endpoint(search_url, headers, query_params)
            t=json_response #json.dumps(json_response, sort_keys=True)

            u, tw = process_tweets(t)
            oldest_t = tw[-1:][0]['created_at']
            # print(oldest_t)
            n_token = t['meta']['next_token']
            print(n_token)
            a=0

            
            tweets_save=tweets_save.append(tw)
            users_save=users_save.append(u)

            # if length > some number then save

            if len(tweets_save) >= n:
                print('trying to save')
                print(oldest_t)
                print(file_name)
                print(f'tweets_{file_name}_{oldest_t}_{n_token}.json')
                file_name = int(count)
                tweets_save=tweets_save.reset_index()
                users_save = users_save.reset_index()
                tweets_save.to_json(f'tweets_{file_name}_{oldest_t}_{n_token}.json')
                users_save.to_json(f'users_{file_name}_{oldest_t}_{n_token}.json')
                count +=1
                tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
                users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])
                print(n_token)
                print('saved')

            time.sleep(1.00) # should stop us hitting rate limit
        except:
            print("Rate Limit Reached: Wating 10 seconds - n_token: " + str(n_token))
            time.sleep(10)
            a+=1

            if a>5:
                print(n_token)
                print('Failed, a>5')
                return np.nan
            
    file_name = int(count)
    tweets_save=tweets_save.reset_index()
    users_save = users_save.reset_index()
    tweets_save.to_json(data_path+f'tweets_{file_name}_{oldest_t}_{count}.json')
    users_save.to_json(data_path+f'users_{file_name}_{oldest_t}_{count}.json')
    count +=1
    tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
    users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])
    print('Finishing \n')
    print(len(tweets_save))
    print("\n")
            
    return tweets_save,users_save, n_token