
"""
	The bots will find the session and player they want to be,
	then they will send their hostname information to this handler.
	the handler will update the session record, so that the Session Initializer
	can finish its process, and allow the game to start.
"""

import tornado.web
import tornadis

class BotSubscriptionHandler(tornado.web.RequestHandler):
	@tornado.gen.coroutine
	def get(self):

		hostname = self.get_argument('hostname')
		session_key = self.get_argument('session_key')

		session_store = tornadis.Client()
		yield session_store.connect()
		# NOTE should do some syncronous checks here before setting
		# so that we can notify the bot if its already been set in the time
		# that it took to join
		# reply with error so the bot can keep searching
		# try dropping in pyredis in here. should hold up the ioloop! :D
		yield session_store.call('HSET', 'sessions', session_key, hostname)
		keys = yield session_store.call('HGETALL', 'sessions')
		print 'hostname set. all keys: ', keys

		self.write("")
		self.finish()
