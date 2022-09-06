import tweepy
import pandas as pd
import numpy as np
import json
from tqdm.notebook import tqdm
import time

# load in list you want to get ids from
with open('list_of_tweet_ids.pkl', 'rb') as f:
    data = pd.read_pickle(f)

data = [int(x) for x in data] # change ids to ints

# reshape data to have 100 columns
k=100
d_ = [data[i:i+k] for i in range(0, len(data), k)]

# get rid of duplicates in final entry (product of reshape)
d_[-1] = list(np.unique(d_[-1]))

hashtags_ = []
text_ = []
failed_responses = []
ids_ = []

bearer_token = ''

# here we are getting original text and hashtags

client = tweepy.Client(bearer_token = bearer_token)

# NOTE THERE IS SOMEHTING GOING ON WITH THE RATE LIMIT - will run into issues

r_saves = []
print('starting')
request_count =0
start_time = time.time()
for x in tqdm(d_):
    request_count +=1
    r = client.get_tweets(x, tweet_fields =['entities']) # this is how tweepy does a request by tweet id
    # you can add more fields using tweet_fields, user_fields, etc.
    r_saves.append(r)
    ht = []
    for tw in r[0]:
        th = []
        if 'hashtags' in tw.entities:
            for a in tw.entities['hashtags']:
                th.append(a['tag'])
            ht.append(th)
        else:
            ht.append(None)

    hashtags_.append(ht)
    text_.append([a.text for a in r[0]])
    ids_.append([a.id for a in r[0]])

    failed_responses.append(r[2])

        # text_.append(None)
        # hashtags_.append(None)
        # ids_.append(None)

    di = {'hashtags': hashtags_, 'text': text_, 'ids': ids_}

    if request_count == 900:
        if time.time() < start_time + 60*15:
            print('sleeping')
            time.sleep(60*15 - time.time() + start_time) # sleep for 15 minutes apart from the last request
            request_count = 0
            start_time = time.time()
    else:
        time.sleep(2)
    # save di as we go
    with open('tweets_by_id.json', 'w') as f:
        json.dump(di, f)

# save all

    
