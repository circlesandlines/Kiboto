"""
	The bots can use this to look for active sessions
"""

import tornado.web
import tornado.gen
import tornadis
import json

class SessionBroadcastHandler(tornado.web.RequestHandler):
	@tornado.gen.coroutine
	def get(self):
		# fairly straight forward :P
		session_store = tornadis.Client()
		yield session_store.connect()
		# the following returns a list... [k,v,k,v]
		# i'm tempted to just use the regular python redis client...
		# or switch to node >:(
		# NOTE handle empty sessions on the bot client
		sessions = yield session_store.call('HGETALL', 'sessions')

		sessions_dict = self.translator(sessions)

		print 'all_sessions: ', json.dumps(sessions_dict, indent=4)

		self.write(sessions_dict)
		self.finish()

	def translator(self, hgetall_list):
		"""For some reason the redis client decides to
		return a dictionary as a list... translate it back"""

		actual_dict = {}
		for i, korv in enumerate(hgetall_list):
			if i % 2 == 0:
				# odd = key
				actual_dict[korv] = hgetall_list[i+1]

		return actual_dict
