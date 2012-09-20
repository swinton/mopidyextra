import logging
import httplib
import json
import ssl
import threading
import time

from pykka.actor import ThreadingActor

from mopidy import settings, SettingsError
from mopidy.listeners import BackendListener

from mopidyextra import utils
from mopidyextra.packages import tweepy
from mopidyextra.frontends.twitter.dispatcher import TwitterDispatcher

logger = logging.getLogger('mopidyextra.frontends.twitter')

class TwitterFrontend(ThreadingActor, BackendListener):
    requests = {}

    def __init__(self):
        super(TwitterFrontend, self).__init__()
        self.session = TwitterSession(frontend_ref=self.actor_ref)

        self.access_token = settings.CUSTOM_TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.CUSTOM_TWITTER_ACCESS_TOKEN_SECRET
        self.consumer_key = settings.CUSTOM_TWITTER_CONSUMER_KEY
        self.consumer_secret = settings.CUSTOM_TWITTER_CONSUMER_SECRET

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        self.api = tweepy.API(auth)

    def on_start(self):
        self.session.start()

    def on_stop(self):
        self.session.stop()

    def on_receive(self, message):
        logging.info(u'Received message: %s' % repr(message))

        if "uri" in message and "screen_name" in message:
            self.requests[message["uri"]] = message["screen_name"]

    def track_playback_started(self, track):
        try:
            # Tweet #Nowplaying ... / ... requested by @...
            artists = ', '.join([a.name for a in track.artists])
            uri = track.uri
            screen_name = self.requests.pop(uri)

            # Send tweet!
            tweet = u'#Nowplaying %s / %s, requested by @%s %s' % (artists, track.name, screen_name, utils.spotify_uri_to_url(uri))
            self.api.update_status(status=tweet, lat="50.82519295639108", long="-0.14594435691833496", display_coordinates="1")
            logger.info(u'Tweeted: %s' % tweet)

        except KeyError:
            # Not requested through Twitter?
            pass
        
        except Exception, e:
            logger.debug(u'Unexpected exception: %s' % str(e))

        return

class TwitterSession(tweepy.StreamListener):
    """
    Connects to the user stream, passes incoming data from Twitter off to the dispatcher.

    Analogous to mopidy.frontends.mpd.MpdSession.
    """
    
    def __init__(self, frontend_ref):
        super(tweepy.StreamListener, self).__init__()

        self.frontend_ref = frontend_ref
        self.dispatcher = TwitterDispatcher(session=self)

        self.access_token = settings.CUSTOM_TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.CUSTOM_TWITTER_ACCESS_TOKEN_SECRET
        self.consumer_key = settings.CUSTOM_TWITTER_CONSUMER_KEY
        self.consumer_secret = settings.CUSTOM_TWITTER_CONSUMER_SECRET

        self._consumer = threading.Thread(target=self.consume)
        self._stop = threading.Event()

        self._stream = None

    def consume(self):
        logger.info(u'Connecting to Twitter')

        # Create an auth handler
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        
        # Connect to stream
        self._stream = tweepy.Stream(auth, self, secure=True)

        while not self._stop.is_set():

            try:
                self._stream.userstream()

            except httplib.IncompleteRead, e:
                logging.debug(u'Exception: %s' % str(e))
                time.sleep(5)

            except ssl.SSLError, e:
                logging.debug(u'Exception: %s' % str(e))
                time.sleep(5)

            except Exception, e:
                logging.debug(u'Unexpected exception: %s' % str(e)) 
                time.sleep(5)

    def start(self):
        self._consumer.start()

    def stop(self):
        logging.info(u'Disconnecting from Twitter... ')
        self._stop.set()
        self._stream.disconnect()
        self._consumer.join()
        logging.info(u'Disconnected from Twitter.')

    def on_data(self, data):
        if not data.strip():
            return True
        
        # Decode JSON data
        obj = json.loads(data)
        logging.debug(u'Received: %s from twitter' % repr(obj))

        if obj is not None:
            try:
                for response in self.dispatcher.handle_request(obj):
                    self.frontend_ref.tell(response)
            except ValueError:
                pass

        return True
