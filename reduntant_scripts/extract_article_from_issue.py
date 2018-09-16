import bs4
import requests
from bs4 import BeautifulSoup
import re

url =  "http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=1722"

def get_article_links(x):
    global url
    url1 = url +"&pageNumber=" + str(x)
    source = (requests.get(url1)).text
    soup = BeautifulSoup(source,"html.parser")

    for link in soup.find_all("div",{"class":"txt"}):
        y= (link.contents[3]).contents[1]
        y = y.get("href"))
        article_link = "http://ieeexplore.ieee.org" + str(y)
        print(article_link)



def main():
    source = (requests.get(url)).text
    soup = BeautifulSoup(source,"html.parser")
    next_page  = soup.find("div",{"class":"pagination"})
    soup1 = BeautifulSoup(str(next_page),"html.parser")
    pages = 0
    for page_number in soup1.find_all("a"):
        pages+= 1
    pages-= 2

    for x in range(1,pages+1):
        get_article_links(x)

if __name__ == '__main__':
    main()
