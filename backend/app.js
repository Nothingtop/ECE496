/**
 * Module dependencies.
 */
var express  = require('express');
var connect = require('connect');
var app      = express();
var port     = process.env.PORT || 44000;

var path = require('path');

// view engine w/ jade
app.set('views', path.join('.', '/views'));
app.set('view engine', 'jade');

//configure shit
app.use(express.static('./public'));
app.use(express.static('./original'));
app.use(express.static('./input'));
app.use(express.static('./output'));
app.use(connect.cookieParser());
app.use(connect.logger('dev'));
app.use(connect.bodyParser());

app.use(connect.json());
app.use(connect.urlencoded());

// Routes

require('./routes/routes.js')(app);
require('./routes/home.js')(app);

app.listen(port, "0.0.0.0");
console.log('The App runs on port ' + port);

/// error handlers
/// catch 404 and forwarding to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});