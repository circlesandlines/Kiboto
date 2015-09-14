import json
import tornado.gen
import tornado.web
from tornado import httpclient
import tornadis

class NoSessionInStoreException(Exception): pass

class EventHandler(tornado.web.RequestHandler):

	def initialize(self, local_sessions):
		self.local_sessions = local_sessions

	@tornado.gen.coroutine
	def post(self):
		# extract POST event data
		# TODO handle non-json error
		event_data = json.loads(self.request.body)
		session_key = 'session:' + event_data['session_key']

		# TODO handle 'no event object' in message
		bot_message = json.dumps({'event': event_data['message']})

		# check if session exists in local store
		if session_key not in self.local_sessions.sessions:
			# cache miss. go to redis
			session_store = tornadis.Client()

			# TODO handle connection error here
			yield session_store.connect()
			hostname = yield session_store.call('HGET', 'sessions', session_key)

			if not hostname:
				# TODO this should return an error to game
				# does it return a 500? should be 404, no session found
				raise NoSessionInStoreException("session store does not contain a bot for session: " + session_key)
		else:
			try:
				hostname = self.local_sessions.sessions[session_key]
			except:
				# TODO this should return an error to game
				# does it return a 500? should be 404, no session found
				raise NoSessionInStoreException("session cache does not contain a bot for session: " + session_key)

		print "bot url: ", hostname

		# request an event from a bot
		request = httpclient.HTTPRequest(	url=hostname,
							body=bot_message,
							method="POST",
							connect_timeout=1,
							request_timeout=1 )

		# TODO handle connection error
		http_client = httpclient.AsyncHTTPClient()
		action = yield http_client.fetch(request)

		# TODO check the action response for bad format
		# ie. just make sure its json

		print action.body

		self.write(json.dumps(action.body))
		self.finish()
