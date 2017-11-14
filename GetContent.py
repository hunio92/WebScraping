from urllib import urlopen
from bs4 import BeautifulSoup as soup
import sqlite3

database = sqlite3.connect('database.db')

cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS announcements(link TEXT, img_link TEXT, price INT, title TEXT, area TEXT, rooms INT, surface TEXT, publishedBy TEXT, agency TEXT)')

urlToScrap = 'https://nemutam.com/?pag=1'

uClient = urlopen(urlToScrap)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")

containers = page_soup.findAll("div", {"class":"thumbnail"})

for container in containers:
    link = container.a["href"]
    img_link = container.img["src"]
    price = container.find("span", {"class":"post-price"}).text
    title = container.find("div", {"class":"caption"}).p["title"]
    rows = container.div.table.findAll("td")
    area = rows[1].text
    rooms = rows[3].text
    surface = rows[5].text
    publishedBy = rows[7].text
    agency = rows[9].img["title"]
    cursor.execute('INSERT INTO announcements (link, img_link, price, title, area, rooms, surface, publishedBy, agency) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (link, img_link, price, title, area, rooms, surface, publishedBy, agency))
    database.commit()

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
