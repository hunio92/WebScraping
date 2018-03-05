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
				// rooms: req.rooms
    });
}

app.get('/', findFirstElements, findAreaNames, findRoomNumbers, renderResults);

function Item(name, minValue, maxValue)
{
  this.name = name;
  this.minValue = minValue;
  this.maxValue = maxValue;
}

function getValueOrZero(value) { return value ? value : 0 }

function addStrWhereOrAnd(querry) { return querry.indexOf("WHERE") === -1 ? querry += " WHERE " : querry += " AND " }

function addToQuerry(item, querry)
{
  if (isNaN(item.minValue))
  {
    querry = addStrWhereOrAnd(querry)
    querry += item.name + " = '" + item.minValue + "'"
  }
  else
  {
    if (item.maxValue > item.minValue)
    {
      querry = addStrWhereOrAnd(querry)
      querry += item.name + " BETWEEN " + getValueOrZero(item.minValue) + " AND " + item.maxValue
    }
    if (item.minValue)
    {
      querry = addStrWhereOrAnd(querry)
      querry += item.name + " >= " + item.minValue
    }
  }
  return querry
}

app.post('/', (req, res, next)=> {
  querry = 'SELECT * FROM announcements';

  price = new Item("price", req.body.minPrice, req.body.maxPrice)
  area = new Item("area", req.body.area, 0)
  rooms = new Item("rooms", req.body.minRooms, req.body.maxRooms)
  surface = new Item("surface", req.body.minSurface, req.body.maxSurface)
  const orderBy = req.body.sortBy

  querry = addToQuerry(price, querry)
  querry = addToQuerry(area, querry)
  querry = addToQuerry(rooms, querry)
  querry = addToQuerry(surface, querry)

  switch (parseInt(orderBy)) {
    case 1:
      querry += " ORDER BY price ASC"
      break;
    case 2:
      querry += " ORDER BY price DESC"
    default:
  }

  output = ""
	db.all(querry, (err, results)=> {
		    res.render('index', { results: results, error: querry});
	});
});

const port = process.env.PORT || 3000;

app.listen(port, ()=> console.log(`listening on port ${port}`));
