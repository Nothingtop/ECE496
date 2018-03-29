var fs = require('fs');
const shell  = require('child_process');


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


    app.get('/uploads/:file', function (req, res){
        file = req.params.file;
        var dirname = "./original";
        var img = fs.readFileSync(dirname + "/uploads/" + file);
        res.writeHead(200, {'Content-Type': 'image/jpg' });
        res.end(img, 'binary');

    });

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
                    'python ./python_scripts/sitch_images.py ' +
                    '--original ./original/' + filename + '.jpg ' +
                    '--input ./input/' + filename + '.png ' +
                    '--output ./output/' + filename + '.png ' +
                    '--comparison_folder ./public/comparison/ ', function(code, stdout, stderr) {
                    if (stderr!=null)
                        console.log(stderr);
                });
            });
        });

    }

};