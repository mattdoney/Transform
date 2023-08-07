const express = require('express');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
const fs = require('fs');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const app = express();

app.use(express.static('public'));

app.post('/upload', upload.single('file'), (req, res) => {
    let data = [];
    fs.createReadStream(req.file.path)
        .pipe(csv())
        .on('data', (row) => {
            // Perform your transformation here
            // row = transform(row);
            data.push(row);
        })
        .on('end', () => {
            const csvWriter = createCsvWriter({
                path: 'out.csv',
                header: Object.keys(data[0]).map(id => ({id, title: id})),
            });

            csvWriter
                .writeRecords(data)
                .then(() => res.download('out.csv'));
        });
});

app.listen(3000, () => {
    console.log('App is listening on port 3000');
});
