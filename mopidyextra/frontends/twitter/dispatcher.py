import logging

from pykka.registry import ActorRegistry

from mopidy.backends.base import Backend

from handlers import default_handler

logger = logging.getLogger('mopidyextra.frontends.twitter.dispatcher')

class TwitterDispatcher(object):
    """
    The Twitter session feeds the Twitter dispatcher with requests. The dispatcher
    processes the request and sends the response back to the Twitter session.

    Equivalent to mopidy.frontends.mpd.dispatcher.MpdDispatcher
    """
    def __init__(self, session=None):
        self.context = TwitterContext(self, session=session)

    def _validate_request(self, request):
        # TODO: ensure request is a valid Spotify URI / URL
        return request

    def _find_handler(self, request):
        # Only one handler currently, althouth this may change...
        return default_handler, dict(uri=request)

    def _call_handler(self, request):
        (handler, kwargs) = self._find_handler(request)
        return handler(self.context, **kwargs)

    def handle_request(self, request):
        # Validate request, must be a value Spotify URI / URL
        request = self._validate_request(request)

        # Identify and call handler, return the response 
        return self._call_handler(request)

class TwitterContext(object):
    """
    Provides access to important parts of Mopidy.

    Equivalent to mopidy.frontends.mpd.dispatcher.MpdContext
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
