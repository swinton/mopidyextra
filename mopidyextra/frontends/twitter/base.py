import logging

import threading

from pykka.actor import ThreadingActor

from mopidy import settings, SettingsError
from mopidy.listeners import BackendListener

import requests

from oauth_hook import OAuthHook

import mopidyextra.utils as utils

from dispatcher import TwitterDispatcher

logger = logging.getLogger('mopidyextra.frontends.twitter')

class TwitterFrontend(ThreadingActor, BackendListener):

    def __init__(self):
        super(TwitterFrontend, self).__init__()
        self.session = TwitterSession(frontend_ref=self.actor_ref)

    def on_start(self):
        logger.info(u'Connecting to Twitter')
        self.session.start()

    def on_stop(self):
        logging.info(u'Disconnecting from Twitter')
        self.session.stop()

    def on_receive(self, message):
        logging.info(u'Received message: %s' % repr(message))

    def track_playback_started(self, track):
        # track (an instance of mopidy.models.Track) has attributes:
        #   uri
        #   name
        #   artists (frozenset)
        #   album
        #   track_no
        #   date
        #   length
        #   bitrate
        #   musicbrainz_id

        # TODO: Tweet #Nowplaying ... / ... requested by @...
        artists = ', '.join([a.name for a in track.artists])
        
        logger.info(u'Now playing track: %s', repr(track))
        
        return

class TwitterSession(object):
    """
    Connects to the user stream, passes incoming data from Twitter off to the dispatcher.

    Equivalent to mopidy.frontends.mpd.MpdSession.
    """
    
    def __init__(self, frontend_ref):
        self.frontend_ref = frontend_ref
        self.dispatcher = TwitterDispatcher(session=self)

        self.access_token = settings.CUSTOM_TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.CUSTOM_TWITTER_ACCESS_TOKEN_SECRET
        self.consumer_key = settings.CUSTOM_TWITTER_CONSUMER_KEY
        self.consumer_secret = settings.CUSTOM_TWITTER_CONSUMER_SECRET

        self._consumer = threading.Thread(target=self.consume)
        self._stop = threading.Event()

    def consume(self):
        userstream_generator = utils.userstream(self.access_token, self.access_token_secret, 
                                                self.consumer_key, self.consumer_secret)

        while not self._stop.is_set():
            obj = userstream_generator.next()
            logger.debug(u'Received %s from stream (stopped: %s)' % (repr(obj), repr(self._stop.is_set())))
            if obj is not None:
                try:
                    for response in self.dispatcher.handle_request(obj):
                        self.frontend_ref.tell(response)
                except ValueError:
                    continue

    def start(self):
        self._consumer.start()

    def stop(self):
        logger.info(u'Stopping, please wait...')
        self._stop.set()
        self._consumer.join()

