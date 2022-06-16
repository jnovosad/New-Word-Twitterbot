''' Run this module in the command line as:
    python -m getUser <Twitter Username>    '''

import tweepy
import string
from login import twitter_login
import time
import sys

'''Returns a list of 20 most recent tweets by the given username.'''
def get_most_recent_tweets(username, api):
    statusList = api.user_timeline(screen_name=username)
    
    return statusList

'''Writes the content to a txt file. Doesn't return a value.'''
def write_to_file(filename, text):
    f = open(filename, "w")
    f.write(str(text))
    f.close()

'''Reads content from a txt file. Returns the content.'''
def read_from_file(filename):
    f = open(filename, "r")
    text = f.read()
    f.close()

    return text

'''Gets the full text of a tweet, parses it into individual words and adds to an existing list.'''
def add_to_list(lst, item):
    lst.extend(item.full_text.split())

'''Generates a query to be used when using the Twitter search API.'''
def word_as_query(word, user):
    query = word + " from:" + user
    return query

'''Prints a status update (identical to tweet_update) to the console.'''
def print_update(word, user):
    print("Hi Twitter world! @" + user + " tweeted the word '" + 
            word.lower() + "'" + " for the first time in 7 days.")

'''Prints a status update (identical to print_update) to the account connected with the Twitter API.'''
def tweet_update(api, word, user):
    api.update_status(status="Hi Twitter world! @" + user + " tweeted the word '" + 
                        word.lower() + "'" + " for the first time in 7 days.")

def main():
    twitter_API = twitter_login()

    try:
        twitter_user = sys.argv[1]
    except IndexError:
        print("You need to input a Twitter username.")
        sys.exit(1)

    tweet_id_file = "mostRecentTweetID.txt"

    most_recent_tweet_ID = get_most_recent_tweets(twitter_user, twitter_API)[0].id
    write_to_file(tweet_id_file, most_recent_tweet_ID)

    while True:
        read_from_file(tweet_id_file)

        new_tweet_list = twitter_API.user_timeline(screen_name=twitter_user, 
                                                since_id=most_recent_tweet_ID,
                                                include_rts=False,
                                                tweet_mode="extended")
 
        words_since_last_update = []

        # NOTE: can replace with exception handling later
        if len(new_tweet_list) > 0:
            for tweet in new_tweet_list:
                add_to_list(words_since_last_update, tweet)

            for word in words_since_last_update:
                if ((word.startswith('http') == False) and 
                    (word.startswith('&amp') == False) and 
                    (word.strip(string.punctuation)!='')):

                    stripped_word = word.strip(string.punctuation)
                    query = word_as_query(stripped_word, twitter_user)

                    if len(twitter_API.search(q=query,
                                            max_id=most_recent_tweet_ID,
                                            count=3,
                                            include_rts=False,
                                            tweet_mode="extended")) == 0:
                        tweet_update(twitter_API, stripped_word, twitter_user)
                        print_update(stripped_word, twitter_user)

            write_to_file(tweet_id_file, new_tweet_list[0].id)

        time.sleep(60*15)


if __name__ == "__main__":
    main()
