"""
Misc. utility functions for dealing with tweets, primarily.
"""
import json
import re
import urllib

from mopidy import settings

from mopidyextra.utils.decorators import memoized

# REGEXes
TRACK_REGEX = re.compile(r'\b(?:spotify:track:|http://open.spotify.com/track/)(\S+)\b')

def extract_spotify_track_uris(s):
    """
    Extracts Spotify track URIs from a string, returns a de-duplicated list.
    """
    ids = list(set(TRACK_REGEX.findall(s)))
    return ["spotify:track:" + id for id in ids]

def spotify_uri_to_url(uri):
    """
    Transfers a Spotify URI into a Spotify URL.
    
    E.g. spotify:track:7jQwvgefVBVaWkb1PXl910 becomes 
    http://open.spotify.com/track/7jQwvgefVBVaWkb1PXl910
    """
    return re.sub(
        r"^spotify:(?P<type>[^:]+):(?P<id>.+)$", 
        "http://open.spotify.com/\g<type>/\g<id>", 
        uri
    )

@memoized
def lookup_spotify_track(uri):
    res = json.load(urllib.urlopen("http://ws.spotify.com/lookup/1/.json?uri=%s" % urllib.quote(uri)))
    return res

def item_a_direct_message(item):
    """
    Returns True if item appears to be a direct message.
    """
    return "direct_message" in item

def item_a_mention(item):
    """
    Returns True if item appears to be a mention
    """
    if "entities" in item and "user_mentions" in item["entities"]:
        return 0 < len([mention 
                        for mention in item["entities"]["user_mentions"] 
                           if mention["screen_name"] == settings.CUSTOM_TWITTER_SCREEN_NAME])

def get_screen_name(item):
    """
    Returns the screen_name from item.
    """
    if item_a_direct_message(item):
        return item["direct_message"]["sender"]["screen_name"]
    elif item_a_mention(item):
        return item["user"]["screen_name"]
    return None

def get_text(item):
    """
    Returns the text from item.
    """
    if item_a_direct_message(item):
        return item["direct_message"]["text"]
    elif item_a_mention(item):
        return item["text"]
    return None

def get_sender(item):
    """
    Returns the sender of the item.
    """
    if item_a_direct_message(item):
        return item["direct_message"]["sender"]
    elif item_a_mention(item):
        return item["user"]
    return None
    
    