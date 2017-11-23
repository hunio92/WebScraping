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

app.use(express.static('public'));

function findFirstElements(req, res, next) {
    var querry = 'SELECT * FROM announcements LIMIT 12';
    db.all(querry, function(err, rows) {
        if(rows.length !== 0) {
            req.results = rows;
            return next();
        }
        res.render(err);
    });
}

function findAreaNames(req, res, next) {
    var querry = 'SELECT DISTINCT area FROM announcements WHERE area != ""';
    db.all(querry, function(err, rows) {
        if(rows.length !== 0) {
            req.areas = rows;
            return next();
        }
        res.render(err);
    });
}

function findRoomNumbers(req, res, next) {
    var querry = 'SELECT DISTINCT rooms FROM announcements WHERE rooms != "" ORDER BY rooms ASC';
    db.all(querry, function(err, rows) {
        if(rows.length !== 0) {
            req.rooms = rows;
            return next();
        }
        res.render(err);
    });
}

function renderResults(req, res) {
    res.render('index', {
        results: req.results,
        areas: req.areas,
				rooms: req.rooms
    });
}

app.get('/', findFirstElements, findAreaNames, findRoomNumbers, renderResults);

app.post('/', (req, res, next)=> {
	const minPrice = req.body.minPrice
	const maxPrice = req.body.maxPrice
  const area = req.body.area
	const querry = 'SELECT * FROM announcements WHERE price BETWEEN ' + minPrice + ' AND ' + maxPrice;
	db.all(querry, (err, results)=> {
		res.render('index', { results: results, error: area});
	});
});

const port = process.env.PORT || 3000;

app.listen(port, ()=> console.log(`listening on port ${port}`));
