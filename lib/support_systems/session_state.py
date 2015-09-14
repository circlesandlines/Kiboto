import tornado.gen
import tornadis

class SessionHandler:
	def __init__(self, update_period_ms=4000):
		self.sessions = {}
		self.update_period_ms = update_period_ms

	@tornado.gen.coroutine
	def update_from_redis(self):
		""""""

		session_store = tornadis.Client()
		# TODO handle bad connection
		yield session_store.connect()
		# handle None return
		self.sessions = yield session_store.call('HKEYS')
