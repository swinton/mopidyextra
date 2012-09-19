import logging

from mopidy.backends.base import PlaybackController

logger = logging.getLogger('mopidyextra.frontends.handlers')

def default_handler(context, screen_name, text, uri):
    """Default handler, adds URI to playlist"""
    logger.info(u"Default handler request %s from %s" % (uri, screen_name))

    # Decode the URI
    track = context.backend.library.lookup(uri).get()
    if track is None:
        raise ValueError(u"No such song: %s" % uri)

    # Add the track
    cp_track = context.backend.current_playlist.add(track).get()

    # Start playing the track already, if not playing already
    state = context.backend.playback.state.get()
    if state != PlaybackController.PLAYING:
        context.backend.playback.play().get()

    return dict(id=cp_track.cpid, screen_name=screen_name, text=text, uri=uri)
