import os
from urllib.parse import urlencode
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tweetstream

clients = set()

def tweetstream_callback(tweet):
    if tweet is None:
        logging.error('tweet is none')
        return

    if 'retweeted_status' in tweet:
        return

    for client in clients:
        client.write_message(tweet)

if 'TWITTER_ACCESS_TOKEN' in os.environ:
    tweetstream_config = {
        "twitter_consumer_key": os.environ["TWITTER_CONSUMER_KEY"],
        "twitter_consumer_secret": os.environ["TWITTER_CONSUMER_SECRET"],
        "twitter_access_token": os.environ["TWITTER_ACCESS_TOKEN"],
        "twitter_access_token_secret": os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    }

    params = {
        'track': '#twitter'
    }

    stream = tweetstream.TweetStream(tweetstream_config)
    stream.fetch("/1.1/statuses/filter.json?" + urlencode(params), callback=tweetstream_callback)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open('static/index.html') as f:
            self.write(f.read())

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.stream.set_nodelay(True)
        clients.add(self)

    def on_close(self):
        clients.discard(self)

class AuthLoginHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self._on_auth)
            return
        if self.get_argument("denied", None):
            # TODO: need to change if we ever have pages that absolutely require authentication
            self.redirect(self.get_argument('next'))
            return
        self.authorize_redirect('/auth/login?next=' + self.get_argument('next'))
    def _on_auth(self, user):
        user_data = {
            'screen_name': user['screen_name'],
            'access_token': user['access_token'],
            'profile_image_url': user['profile_image_url'],
        }
        self.set_secure_cookie("chat_user",
                               tornado.escape.json_encode(user_data))
        self.redirect(self.get_argument('next'))


application = tornado.web.Application(
[
    (r"/", MainHandler),
    (r"/ws", WebSocketHandler),
    (r"/auth/login", AuthLoginHandler),
],
cookie_secret=os.environ["COOKIE_SECRET"],
template_path='templates',
static_path=os.path.join(os.path.dirname(__file__), "static"),
twitter_consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
twitter_consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
# debug=True,
)

if __name__ == "__main__":
    application.listen(os.environ['PORT'])
    tornado.ioloop.IOLoop.instance().start()