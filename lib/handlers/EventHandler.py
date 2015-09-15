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
		try:
			event_data = json.loads(self.request.body)
		except Exception as e:
			raise NotJSONException("don't sent non-json event data")

		session_key = 'session:' + event_data['session_key']

		try:
			bot_message = json.dumps({'event': event_data['message']})
		except KeyError:
			raise NoEventMessageException("no 'message' was sent")

		# check if session exists in local store
		if session_key not in self.local_sessions.sessions:
			# cache miss. go to redis
			session_store = tornadis.Client()

			yield session_store.connect()
			hostname = yield session_store.call('HGET', 'sessions', session_key)

			if not hostname:
				reply = {
					'error': 1,
					'err_msg': "server-side session store error"
				}
				self.write(json.dumps(reply))
				self.finish()
				raise NoSessionInStoreException("session store does not contain a bot for session: " + session_key)
		else:
			try:
				hostname = self.local_sessions.sessions[session_key]
			except:
				reply = {
					'error': 1,
					'err_msg': "server-side session cache error"
				}
				self.write(json.dumps(reply))
				self.finish()

				raise NoSessionInStoreException("session cache does not contain a bot for session: " + session_key)

		print "bot url: ", hostname

		# request an event from a bot
		request = httpclient.HTTPRequest(	url=hostname,
							body=bot_message,
							method="POST",
							connect_timeout=1,
							request_timeout=1 )

		# TODO handle connection error
		try:
			http_client = httpclient.AsyncHTTPClient()
			action = yield http_client.fetch(request)
		except Exception as e:
			# this seems lazy, but really, no errors should be happening here
			print 'bot action error: ', e
			reply = {
				'error': 1,
				'err_msg': "no action received. bot error"
			}
			self.write(json.dumps(reply))
			self.finish()
			return

		print 'action: ', action.body

		self.write(json.dumps(action.body))
		self.finish()
