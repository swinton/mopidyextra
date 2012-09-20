# mopidyextra

Extra goodies for [mopidy](http://mopidy.com/), including the ability to control a mopidy instance using [Twitter](http://twitter.com/).

## Installation

* Patch your mopidy install to allow custom settings.

* Install mopidyextra.

## Configuration

* Update your settings.py to include the path to mopidyextra:

```python
import sys

sys.path.append("/path/to/mopidyextra")
```

* Add mopidyextra.frontends.twitter.TwitterFrontend to FRONTENDS in settings.py:

```python
FRONTENDS = (
    u'mopidy.frontends.mpd.MpdFrontend',
    u'mopidyextra.frontends.twitter.TwitterFrontend',
)
```

* Add your Twitter details in settings.py:

```python
CUSTOM_TWITTER_ACCESS_TOKEN = "{{YOUR_TWITTER_ACCESS_TOKEN}}"
CUSTOM_TWITTER_ACCESS_TOKEN_SECRET = "{{YOUR_TWITTER_ACCESS_TOKEN_SECRET}}"
CUSTOM_TWITTER_CONSUMER_KEY = "{{YOUR_TWITTER_CONSUMER_KEY}}"
CUSTOM_TWITTER_CONSUMER_SECRET = "{{YOUR_TWITTER_CONSUMER_SECRET}}"
CUSTOM_TWITTER_SCREEN_NAME = "{{YOUR_TWITTER_SCREEN_NAME}}"
```

* Run mopidy as usual:

    $ mopidy

## Contact

@[steveWINton](http://twitter.com/steveWINton).