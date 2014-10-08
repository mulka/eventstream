import os
from urllib.parse import urlencode

import tornado.ioloop
import tornado.web
import tornado.websocket
import tweetstream

clients = set()

def tweetstream_callback(tweet):
    for client in clients:
        client.write_message(tweet)

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

application = tornado.web.Application(
[
    (r"/", MainHandler),
    (r"/ws", WebSocketHandler),
],
template_path='templates',
static_path=os.path.join(os.path.dirname(__file__), "static"),
# debug=True,
)

if __name__ == "__main__":
    application.listen(os.environ['PORT'])
    tornado.ioloop.IOLoop.instance().start()