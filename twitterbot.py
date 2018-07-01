import base64
import tweepy
from time import sleep
from os import path

from secrets import consumer_key, consumer_secret, access_token, access_token_secret
from satoshis_place import SatPlaceSocket
import config

def download_latest_canvas(imagename = path.join(config.satoshis_image_folder, 'latest_canvas.png')):
    sps = SatPlaceSocket()
    sps.emitLatestPixels()
    sps.wait(seconds = 1)

    img = sps.latestImage
    imgdata = base64.b64decode(img)
    filename = imagename  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)

def initialize_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

def update_twitter_status(api):
    print("Posting canvas to twitter")
    download_latest_canvas()
    api.update_with_media(path.join(config.satoshis_image_folder, "latest_canvas.png"))

if __name__ == "__main__":
    api = initialize_api()
    while True:
        print("Starting up twitter bot")
        update_twitter_status(api)
        sleep(config.sleep_period)
