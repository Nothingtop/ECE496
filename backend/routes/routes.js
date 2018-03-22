var fs = require('fs');
const shell  = require('child_process');

module.exports = function(app) {


    app.get('/',function(req,res){
        processImage('/home/k/ECE496/waifu2x-chainerx/images/small.png', "small.png");
        res.end("Node-File-Upload");
    });

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
        var dirname = "/home/rajamalw/Node/file-upload";
        var img = fs.readFileSync(dirname + "/uploads/" + file);
        res.writeHead(200, {'Content-Type': 'image/png' });
        res.end(img, 'binary');

    });

    function processImage(filename) {
        shell.exec('' +
            'python ./python_scripts/reduce_image.py ' +
            '-q 10 ' +
            '-i '+ './original/' + filename + '.jpg ' +
            '-o ./input/ ', function(code, stdout, stderr) {
            shell.exec('' +
                'python /home/k/ECE496/waifu2x-chainerx/waifu2x.py ' +
                '--method noise ' +
                '--noise_level 0 ' +
                '--input ./input/' + filename + '.png ' +
                '--arch VGG7 ' +
                '--output ./output ' +
                '--model_dir /home/k/ECE496/waifu2x-chainerx/models ' +
                '--model_name portraits_300x300_epoch640k.npz ' +
                '--block_size 32', function(code, stdout, stderr) {
                console.log('Program output:', stdout);
                if (stderr != null)
                    console.log('Program stderr:', stderr);
            });
        });

    }

};