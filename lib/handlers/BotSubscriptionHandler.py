
"""

	Bot Subscription handler

	Handles requests to subscribe to an inactive session.

	The bots will find the session and player they want to be,
	then they will send their hostname information to this handler.
	the handler will update the session record, so that the Session Initializer
	can finish its process, and allow the game to start.

	url format:
		<host>:<port>/subscribe?hostname=<urlencoded hostname>&session_key=<session key"

	eg.
		http://localhost:9090/subscribe?hostname=http%3A%2F%2Flocalhost%3A9091%2Fevent&session_key=1
"""

import tornado.web
import tornadis

class BotSubscriptionHandler(tornado.web.RequestHandler):
	def initialize(self, sync_redis):
		self.sync_redis = sync_redis

	@tornado.gen.coroutine
	def get(self):

		# TODO handle missing arguments. notify client
		hostname = self.get_argument('hostname')
		session_key = self.get_argument('session_key')

		# use non-async redis, so that we can't overwrite something that
		# has just been written, while the callback is waiting for a reply.
		# not sure if this is possible, but just in case until verified!

		# TODO handle None return
		self.sync_redis.hset('sessions', session_key, hostname)
		keys = self.sync_redis.hgetall('sessions')
		print 'hostname set. all keys: ', keys

		self.finish()
