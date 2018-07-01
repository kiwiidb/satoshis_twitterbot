import wget
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from multiprocessing import Process

from image import convert_image
import config
from satoshis_place import SatPlaceSocket
from twitterbot import initialize_api

#download image, convert image, send to satoshis place, answer tweet id with invoice
def handleTweet(imgurl, name, tweetid, api, startX, startY, satPlaceSocket):
    print("startX: ", startX)
    print("startY: ", startY)
    filename = wget.download(imgurl, out=config.uploaded_image_folder)
    cj = convert_image(filename, (config.image_size, config.image_size), startX, startY)
    emitResult = satPlaceSocket.emitNewOrder(cj)
    if emitResult:
        satPlaceSocket.wait(seconds=5)
        try:
            invoice = satPlaceSocket.receivedInvoice
            print(invoice)
            api.update_status("@" + name + " " + invoice['paymentRequest'], tweetid)
        except AttributeError:
            print("Failed to get invoice")
            api.update_status("Sorry @" + name + ", try again please!", tweetid)
    else:
            api.update_status("Sorry @" + name + ", try again please!", tweetid)



#Import credentials
from secrets import consumer_key, consumer_secret, access_token, access_token_secret
#This is a listener that calls a subprocess processing the tweet
class StdOutListener(StreamListener):    
    
    def __init__(self):
        self.satPlaceSocket = SatPlaceSocket()
        self.api = initialize_api()
        self.coord = 1100
    def on_data(self, data):
        tweet = json.loads(data)
        try:
            imgurl = tweet['entities']['media'][0]['media_url']
        except KeyError:
            imgurl = False
        tweetid = tweet['id_str']
        name = tweet['user']['screen_name']
        if imgurl:
            p = Process(target=handleTweet, args=(imgurl,name, tweetid, self.api, int(self.coord%1000), config.image_size*int(self.coord/1000), self.satPlaceSocket))
            p.start()
            self.coord = (self.coord + config.image_size) % 1e6
            print("handled tweet with id", tweetid)

    def on_error(self, status):
        print(status)
        
if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    print("Starting stream")
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data from mentions
    stream.filter(track=[config.twitter_handle])
