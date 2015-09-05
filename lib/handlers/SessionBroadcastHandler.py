"""
	The bots can use this to look for active sessions
"""

import tornado.web

class MyRequestHandler(tornado.web.RequestHandler):
	def initialize(self, local_sessions):
		self.local_sessions = local_sessions

	@tornado.web.asynchronous
	def get(self):
		# fairly straight forward :P
		self.write(self.local_sessions)
		self.finish()
