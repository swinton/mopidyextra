import logging

from pykka.registry import ActorRegistry

from mopidy.backends.base import Backend

from mopidyextra import utils
from mopidyextra.frontends.twitter.handlers import default_handler

logger = logging.getLogger('mopidyextra.frontends.twitter.dispatcher')

class TwitterDispatcher(object):
    """
    The Twitter session feeds the Twitter dispatcher with requests. The dispatcher
    processes the request and sends the response back to the Twitter session.

    Analogous to mopidy.frontends.mpd.dispatcher.MpdDispatcher
    """
    def __init__(self, session=None):
        self.context = TwitterContext(self, session=session)

    def _validate_request(self, request):
        # Is this request a direct message?
        a_direct_message = utils.item_a_direct_message(request)

        # Is this request a mention?
        a_mention = utils.item_a_mention(request)

        # Only allow direct messages or mentions
        if not a_direct_message and not a_mention:
            raise ValueError("Required: a mention or a direct message")

        # Get screen_name and text from request
        screen_name = utils.get_screen_name(request)
        text = utils.get_text(request)

        # Any Spotify tracks?
        tracks = utils.extract_spotify_track_uris(text)
        if not tracks:
            raise ValueError("Required: one or more Spotify track URIs")

        requests = [dict(screen_name=screen_name, text=text, uri=track) for track in tracks]

        return requests

    def _find_handler(self, request):
        # Only one handler currently, althouth this may change...
        return default_handler, request

    def _call_handler(self, request):
        (handler, kwargs) = self._find_handler(request)
        return handler(self.context, **kwargs)

    def handle_request(self, request):
        # Validate request, must be a value Spotify URI / URL
        requests = self._validate_request(request)

        for request in requests:
            # Notify front-end
            yield request
            
            # Identify and call handler 
            self._call_handler(request)
    
class TwitterContext(object):
    """
    Provides access to important parts of Mopidy.

    Analogous to mopidy.frontends.mpd.dispatcher.MpdContext
    """

    def __init__(self, dispatcher, session=None):
        self.dispatcher = dispatcher
        self.session = session
        self._backend = None

    @property
    def backend(self):
        """
        The backend. An instance of :class:`mopidy.backends.base.Backend`.
        """
        if self._backend is None:
            backend_refs = ActorRegistry.get_by_class(Backend)
            assert len(backend_refs) == 1, \
                'Expected exactly one running backend.'
            self._backend = backend_refs[0].proxy()
        return self._backend
