import tornado.gen
import tornado.web
import tornadis

class GameSessionInitializer(tornado.web.RequestHandler):
	"""
		The game client sends a request to this handler, telling it
		to initialize a session that others can see.

		We store it locally, and back it up on redis.

		The interested bots can then look for this session by
		querying '/get_sessions'.

		The bot can then be configured to join the session.

	"""
	def initialize(self, local_sessions):
		self.local_sessions = local_sessions

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
		# NOTE that if either of the parameters below are missing,
		# tornado will throw an exception on game client side.
		# check if its meaningful. if not, wrap it in a try catch
		# TODO: cleanly handle missing arguments
		game_id = self.request.get_argument('game_id')
		session_id = self.request.get_argument('session_id')
		player_id = self.request.get_argument('player_id')

		# gen session key
		session_key = "session:{}:{}:{}".format(game_id, session_id, player_id)

		# update session_store (and expire after 5 hours)
		# set the value as empty. it will be set to the bot hostname when it decides to connect
		# TODO cleanly handle timeout
		session_store = tornadis.Client(client_timeout=1)
		yield session_store.connect()
		yield session_store.call('SET', session_key, "", 5*60*60*60)

		# wait for the session to have a subscriber
		# once a bot subscribes, the value of the key will be the hostname
		for retries in xrange(0, 100):
			# wait and retry
			yield tornado.gen.sleep(5)
			hostname = yield session_store.call('GET', session_key)

			if hostname != "":
				break

		# if the host name is still not set after 100 retries
		if hostname == "":
			# send an HTTP timeout error
			self.send_error(504)
			return

		# update local store
		# TODO. also make a periodic function that updates this.
		# if a node in the cluster hasn't synced with the session store,
		# send errors on ping so that proxies can't detect it
		# the key written here might be overwritten later in the sync
		# that's ok, its async :) no collisions!
		# the above strategy will minimize cache misses and eventual
		# consistency anomalies
		self.local_sessions.sessions[session_key] = hostname

		# update session_store with the hostname that is subscribed to the game client
		# TODO cleanly handle timeout
		yield session_store.call('SET', session_key, "hostname", 5*60*60*60)

		# the game can now start!
		self.finish()
