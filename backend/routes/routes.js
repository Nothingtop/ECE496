var fs = require('fs');
var _ = require('underscore');
const shell  = require('child_process');
const cron = require('node-cron');

module.exports = function(app) {

    app.post('/upload', function(req, res) {
        console.log(req.files.image.originalFilename);
        console.log(req.files.image.path);
        fs.readFile(req.files.image.path, function (err, data){
            var newPath = "./original";
            if (!fs.existsSync(newPath)){
                fs.mkdirSync(newPath);
            }
            fs.writeFile(newPath + '/' + req.files.image.originalFilename, data, function (err) {
                if(err){
                    res.json({'response':"Error"});
                }else {
                    res.json({'response':"Saved"});
                }
            });
        });
        processImage(req.files.image.originalFilename.split('.')[0]);
    });

    app.get('/getFile', function (req, res){
        var filedir = './' + req.param('fileDir') + '/';
        var img;

        var index = req.param('index');
        if(typeof index == 'undefined')
            img = fs.readFileSync(filedir + getMostRecentFileName(filedir));
        else
            img = fs.readFileSync(filedir + getFilesSortedByDate(filedir).reverse()[index]);
        res.writeHead(200, {'Content-Type': 'image/png'});
        res.end(img, 'binary');
    });

    app.get('/getData', function (req, res){
        var json = JSON.stringify(readFromFiles('./scores/'));
        res.writeHead(200, {'Content-Type': 'application/json', "Access-Control-Allow-Origin" : "*"});
        res.end(json);
    });

    app.get('/getUpdateCount', function (req, res){
        res.writeHead(200, {'Content-Type': 'appliation/json', "Access-Control-Allow-Origin" : "*"});
        res.end(JSON.stringify({ count: fs.readdirSync('./scores/').length }));
        fs.watch('./scores/', { encoding: 'buffer' }, (eventType, filename) => {
            if (filename) {
            }
        });
    });

    function getFilesSortedByDate(dir) {
        return fs.readdirSync(dir, function(err, files){
            files = files.map(function (fileName) {
                return {
                    name: fileName,
                    time: fs.statSync(dir + '/' + fileName).mtime.getTime()
                };
            })
                .sort(function (a, b) {
                    return a.time - b.time; })
                .map(function (v) {
                    return v.name; });
        });
    }

    function getMostRecentFileName(dir) {
        var files = fs.readdirSync(dir);

        // use underscore for max()
        return _.max(files, function (f) {
            var fullpath = dir + f;
            return fs.statSync(fullpath).ctime;
        });
    }

    function processImage(filename) {
        shell.exec('' +
            'python ./python_scripts/reduce_image.py ' +
            '-q 5 ' +
            '-i '+ './original/' + filename + '.jpg ' +
            '-o ./input/ ', function(code, stdout, stderr) {
            shell.exec('python ./gan/test.py ' +
                '--model_path ./gan/gan.npz ' +
                '--input_path ./input/' + filename + '.png '  +
                '--output_folder ./output/ ' +
                '--filename ' + filename + '.png ' +
                '--use_gpu=0', function(code, stdout, stderr) {
                console.log('GAN Model output:', stdout);
                if (stderr!=null)
                    console.log(stderr);
                shell.exec('' +
                    'python ./python_scripts/scores.py ' +
                    '--original ./original/' + filename + '.png ' +
                    '--input ./input/' + filename + '.png ' +
                    '--output ./output/' + filename + '.png ' +
                    '--save_folder ./scores/ ', function(code, stdout, stderr) {
                    if (stderr!=null) {
                        console.log(stderr);
                    }
                    global.updateCount += 1;
                    console.log(global.updateCount);
                });
            });
        });
    }

    function readFromFiles(fileDir) {
        var results = [];
        var files = fs.readdirSync(fileDir);
        files.forEach( function(file, index ) {
            results.push(fs.readFileSync(fileDir + file).toString().split('\n'));
        });
        return results;
    }

    cron.schedule('10 * * * *', function(){
        console.log('sup');
    });

};