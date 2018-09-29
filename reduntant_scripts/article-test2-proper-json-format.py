
import bs4
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json

true = "true"
false = "false"

browser = webdriver.PhantomJS()
article_link = "http://ieeexplore.ieee.org/document/6546380/"


# Get the page source
browser.get(article_link)
WebDriverWait(browser, 20)
wait = WebDriverWait(browser, 12)

page_source = browser.page_source
soup = BeautifulSoup(page_source, 'html.parser')
soup_str = str(soup)

'''
BETTER THING WOULD BE TO FIRST STORE THE SOURCE ON THE COMPUTER THEN SCRAPE. REDUCES THE CHANCES OF FAILURE.
text = open("/home/theprophet/Atom/Scibase/article-page-source.txt")
text = str(text.read())
'''

metadata = re.findall(
    r'global\.document\.metadata=(\{[\s\S]+\})\;', soup_str, re.DOTALL)
json_data = json.dumps(json.loads(metadata[0]))
print(json_data)


# In order to avoid error where we have no issn
try:
    issn = re.findall(r'("issn":[\s\[\{\"\w\:\-\,\}]*])', json_data, re.DOTALL)
    print("{"+issn[0]+",")
except:
    print('{"issn":"none",')

# Adding ? to + in [\s\S]+? make the + which is a greedy operator lazy i.e it will try to match as few times as possible
# [\s\S] means any space or non space character. It matches all characters
try:
    abstract = re.findall(
        r'(\s\"abstract\"\:[\s\S]+?\.\"\,)', json_data, re.DOTALL)
    print(abstract[0])
except:
    abstract = re.findall(
        r'(\s\"abstract\"\:[\s\S]+?\"\,)', json_data, re.DOTALL)
    print(abstract[0])

# METRICS
metrics = re.findall(r'("metrics":[\s\{\w\"\:\,]*})', json_data, re.DOTALL)
print(metrics[0]+",")

# DOI
# Problem with the abstract for the link http://ieeexplore.ieee.org/document/6546378/
try:
    doi = re.findall(r'(\"doi\"\:[\s\S]+?\"\,)', json_data, re.DOTALL)
    print(doi[0])
except:
    print('"abstract":"none",')

# TITLE
title = re.findall(r'(\"title\"\:[\s\S]+?\"\,)', json_data, re.DOTALL)
print(title[0])

# publicationTitle
publicationTitle = re.findall(
    r'(\"publicationTitle\"\:[\s\S]+?\"\,)', json_data, re.DOTALL)
print(publicationTitle[0])

# We are getting the content between two keywords using regex. The () is the grouping element that gets displayed.
t = re.findall(
    r'("authors":\s\[\{\"affiliation\"\:[\S\s]*)\,\s+\"isDynamicHtml\"\:', json_data, re.DOTALL)
if(t):
    print(t[0]+"}")
else:
    t = re.findall(
        r'("authors":\s\[\{\"affiliation\"\:[\S\s]*)\,\s+\"pubLink\"\:', json_data, re.DOTALL)
    print(t[0]+"}")
