/*

	Usage:

		workflow 1 - supplying callbacks:

		...
		game = new KibotoGame(hostname, port, 123, 000, "bob");
		game.connect();

		...

		game.event({...}, function (err) {
				this.responseText;
				this.statusText;
			},

			function (err) {
				this.statusText;
			});

		workflow 2 - using the global message queue

		...
		botMessages = new KibotoBotMessages();
		game = new KibotoGame(hostname, port, 123, 000, "bob");
		game.connect();

		...

		game.event({...});

		// here, gameLogic is assumed to exist
		gameLogic.process(botMessages.get());

		botMessages.clear();

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

	this.session_key = game_id + ':' + session_id + ':' + player_id;
	this.responses = [];

	this.connect = function() {
		// initializes the session
	};

	this.event = function(data, callback, errorCallback) {
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
				if (xhr.readyState === 4) {
					if (xhr.status === 200) {
						window.kibotoResponses.push(xhr.responseText);
						window.messagesToProcess = true;
					} else {
						window.kibotoResponses.push(xhr.statusText);
					}
				}
			};
		} else {
			// wrap the function to notify the bot message
			// object that there are messages to process
			xhr.onload = function (err) {
				if (xhr.status == 200 ) {
					window.messagesToProcess = true;
					callback("");
				} else {
					callback(xhr.statusText);
				}
			}
		}

		// handle errors
		if (errorCallback == null) {
			xhr.onerror = function (err) {
				// should we store text or HTTP codes? or our own mapping?
				window.kibotoResponses.push(xhr.statusText);
			}
		} else {
			xhr.onerror = errorCallback;
		}

		xhr.send();
 	};
}

