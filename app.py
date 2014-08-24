import os

import tornado.ioloop
import tornado.web
import tornado.websocket
import tweetstream

clients = set()

min_lat = 42.2
min_lng = -83.8
max_lat = 42.3
max_lng = -83.7

def tweetstream_callback(tweet):
    if 'retweeted_by' in tweet:
        return

    coord = tweet['coordinates']['coordinates']
    lng = coord[0]
    lat = coord[1]
    coord_in_bounds = lat < min_lat or lat > max_lat or lng < min_lng or lng > max_lng
    if coord_in_bounds and tweet['place']['name'] != 'Ann Arbor':
        return

    for client in clients:
        client.write_message(tweet)

tweetstream_config = {
    "twitter_consumer_key": os.environ["TWITTER_CONSUMER_KEY"],
    "twitter_consumer_secret": os.environ["TWITTER_CONSUMER_SECRET"],
    "twitter_access_token": os.environ["TWITTER_ACCESS_TOKEN"],
    "twitter_access_token_secret": os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
}

query_string = "locations=%s,%s,%s,%s" % (min_lng, min_lat, max_lng, max_lat)
# query_string = "track=%23twitter"

stream = tweetstream.TweetStream(tweetstream_config)
stream.fetch("/1.1/statuses/filter.json?" + query_string, callback=tweetstream_callback)


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