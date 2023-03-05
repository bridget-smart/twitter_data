import requests
import os
import json
import pandas as pd
import numpy as np
import time
# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = "AAAAAAAAAAAAAAAAAAAAALW5NwEAAAAAgRWt0zN6BZhWsodtxft0oYzvuks%3De7zr1szz6jnKxLXR7IZXkAVZLQOKlc8bH3Bnio3eaPox2JqvUV"


def create_url(user_id):
    # Replace with user ID below
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def get_params(token):
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    if token:
        return {"pagination_token": token, "max_results": 100, "tweet.fields": 'author_id,created_at,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,geo,entities,attachments', 'user.fields':'description,created_at,location,pinned_tweet_id,protected,public_metrics,url','expansions':'author_id,referenced_tweets.id.author_id'}

    else:
        return {"max_results": 100, "tweet.fields": 'author_id,created_at,in_reply_to_user_id,lang,public_metrics,referenced_tweets,source,geo,entities,attachments', 'user.fields':'description,created_at,location,pinned_tweet_id,protected,public_metrics,url','expansions':'author_id,referenced_tweets.id.author_id'}

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    # print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
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

        return(pd.DataFrame(users), pd.DataFrame(tweets))
    except:
        return(np.nan, np.nan)

def get_tweets_by_user(user_id):
    tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
    users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])

    n = 250 # save every n tweets
    data_path = 'tweets/'

    url = create_url(user_id)
    token = None

    # do first search
    params = get_params(token)
    json_response = connect_to_endpoint(url, params)

    t=json_response #json.dumps(json_response, sort_keys=True)
    # print(t)
    try:
        token = t['meta']['next_token']
    except:
        token = None

    u, tw = process_tweets(t)
    
    tweets_save=pd.concat([tweets_save,tw], axis=0, join='outer')#tweets_save.append(tw)
    users_save=pd.concat([users_save,u], axis=0, join='outer') #users_save.append(u)
    count = 1

    # print(len(tweets_save))

    # if length > some number then save
    while token: # if none then we have gotten them all

        # print(len(tweets_save))
        errors = []
        
        params = get_params(token)
        
        json_response = connect_to_endpoint(url, params)

        t=json_response #json.dumps(json_response, sort_keys=True)
        
        try:
            token = t['meta']['next_token']
        except:
            token = None

        u, tw = process_tweets(t)
        
        tweets_save=pd.concat([tweets_save,tw], axis=0, join='outer')#tweets_save.append(tw)
        users_save=pd.concat([users_save,u], axis=0, join='outer') #users_save.append(u)

        # if length > some number then save

        if len(tweets_save) >= n:
            file_name = int(count)
            tweets_save=tweets_save.reset_index()
            users_save = users_save.reset_index()
            tweets_save.to_json(data_path+"temp/"+f'temp_tweets_{file_name}_{user_id}.json')
            users_save.to_json(data_path+"temp/"+f'temp_users_{file_name}_{user_id}.json')
            count +=1
            tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
            users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])
            # print(n_token)

        time.sleep(1)

        # except:
        #     print("Rate Limit Reached: Wating 30 seconds")
        #     time.sleep(30)
        # takes around 1.2 seconds per iteration, so shouldn't hit rate limit
    # print('saving')
    file_name = int(user_id)
    tweets_save=tweets_save.reset_index()
    users_save = users_save.reset_index()

            
    file_name = int(count)
    tweets_save=tweets_save.reset_index()
    users_save = users_save.reset_index()
    tweets_save.to_json(data_path+f'tweets_{user_id}.json')
    users_save.to_json(data_path+f'users_{user_id}.json')
    count +=1
    tweets_save=pd.DataFrame(columns = ['lang', 'id', 'text', 'author_id', 'created_at', 'entities', 'source', 'public_metrics'])
    users_save = pd.DataFrame(columns = ['public_metrics', 'created_at', 'location', 'id', 'protected', 'url', 'username', 'name', 'description'])
    # print('Finishing \n')
    # print(len(tweets_save))
    # print("\n")

    return 1




