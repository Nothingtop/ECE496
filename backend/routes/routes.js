var fs = require('fs');
var _ = require('underscore');
const shell  = require('child_process');
const readline = require('readline');


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
        var file = getMostRecentFileName(filedir);
        var img = fs.readFileSync(filedir + file);
        res.writeHead(200, {'Content-Type': 'image/png' });
        res.end(img, 'binary');
    });

    app.get('/getSsim', function (req, res){
        var file = './scores/' + req.param('filename') + '.txt';

        var json = JSON.stringify(readFromFile(file));
        res.writeHead(200, {'Content-Type': 'application/json' });
        res.end(json);
    });

    app.get('/getUpdateCount', function (req, res){
        res.writeHead(200, {'Content-Type': 'appliation/json' });
        res.end(JSON.stringify({ count: fs.readdirSync('./scores/').length }));
    });

    function readFromFile(file) {
        var results = [];
        const rl = readline.createInterface({
            input: fs.createReadStream(file),
            crlfDelay: Infinity
        });
        rl.on('line', (line) => {
            results.push(line)
        });
        return results;
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
            '-q 10 ' +
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

};