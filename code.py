#importing Libraries
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt
import tweepy 
from textblob import TextBlob
import re
import warnings
warnings.filterwarnings('ignore') 
#pip install wordcloud
from wordcloud import WordCloud 
from wordcloud import STOPWORDS 

#ENTER THE CREDENTIALS
consumer_key = "ENTER YOUR API KEY"
consumer_secret = "ENTER YOUR API SECRET"
access_key = "ENTER YOUR ACCESS TOKEN"
access_secret = "ENTER YOUR ACCESS TOKEN"

def twitter_setup():
    auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api

screen_name="ImranKhanPTI"

def get_all_tweets(screen_name):
    auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api=tweepy.API(auth)
    
    tweets=[]
    new_tweets=api.user_timeline(screen_name=screen_name, count=200)
    tweets.extend(new_tweets)
    
    oldest=tweets[-1].id-1
    
    while len(new_tweets)>0:
        print(f"Getting tweets before {oldest}")
        #all request will include oldest parameter to exclude the chances of the duplicates 
        new_tweets=api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
        tweets.extend(new_tweets)
        oldest=tweets[-1].id-1
        print(f"Number of Tweets have been downloaded so far: {len(tweets)}")
    
    return tweets

tweets=get_all_tweets(screen_name)
print("7 recent Tweets")
for tweet in tweets[:7]:
    print(tweet.text)
    print()
    
    
data=pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
print (data.head(10))


print(dir(tweets[0]))

data['Length']=np.array([len(tweet.text) for tweet in tweets])
data['ID']=np.array([tweet.id for tweet in tweets])
data['Date']=np.array([tweet.created_at for tweet in tweets])
data['Source']=np.array([tweet.source for tweet in tweets])
data['Likes']=np.array([tweet.favorite_count for tweet in tweets])
data['RTs']=np.array([tweet.retweet_count for tweet in tweets])
print(data.head(10))


mean=np.mean(data['Length'])
print(f"The mean length of the tweets:  {mean}")


lik_max=np.max(data['Likes'])
rt_max=np.max(data['RTs'])

#Extract the index of max
fav=data[data.Likes==lik_max].index[0]
rt=data[data.RTs==rt_max].index[0]

#Print the result
print(f"The most liked tweet is: {data['Tweets'][fav]}")
print(f"Number of likes: {lik_max}")
print("------------------")
print()

#Print the most retweeted tweet
print(f"The most retweeted tweet is: {data['Tweets'][rt]}")
print(f"Number of rt: {rt_max}")
print("------------------")
print()

data.isnull().any()
data.describe()
data['Tweets_Cln']=data.Tweets.str.replace(r'http\S+', '').str.replace(r'@\S+', '').str.replace('&amp', '').str.rstrip()
data=data[data.Likes!=0]
data.head(5)


def analize_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1
data['sentiment'] = np.array([ analize_sentiment(tweet) for tweet in data['Tweets_Cln']])
print(data.head(5))

positive=data.loc[data.sentiment==1,'Tweets'].count()
negative=data.loc[data.sentiment==-1,'Tweets'].count()
neutral=data.loc[data.sentiment==0,'Tweets'].count()

#Let's plot
labels='Postive', 'Negative', 'Neutral'
sizes=[positive, negative, neutral]
explode=(0, 0.1, 0)
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=True, startangle=0)
ax1.axis('equal') 
plt.show()


edu_count = data.Tweets[data.Tweets.str.contains('education', flags=re.IGNORECASE)].count() 
print(f"Imran Khan has tweeted about Education {edu_count} times.")
print("--------------------------------")
print()
data.Tweets[data.Tweets.str.contains('education', flags=re.IGNORECASE)]


stopwords = set(STOPWORDS)
stopwords.add("will")
stopwords.update(["say","said", "let", "now", "go", "talk", "many", "Dear", "hello", "watch"])
wordcloud_hc = WordCloud(max_font_size=40, relative_scaling=.5,stopwords=stopwords, background_color="black").generate(data['Tweets_Cln'].str.cat())
plt.figure(figsize=[16,8])
plt.imshow(wordcloud_hc)
plt.axis("off")
plt.show()
