form urllib.request import urlopen as urlReq
form bs4 import BeautifulSoup as soup

urlToScrap = 'https://nemutam.com/?pag=1'

uClient = urlReq(urlToScrap)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")

containers = page_html.findAll("div", {"class":"???"})

for container in containers:
	