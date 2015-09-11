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
		event_data = json.loads(self.request.body)
		session_key = 'session:' + event_data['session_key']

		bot_message = json.dumps({'event': event_data['message']})

		# check if session exists in local store
		if session_key not in self.local_sessions.sessions:
			# cache miss. go to redis
			session_store = tornadis.Client()
			yield session_store.connect()
			hostname = yield session_store.call('HGET', 'sessions', session_key)

			if not hostname:
				raise NoSessionInStoreException("session store does not contain a host for session: " + session_key)
		else:
			try:
				hostname = self.local_sessions.sessions[session_key]
			except:
				raise NoSessionInStoreException("session cache does not contain a host for session: " + session_key)

		print "bot url: ", hostname

		# request an event from a bot
		request = httpclient.HTTPRequest(	url=hostname,
							body=bot_message,
							method="POST",
							connect_timeout=1,
							request_timeout=1 )

		http_client = httpclient.AsyncHTTPClient()
		action = yield http_client.fetch(request)

		# TODO check the action response for bad format

		print action.body

		self.write(json.dumps(action.body))
		self.finish()
