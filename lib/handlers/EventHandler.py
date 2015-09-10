import json
import tornado.gen
import tornado.web
from tornado.httpclient import AsyncHTTPClient
import tornadis

class EventHandler(tornado.web.RequestHandler):

	def initialize(self, local_sessions):
		self.local_sessions = local_sessions

	@tornado.gen.coroutine
	def post(self):
		# extract POST event data
		event_data = json.loads(self.request.body)
		session_key = event_data['session_key']

		# check if session exists in local store
		if session_key not in self.local_sessions.sessions:
			session_store = tornadis.Client(client_timeout=1)
			yield session_store.connect()
			hostname = yield session_store.call('GET', session_key)
		else:
			hostname = self.local_sessions.sessions[session_key]

		# request an event from a bot
		bot = AsyncHTTPClient()
		action = yield bot.fetch(hostname)

		# TODO check the action response for bad format

		self.write(action)
		self.finish()
