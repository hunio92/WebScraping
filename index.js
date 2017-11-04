const express = require('express'); // install express
const bodyParser = require('body-parser'); // install body parser: npm install body-parser
const swig = require('swig'); // install swig: 
swig.setDefaults({ cache: false });
const sqlite = require('slite3');

const db = new sqlite.Database('./databaseName.db', (err)=> console.log(err));

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));

app.set('view enginew', 'html');
app.engine('html', swig. renderFile); 

app.get('/', (req, res, next)=> res.render('index'));

app.post('/', (req, res, next)=> {
	const sql = req.body.sql;
	db.all(sql, (err, results)=> {
		res.render('index', { sql, results: results, error: err});
	});
});

const port = process.env.PORT || 3000;

app.listen(port, ()=> console.log('listening on port ${port}'));