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

function getValueOrZero(value) { return value ? value : 0 }
function addStrWhereOrAnd(querry) { return querry.indexOf("WHERE") === -1 ? querry += " WHERE " : querry += " AND " }

app.post('/', (req, res, next)=> {
  querry = ""
  const minPrice = req.body.minPrice
  const maxPrice = req.body.maxPrice
  const area = req.body.area
  const rooms = req.body.rooms
  const minSurface = req.body.minSurface
  const maxSurface = req.body.maxSurface
  const orderBy = req.body.sortBy
  if (minPrice || maxPrice || area || rooms || minSurface || maxSurface || orderBy)
  {
    querry = 'SELECT * FROM announcements';
  }
  if (minPrice || maxPrice)
  {
    querry = addStrWhereOrAnd(querry)
    querry += "price BETWEEN " + getValueOrZero(minPrice) + " AND " + getValueOrZero(maxPrice)
  }
  if (area)
  {
    querry = addStrWhereOrAnd(querry)
    querry += "area = '" + area + "'"
  }
  if (rooms) 
  {
    querry = addStrWhereOrAnd(querry)
    querry += "rooms = '" + rooms + "'"
  }
  if (minSurface || maxSurface)
  {
    querry = addStrWhereOrAnd(querry)
    querry += "surface BETWEEN " + getValueOrZero(minSurface) + " AND " + getValueOrZero(maxSurface)
  }
  switch (parseInt(orderBy)) {
    case 1:
      querry += " ORDER BY price ASC"
      break;
    case 2:
      querry += " ORDER BY price DESC"
    default:
  }

  output = mnPrice + " " + maxPrice + " " + area + " " + rooms + " " + minSurface + " " + maxSurface + " " + orderBy
	db.all(querry, (err, results)=> {
		    res.render('index', { results: results, error: querry});
	});
});

const port = process.env.PORT || 3000;

app.listen(port, ()=> console.log(`listening on port ${port}`));
