"""

	Copyright 2015 KibotoLabs

	Game Session Initializer

	This handles requests from games for starting an AI session.
	A session is initialized per game client connected to the game.

	eg:

	game server -> game client 1 -> kiboto server -> bot1
	           \-> game client 2 /               \-> bot2

	A game can have multiple sessions if supported:
		session:
			player1
			player2
			...
		session2:
			player1
			player2
			...

	all connecting to the same Kiboto server

	Once a game initializes a session, it waits for bots to connect
	asynchronously

"""


import tornado.gen
import tornado.web
import tornadis
from tornado.web import MissingArgumentError
from tornadis import ClientError
from tornadis import ConnectionError

import json

class SessionStoreException(Exception): pass

class GameSessionInitializer(tornado.web.RequestHandler):
	"""
		The game client sends a request to this handler, telling it
		to initialize a session that others can see.

		We store it locally, and back it up on redis.

		The interested bots can then look for this session by
		querying '/get_sessions'.

		The bot can then be configured to join the session.

	"""
	def initialize(self, local_sessions, domain):
		self.local_sessions = local_sessions
		self.domain = domain

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")

	def check_origin(self, origin):
		if 'localhost' in origin or self.domain in origin:
			return True

		return False

	@tornado.gen.coroutine
	def get(self):
		""" start a session given the game client's info:
			game id - unique game identifier
			session id - game session identifier
			player id - unique identifier of the game client. ie. the player

			format of request:
			<host>:<port>/session?game_id=<game id>&session_id=<session id>&player_id=<player id>
		"""

		# extract params
		try:
			game_id = self.get_argument('game_id')
			session_id = self.get_argument('session_id')
			player_id = self.get_argument('player_id')
		except MissingArgumentError as e:
			reply = {
				'error': 1,
				'err_msg': "missing parameter: " + str(e)
			}
			self.write(json.dumps(reply))
			self.finish()
			raise e

		# gen session key
		session_key = "session:{}:{}:{}".format(game_id, session_id, player_id)

		# update session_store (and expire after 5 hours)
		# set the value as empty. it will be set to the bot hostname when it decides to connect
		session_store = tornadis.Client()
		# TODO handle connection error
		cstatus = yield session_store.connect()
		if not cstatus:
			reply = {
				'error': 1,
				'err_msg': "server session store connection error"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise SessionStoreException('session store connection error')

		# TODO handle None return error
		try:
			cstatus = yield session_store.call('HSET', 'sessions', session_key, "empty")

			if cstatus == ConnectionError:
				raise cstatus
		except ClientError as e:
			reply = {
				'error': 1,
				'err_msg': "server session store update error"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise e

		except ConnectionError as e:
			reply = {
				'error': 1,
				'err_msg': "server session store update error"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise e

		if cstatus == None:
			reply = {
				'error': 1,
				'err_msg': "session does not exist"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise SessionStoreException('session does not exist: ' + session_key)

		print "session stored: ", session_key
		print "redis status: ", cstatus

		# wait for the session to have a subscriber
		# once a bot subscribes, the value of the key will be the hostname
		for retries in xrange(0, 100):
			# wait 5 seconds and retry
			yield tornado.gen.sleep(5)
			hostname = yield session_store.call('HGET', 'sessions', session_key)

			if hostname != "empty" and hostname != None:
				print "bot matched! ", hostname
				break
			print "retry ", session_key

		# if the host name is still not set after 100 retries
		if hostname == "empty":
			# send an HTTP timeout error
			self.send_error(504)
			print "failed to find any bots"
			return

		# update local store
		self.local_sessions.sessions[session_key] = hostname

		# update session_store with the hostname that is subscribed to the game client

		# TODO handle None return
		# how to handle timeout?
		try:
			stored_hostname = yield session_store.call('HGET', 'sessions', session_key)
		except ClientError as e:
			reply = {
				'error': 1,
				'err_msg': "server session store update error"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise e

		if stored_hostname == ConnectionError:
			reply = {
				'error': 1,
				'err_msg': "server session store update error"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise SessionStoreException('session store update error')
		elif stored_hostname == None:
			reply = {
				'error': 1,
				'err_msg': "session does not exist"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise SessionStoreException('session does not exist: ' + session_key)

		print 'stored hostname: ', stored_hostname

		if stored_hostname != hostname:
			print "stored hostname does not equal cached hostname. stored: {0}, cached: {1}".format(stored_hostname, hostname)
			reply = {
				'error': 1,
				'err_msg': "server error: session cache doesn't match session store"
			}
			self.write(json.dumps(reply))
			self.finish()
			raise SessionStoreException("stored hostname doesn't match cached hostname")

		# the game can now start!
		self.finish()
