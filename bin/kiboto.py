import tornado.ioloop
from tornado.httpserver import HTTPServer
import tornado.web
from tornado.netutil import bind_sockets
from tornado.process import fork_processes

# kiboto specific libraries
from lib.handlers import GameSessionInitializer
from lib.handlers import BotSubscriptionHandler
from lib.handlers import SessionBroadcastHandler
from lib.handlers import EventHandler

import session_state

if __name__ == "__main__":
	# load config files
	with open('conf/server.json') as f:
		config = json.loads(f.read())

	# keep a global copy of session cache for speed
	local_sessions = session_state.SessionHandler()

	# multiple request handlers, sharing the same state
	tornado_app_config = tornado.web.Application([
			(r"/session", GameSessionInitializer, dict(local_sessions=local_sessions)),
			(r"/subscribe", BotSubscriptionHandler),
			(r"/get_sessions", SessionBroadcastHandler, dict(local_sessions=local_sessions))
			(r"/event", EventHandler, dict(local_sessions=local_sessions))
		])

	# listen on the configured port, default to 8888 if not specified
	sockets = bind_sockets(config.get('port', 8888))

	# multi-process tornado. auto forks for every core you have
	fork_processes()

	# set the server's application handler
	server = HTTPServer(tornado_app_config)
	server.add_sockets(sockets)

	# create the io loop
	main_loop = tornado.ioloop.IOLoop.instance()

	# periodically sync local sessions to mongo
	session_updater_loop = tornado.web.PeriodicCallback(local_sessions.update_from_redis, local_sessions.update_period_ms, main_loop)

	main_loop.start()


