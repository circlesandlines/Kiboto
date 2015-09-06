function kibotoMessages() {
	// store responses in global state because
	// callback can't access anything in KibotoGame
	// object
	// NOTE: this should be a singleton

	window.kibotoResponses = [];

	this.getResponses = function() {
		window.kibotoResponses.pop();
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

	this.gameEvent = function(data, callback) {
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
		if (callback == null) {
			xhr.onload = function (err) {
				if (xhr.readyState === 4) {
					if (xhr.status === 200) {
						window.kibotoResponses.push(xhr.responseText);
					} else {
						// not really sure how to handle errors here...
					}
				}
			};
		} else {
			xhr.onload = callback;
		}
 	};
}

