import os

import tornado.ioloop
import tornado.web
import tornado.websocket
import tweetstream

clients = set()

def tweetstream_callback(message):
    for client in clients:
        client.write_message(message)

tweetstream_config = {
    "twitter_consumer_key": os.environ["TWITTER_CONSUMER_KEY"],
    "twitter_consumer_secret": os.environ["TWITTER_CONSUMER_SECRET"],
    "twitter_access_token": os.environ["TWITTER_ACCESS_TOKEN"],
    "twitter_access_token_secret": os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
}

# query_string = "locations=-83.8,42.2,-83.7,42.3"
query_string = "track=%23twitter"

stream = tweetstream.TweetStream(tweetstream_config)
stream.fetch("/1.1/statuses/filter.json?" + query_string, callback=tweetstream_callback)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.stream.set_nodelay(True)
        clients.add(self)

    def on_close(self):
        clients.discard(self)


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", WebSocketHandler),
], template_path='templates')

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()