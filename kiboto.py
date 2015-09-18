# web server
import tornado.ioloop
from tornado.httpserver import HTTPServer
import tornado.web
from tornado.netutil import bind_sockets
from tornado.process import fork_processes

# cache
import redis

# helpers
import json

# kiboto specific imports
from lib.handlers.GameSessionInitializer import GameSessionInitializer
from lib.handlers.BotSubscriptionHandler import BotSubscriptionHandler
from lib.handlers.SessionBroadcastHandler import SessionBroadcastHandler
from lib.handlers.EventHandler import EventHandler
from lib.support_systems import session_state

def splash_screen():
	print "KIBOTO ONLINE"
	print " _____"
	print "|  _  |"
	print "| |_| |"
	print "| ___ |"
	print "| ___ |"
	print "| ___ |"
	print "|_____|"
	print

if __name__ == "__main__":
	# load config files
	with open('conf/server.config') as f:
		config = json.loads(f.read())

	# keep a global copy of session cache for speed
	local_sessions = session_state.SessionHandler()

	# have non-async bot registration so bots can't un-register eachother
	# see BotSubscriptionHandler implementation for more details
	sync_redis = redis.StrictRedis() # only local for now

	# multiple request handlers, sharing the same state
	tornado_app_config = tornado.web.Application([
			(r"/session", GameSessionInitializer, dict(local_sessions=local_sessions, domain=config['domain'])),
			(r"/subscribe", BotSubscriptionHandler, dict(sync_redis=sync_redis, domain=config['domain'])),
			(r"/get_sessions", SessionBroadcastHandler, dict(domain=config['domain'])),
			(r"/event", EventHandler, dict(local_sessions=local_sessions, domain=config['domain']))
		])

	# listen on the configured port, default to 8888 if not specified
	sockets = bind_sockets(config.get('port', 8888))

	# :)
	splash_screen()

	# multi-process tornado. auto forks for every core you have
	fork_processes(None)

	# set the server's application handler
	server = HTTPServer(tornado_app_config)
	server.add_sockets(sockets)

	# create the io loop
	main_loop = tornado.ioloop.IOLoop.instance()

	# periodically sync local sessions to mongo
	session_updater_loop = tornado.ioloop.PeriodicCallback(local_sessions.update_from_redis, local_sessions.update_period_ms, main_loop)

	main_loop.start()


