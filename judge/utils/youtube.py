"""YouTube links of quiz questions. Only the video id and the start second are kept: every player's
browser loads the video straight from YouTube, nothing goes through this site.

The same rules are repeated in resources/quiz/editor.js (parseVideo) for the instant preview."""
import re
from urllib.parse import parse_qs, urlsplit

MAX_LINK = 500
MAX_START = 24 * 3600
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}')
TIME = re.compile(r'(?:(\d{1,6})h)?(?:(\d{1,6})m)?(?:(\d{1,6})s?)?')
HOSTS = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com',
         'youtube-nocookie.com', 'www.youtube-nocookie.com')
SHORT_HOSTS = ('youtu.be', 'www.youtu.be')
PATHS = ('shorts', 'embed', 'live', 'v')


def seconds(value):
    """'90', '90s', '1m30s', '1h2m3s' -> seconds; anything else is the beginning."""
    match = TIME.fullmatch(value or '')
    if not match:
        return 0
    hours, minutes, secs = (int(part or 0) for part in match.groups())
    total = hours * 3600 + minutes * 60 + secs
    return total if total <= MAX_START else 0


def parse(link):
    """(video id, start second) of a YouTube link, or None when it is not one."""
    link = str(link or '').strip()
    if not link or len(link) > MAX_LINK or any(c.isspace() for c in link):
        return None
    if '://' not in link:
        link = 'https://' + link
    try:
        parts = urlsplit(link)
        host = parts.hostname or ''
    except ValueError:
        return None
    if parts.scheme not in ('http', 'https'):
        return None
    query = parse_qs(parts.query)
    path = [p for p in parts.path.split('/') if p]
    video = ''
    if host in SHORT_HOSTS:
        video = path[0] if path else ''
    elif host in HOSTS:
        if path == ['watch']:
            video = query.get('v', [''])[0]
        elif len(path) >= 2 and path[0] in PATHS:
            video = path[1]
    if not VIDEO_ID.fullmatch(video):
        return None
    fragment = parse_qs(parts.fragment)
    start = query.get('t') or query.get('start') or fragment.get('t') or ['']
    return video, seconds(start[0])


def link(video_id, start=0):
    """The short link shown back in the editor; '' without a video."""
    if not video_id:
        return ''
    return 'https://youtu.be/%s%s' % (video_id, '?t=%d' % start if start else '')
