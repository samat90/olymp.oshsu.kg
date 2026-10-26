"""Error messages without the inside of the sandbox.

Compiler errors and tracebacks keep every word of the message, but folders are cut down to
the file name (/tmp/tmp8ai6qfxa/main.py -> main.py) and the frames of our own Python loader
are dropped, so the output says nothing about how the server is laid out.
The site uses the same rules for errors that come from the judges (judge/utils/clean_output.py).
"""
import re

_LOADER_FRAME = re.compile(r'^  File "(?:[^"\n]*/)?-loader\.py", line \d+, in [^\n]*\n(?:    [^\n]*\n)?', re.M)
_FROZEN_FRAME = re.compile(r'^  File "<frozen [^">\n]+>", line \d+, in [^\n]*\n(?:    [^\n]*\n)?', re.M)
_PATH = re.compile(r'(?<![\w.~/-])/(?:[\w.+@-]+/)+([\w.+@-]+)')
# The runner compiles the user's file as problem "main", which DMOJ saves as maincpp.cpp and so on.
_MAIN = re.compile(r'(?:(?<=\x1b\[K)|(?<![\w.-]))main([a-z]+)\.\1(?![\w-])')
_JAVA_PREFIX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: ', re.M)
# kotlinc cannot unpack its colour library into /tmp inside the sandbox and says so; the build is fine.
_JANSI_LOCK = re.compile(r'^[^\n]*jansi-[\w.-]*\.lck \(Permission denied\)\r?(?:\n|$)', re.M)


def clean(text):
    if not text:
        return text
    text = _LOADER_FRAME.sub('', text)
    text = _FROZEN_FRAME.sub('', text)
    text = _JAVA_PREFIX.sub('', text)
    text = _JANSI_LOCK.sub('', text)
    text = _PATH.sub(r'\1', text)
    return _MAIN.sub(r'main.\1', text)
