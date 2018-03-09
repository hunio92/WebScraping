# from urllib import urlopen
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import sqlite3, time

def isNotInDatabase(title, area, rooms, price, currentRecentData):
    "Check if the current announcement exists in database"
    if ( (currentRecentData) and (title == currentRecentData[0]) and (area == currentRecentData[1]) and (int(rooms) == int(currentRecentData[2])) and (int(price) == int(currentRecentData[3])) ):
        return False
    else:
        return True

def parseContainerAndInsert(containers, isTheMostRecent, currentRecentData):
    "Parse the container, get the content and insert in database"
    # Set the new data to the current in case that nothing changed
    newRecentData = currentRecentData[:]
    # Parse the container
    for container in containers:
        # Get link to announcement
        if "http" in container.a["href"]:
            link = container.a["href"]
        else:
            link = "https://nemutam.com" + container.a["href"]
        # Get link to the image
        if "http" in container.img["src"]:
            img_link = container.img["src"]
        else:
            img_link = "https://nemutam.com/static/img/fara-poze.png"
        # Get the price of the announcement
        priceValue = container.find("span", {"class":"post-price"}).text.split()[0]
        if ( (priceValue) and (priceValue != "?") ) :
            price = int(container.find("span", {"class":"post-price"}).text.split()[0].replace(".",""))
        else:
            price = 0
        # Get the title
        title = container.find("div", {"class":"caption"}).p["title"]
        # Get content of the table where are stored next details
        rows = container.div.table.findAll("td")
        # Get the area
        area = rows[1].text
        # Get number of rooms
        if (rows[3].text):
            rooms = rows[3].text
        else:
            rooms = 0
        # Get the surface
        surface = rows[5].text
        # Get who published the announcement
        publishedBy = rows[7].text
        # Get which agency posted the announcement
        agency = rows[9].img["title"]
        # Set the time when was inserted in the database
        inserted_in = time.time()
        # Check if is in the database if not then insert else quit and stop
        if ( isNotInDatabase(title, area, rooms, price, currentRecentData) ):
            # Insert into the database
            cursor.execute('INSERT INTO announcements (link, img_link, price, title, area, rooms, surface, publishedBy, agency, inserted_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (link, img_link, price, title, area, rooms, surface, publishedBy, agency, inserted_in))
            database.commit()
            # Check if the data is the most recent
            if( isTheMostRecent and currentRecentData ):
                newRecentData.clear()
                newRecentData.append(title)
                newRecentData.append(area)
                newRecentData.append(rooms)
                newRecentData.append(price)
                isTheMostRecent = False
        else:
            return True, isTheMostRecent, newRecentData
    return False, isTheMostRecent, newRecentData

def verifyRecentData(currentRecentData):
    "At the first call recent data is empty at the second call need to get from the database and after that just replace with the new data"
    if(currentRecentData):
        # Put the recent data
        currentRecentData = newRecentData[:]
    else:
        # Get the recent data when called second time when currentRecentData is empty
        cursor.execute('SELECT title, area, rooms, price FROM announcements WHERE inserted_in = (SELECT min(inserted_in) FROM announcements LIMIT 1)')
        currentRecentData = cursor.fetchone()
        if (currentRecentData):
            # Convert tuple to list
            currentRecentData = list(currentRecentData)


# Access the database or create a new one
database = sqlite3.connect('database.db')
cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS announcements(id	INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, img_link TEXT, price INTEGER, title TEXT, area TEXT, rooms INTEGER, surface TEXT, publishedBy TEXT, agency TEXT, inserted_in REAL)')
# Keep the most recent data
currentRecentData = []
while(True):
    # Flag to know when to stop: 1. Is at the and of pages 2. Found the recent data and need to reset at every "refresh"
    stopParsePage = False
    # Flag for keep the most recent data
    isTheMostRecent = True
    # Only for debug
    pageIndex = 1
    while( not stopParsePage ):
        # Get the URL content
        urlToScrap = 'https://nemutam.com/?pag=' + str(pageIndex)
        uClient = urlopen(urlToScrap)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        # Check if is last page
        if (not page_soup.find("p", {"class":"text-center"})):
            # Get content of announcements
            containers = page_soup.findAll("div", {"class":"thumbnail"})
            # Parse announcements
            stopParsePage, isTheMostRecent, newRecentData  = parseContainerAndInsert(containers, isTheMostRecent, currentRecentData)
        else:
            stopParsePage = True

        print(pageIndex) # for_DEBUG
        pageIndex += 1
        # Wait for 10 sec to not to flood the site
        time.sleep(10)

    # Check if current data changed or it was the second call because at first is empty
    currentRecentData = verifyRecentData(currentRecentData)

    # Wait 4:47 min till the next update
    time.sleep(287)

# Close cursor and database
cursor.close()
database.close()
