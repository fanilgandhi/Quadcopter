var app = require('express')();
var http = require('http').Server(app);
var path = require('path');
var io = require('socket.io')(http);

app.get('/', function(req, res){
  res.sendFile(path.join(__dirname , 'index.html'));
});

app.get('/socket.io.js', function(req, res){
  res.sendFile(path.join(__dirname , 'socket.io.js'));
});

io.on('connection', function(socket){
  console.log('a user connected from ' + socket.request.connection.remoteAddress);

  socket.emit("user connected");

  socket.on('message', function(msg){
    	io.emit('message' , JSON.stringify(msg));
	console.log('message: ' + JSON.stringify(msg) ) ;
  });
  
  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

http.listen(80, function(){
  console.log('listening on *:80');
});
