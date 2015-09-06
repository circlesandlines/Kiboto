/*

	This is the Kiboto game client SDK.
	===================================

	Either use it with the supplied bot message queue, or
	use your own and supply the callbacks

	> USAGE:

		workflow 1 - supplying callbacks:
		---------------------------------

		...
		game = new KibotoGame(hostname, port, 123, 000, "bob");
		game.init_session();

		...

		game.event({...}, function (httpcode, text, statustext, timeoutMS) {
				// do stuff here
			},

			function (errorcode, errormessage) {
				// do stuff here
			});

		// here, gameLogic is assumed to exist
		if botMessages.messagesToProcess()
			gameLogic.process(botMessages.get());


		workflow 2 - using the global message queue
		-------------------------------------------

		...
		botMessages = new KibotoBotMessages();
		game = new KibotoGame(hostname, port, 123, 000, "bob");
		game.init_session();

		...
		game.event({...});

		if botMessages.messagesToProcess()
			gameLogic.process(botMessages.get());

		botMessages.clear();
		...

		// repeat


*/

function KibotoBotMessages() {
	// store responses in global state because
	// callback can't access anything in KibotoGame
	// object
	// NOTE: this should be a singleton but can't really enforce it!

	window.kibotoResponses = [];
	window.messagesToProcess = false;

	this.get = function() {
		return window.kibotoResponses;
	};

	this.clear = function() {
		window.kibotoResponses = [];
		window.messagesToProcess = false;
	};
}

function KibotoGame(hostname, port, game_id, session_id, player_id) {
	this.hostname = hostname;
	this.port = port;
	this.game_id = game_id;
	this.session_id = session_id;
	this.player_id = player_id;

	// a session should already exist, so might as well use it
	this.session_key = game_id + ':' + session_id + ':' + player_id;
	this.responses = [];

	this.session_error = false;

	this.init_session = function() {
		// initializes the session
		url = this.host + ':' + this.port + '/session?' + \
				'game_id=' + game_id + '&' + \
				'session_id=' + session_id + '&' + \
				'player_id=' + player_id;

		var xhr = new XMLHttpRequest();
		xhr.open("GET", "/event", true);
		xhr.onload = function (err) {
			if (xhr.readyState == 4) {
				if (xhr.status != 200) {
					console.log ("error: couldn't start session:");
					console.log ("status: " + xhr.status.toString());
					onsole.log ("message: " + xhr.statusText);
					this.session_error = true;
				} else {
					this.session_error = false;
				}
			}
		}
	};

	this.event = function(data, callback, errorCallback, timeout) {
		// send an event to kiboto server with
		// what ever data the game developer wants.
		// should represent state changes for the current player
		// as well as other players and the environment.
		// the callback should be a function that the game
		// specifies. they can do whatever they want in there
		// if no callback is set, the message will be added to the
		// kiboto message queue for later processing.

		var xhr = new XMLHttpRequest();
		xhr.open("POST", "/event", true);

		// handle success
		if (callback == null) {
			xhr.onload = function (err) {
				if (xhr.readyState == 4) {
					if (xhr.status == 200) {
						window.kibotoResponses.push(xhr.responseText);
						window.messagesToProcess = true;
					} else {
						// we still want to process the errors
						window.kibotoResponses.push(xhr.statusText);
						window.messagesToProcess = true;
					}
				}
			};
		} else {
			// wrap the function to notify the bot message
			// object that there are messages to process
			xhr.onload = function (err) {
				// assume they handle their own message state and
				// message queue. only pass them what they need
				if (xhr.readyState == 4) {
					callback(xhr.status, xhr.responseText, xhr.statusText);
				}
			};
		}

		// handle errors
		if (errorCallback == null) {
			xhr.onerror = function (err) {
				// should we store text or HTTP codes? or our own mapping?
				window.kibotoResponses.push(xhr.statusText);
				window.messagesToProcess = true;
			};
		} else {
			xhr.onerror = function (err) {
				errorCallback(xhr.status, xhr.statusText);
			};
		}

		// handle timeouts?

		xhr.timeout = timeoutMS;
		xhr.send();
 	};
}

