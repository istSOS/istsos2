"""
Copyright (c) 2014 Kenneth Reitz.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""




from .oauth1_auth import OAuth1
from .oauth1_session import OAuth1Session
from .oauth2_auth import OAuth2
from .oauth2_session import OAuth2Session, TokenUpdated

__version__ = '0.4.2'

import requests
if requests.__version__ < '2.0.0':
    msg = ('You are using requests version %s, which is older than '
           'requests-oauthlib expects, please upgrade to 2.0.0 or later.')
    raise Warning(msg % requests.__version__)

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
   class NullHandler(logging.Handler):
       def emit(self, record):
           pass

logging.getLogger('requests_oauthlib').addHandler(NullHandler())
