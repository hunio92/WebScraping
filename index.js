const express = require('express');
const bodyParser = require('body-parser');
const swig = require('swig');
swig.setDefaults({ cache: false });
const sqlite = require('sqlite3');

const db = new sqlite.Database('./database.db', (err)=> console.log(err));

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));

app.set('view engine', 'html');
app.engine('html', swig.renderFile);

app.use(express.static('public'))

app.get('/', (req, res, next)=> res.render('index'));

app.post('/', (req, res, next)=> {
	const sql = req.body.sql;
	db.all(sql, (err, results)=> {
		res.render('index', { sql, results: results, error: err});
	});
});

const port = process.env.PORT || 3000;

app.listen(port, ()=> console.log(`listening on port ${port}`));
