var app = require('express')();
var http = require('http').Server(app);
var path = require('path');
var io = require('socket.io')(http);
var fs = require("fs");

app.get('/', function(req, res){
	res.sendFile(path.join(__dirname , 'index.html'));
});

app.get('/socket.io.js', function(req, res){
	res.sendFile(path.join(__dirname , 'socket.io.js'));
});

app.get('/jquery-1.7.1.min.js', function(req, res){
	res.sendFile(path.join(__dirname , 'jquery-1.7.1.min.js'));
});

io.on('connection', function(socket){
	//console.log('a new user connected from ' + socket.request.connection.remoteAddress);

	socket.on('read_message', function(msg){
			//console.log(JSON.stringify(msg));
			io.emit('read_message' , JSON.stringify(msg));
	});
	
	socket.on('write_message', function(msg){
		console.log(msg);
		fs.appendFile('/home/pi/message.txt', JSON.stringify(msg) + "\n", (err) => {
			if (err) {
				console.log("Error occured in writing to file. \n The following command is not written");
				console.log(msg);
			}
		});
	});

	socket.on("log" , function(msg) {
		fs.appendFile('/home/pi/log.txt' , msg + "\n" , (err) => { 
			if (err) {console.log(msg); }
		}); 
	});	
	
	
	socket.on('disconnect', function(){
		//console.log('A user disconnected from ' + socket.request.connection.remoteAddress);
	});
});

http.listen(80, function(){
	console.log('listening on *:80');
});
