# from urllib import urlopen
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import sqlite3, time

# def timestampToDateTime(currentTimestamp, secondsToSubstract):
#     result = currentTimestamp - secondsToSubstract
#     return str(time.localtime(result).tm_year) + "/" + str(time.localtime(result).tm_mon) + "/"+ str(time.localtime(result).tm_mday)
#
# def calculateDate(timeElapsed):
#     currentDateTime = time.time()
#     searchTo = ['minut', 'minute', 'ore', 'ora', 'zi', 'zile', 'nemutam']
#     if any(ch in timeElapsed for ch in searchTo):
#         return timestampToDateTime(currentDateTime, 0)
#     elif (("săptămână" in timeElapsed) or ("săptămâni" in timeElapsed)):
#         return timestampToDateTime(currentDateTime, 604800)
#     elif (("lună" in timeElapsed) or ("luni" in timeElapsed)):
#         return timestampToDateTime(currentDateTime, 2.592e+6)
#     elif (("an" in timeElapsed) or ("ani" in timeElapsed)):
#         return timestampToDateTime(currentDateTime, 3.154e+7)

# # start for_DEBUG
# if(mostRecentRow):
#     print("1 " + str(len(tmpMostRecentRow)) + " " + str(isTheMostRecent) + " " + str(mostRecentRow[2]) + " " + str(mostRecentRow[3]) + " <=> " + str(tmpMostRecentRow[2]) + " " + str(tmpMostRecentRow[3]))
# # end for_DEBUG

def isNotInDatabase(title, area, rooms, price, mostRecentRow):
    if ( (mostRecentRow) and (title == mostRecentRow[0]) and (area == mostRecentRow[1]) and (int(rooms) == int(mostRecentRow[2])) and (int(price) == int(mostRecentRow[3])) ):
        return False
    else:
        return True

def parseContainerAndInsert(containers, isTheMostRecent, mostRecentRow):
    tmpMostRecentRow = mostRecentRow[:]
    for container in containers:
        if "http" in container.a["href"]:
            link = container.a["href"]
        else:
            link = "https://nemutam.com" + container.a["href"]
        if "http" in container.img["src"]:
            img_link = container.img["src"]
        else:
            img_link = "https://nemutam.com/static/img/fara-poze.png"
        priceValue = container.find("span", {"class":"post-price"}).text.split()[0]
        if ( (priceValue != "?") and (priceValue != "") ) :
            price = int(container.find("span", {"class":"post-price"}).text.split()[0].replace(".",""))
        else:
            price = 0
        title = container.find("div", {"class":"caption"}).p["title"]
        rows = container.div.table.findAll("td")
        area = rows[1].text
        if (rows[3].text != "")
            rooms = rows[3].text
        surface = rows[5].text
        publishedBy = rows[7].text
        agency = rows[9].img["title"]
        timeElapsed = rows[9].text
        # posted_on = calculateDate(timeElapsed)
        inserted_in = time.time()
        if ( isNotInDatabase(title, area, rooms, price, mostRecentRow) ):

            cursor.execute('INSERT INTO announcements (link, img_link, price, title, area, rooms, surface, publishedBy, agency, inserted_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (link, img_link, price, title, area, rooms, surface, publishedBy, agency, inserted_in))
            database.commit()
            if( isTheMostRecent and mostRecentRow ):
                tmpMostRecentRow.clear()
                tmpMostRecentRow.append(title)
                tmpMostRecentRow.append(area)
                tmpMostRecentRow.append(rooms)
                tmpMostRecentRow.append(price)
                isTheMostRecent = False
        else:
            return True, isTheMostRecent, tmpMostRecentRow
    return False, isTheMostRecent, tmpMostRecentRow

# Access the database or create a new one
database = sqlite3.connect('database.db')
cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS announcements(id	INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, img_link TEXT, price INTEGER, title TEXT, area TEXT, rooms INTEGER, surface TEXT, publishedBy TEXT, agency TEXT, inserted_in REAL)')
# Keep the most recent data
mostRecentRow = []
while(True):
    # Flag to know when to stop: 1. Is at the and of pages 2. Found the recent data and need to reset at every "refresh"
    stopParsePage = False
    # 
    isTheMostRecent = True
    pageIndex = 1856
    while( (not stopParsePage) and (pageIndex < 1857) ):
        urlToScrap = 'https://nemutam.com/?pag=' + str(pageIndex)
        uClient = urlopen(urlToScrap)
        page_html = uClient.read()
        uClient.close()

        page_soup = soup(page_html, "html.parser")

        if (not page_soup.find("p", {"class":"text-center"})):
            containers = page_soup.findAll("div", {"class":"thumbnail"})
            stopParsePage, isTheMostRecent, tmpMostRecentRow  = parseContainerAndInsert(containers, isTheMostRecent, mostRecentRow)
        else:
            stopParsePage = True

        print(pageIndex) # for_DEBUG
        pageIndex += 1
        time.sleep(10)

    if(mostRecentRow):
        mostRecentRow = tmpMostRecentRow[:]
    else:
        cursor.execute('SELECT title, area, rooms, price FROM announcements WHERE inserted_in = (SELECT min(inserted_in) FROM announcements LIMIT 1)')
        mostRecentRow = cursor.fetchone()
        if (mostRecentRow):
            mostRecentRow = list(mostRecentRow)

    time.sleep(60)
    print("REFRESH")

cursor.close()
database.close()
