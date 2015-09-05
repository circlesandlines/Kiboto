
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

		hostname = self.request.get_argument('hostname')
		session_key = self.request.get_argument('session_key')

		session_store = tornadis.Client(client_timeout=1)
		yield session_store.connect()
		yield session_store.call('SET', session_key, hostname)

		self.write()
		self.finish()
