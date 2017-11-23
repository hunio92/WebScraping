from urllib import urlopen
from bs4 import BeautifulSoup as soup
import sqlite3, time

database = sqlite3.connect('database.db')

cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS announcements(id	INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, img_link TEXT, price INTEGER, title TEXT, area TEXT, rooms INTEGER, surface TEXT, publishedBy TEXT, agency TEXT)')

for i in range(1,1411):
    urlToScrap = 'https://nemutam.com/?pag=' + str(i);

    uClient = urlopen(urlToScrap)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, "html.parser")

    containers = page_soup.findAll("div", {"class":"thumbnail"})

    for container in containers:
        if "http" in container.a["href"]:
            link = container.a["href"]
        else:
            link = "https://nemutam.com" + container.a["href"]
        img_link = "https://nemutam.com" + container.img["src"]
        if (container.find("span", {"class":"post-price"}).text.split()[0]) != "?":
            price = long(container.find("span", {"class":"post-price"}).text.split()[0].replace(".",""))
        else:
            price = 0
        title = container.find("div", {"class":"caption"}).p["title"]
        rows = container.div.table.findAll("td")
        area = rows[1].text
        rooms = rows[3].text
        surface = rows[5].text
        publishedBy = rows[7].text
        agency = rows[9].img["title"]
        cursor.execute('INSERT INTO announcements (link, img_link, price, title, area, rooms, surface, publishedBy, agency) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (link, img_link, price, title, area, rooms, surface, publishedBy, agency))
        database.commit()

    time.sleep(10)
    print(i)
# print(containers[0])
# print(link)
# print("https://nemutam.com" + img_link)
# print(price.split()[0])
# print(title)
# print(area)
# print(rooms)
# print(surface)
# print(publishedBy)
# print(agency)

cursor.close()
database.close()
