/ GET home page. /
module.exports = function(app) {
    app.get('/', function(req, res) {
        res.render('home', { title: '6719068a'});
    });
}