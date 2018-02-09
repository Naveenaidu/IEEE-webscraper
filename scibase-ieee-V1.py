import bs4
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
from lxml import html
from lxml.cssselect import CSSSelector

def get_response(url):
    try:
        browser.get(url)
    except:
        print("Invalid URL")

def get_page_source(browser):
    page_source = browser.page_source
    return page_source

def get_soup(browser):
    response = get_page_source(browser)
    soup = BeautifulSoup(response,'html.parser')
    return soup

def get_json_data(browser):
    str_soup = str(get_soup(browser))
    metadata = re.findall(r'global\.document\.metadata=(\{[\s\S]+\})\;',soup_str,re.DOTALL)
    json_data = json.dumps(json.loads(metadata[0],object_pairs_hook=OrderedDict))
    return json_data

#Store the data from the above function in a variable and pass it
def get_issn(json_data):
    try:
        issn = re.findall(r'(\"issn\"\:[\s\S]+?\,)\s\"article',json_data,re.DOTALL)
        return(issn[0])
    except:
        issn = '"issn":"none",'

##Abstract
def _abstract(json_data):
    try:
        abstract = re.findall(r'(\"abstract\"\:[\s\S]+?\.\"\,)\s',json_data,re.DOTALL)
        return(abstract[0])
    except:
        abstract = '"abstract":"null",'
        return(abstract)
##Metrics
def get_metrics(json_data):
    try:
        metrics = re.findall(r'(\"metrics\"\:[\s\S]+?\}\,)\s\"',json_data,re.DOTALL)
        return(metrics[0])
    except:
        metrics = '"metrics":"null",'
        return(metrics)

##DOI
def get_doi(json_data):
    try:
        doi = re.findall(r'(\"doi\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(doi[0])
    except:
        doi = '"doi":"null",'
        return(doi)

##TITLE
def get_title(json_data):
    try:
        title = re.findall(r'(\"title\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(title[0])
    except:
        title = '"title":"null",'
        return(title)

##Publication TITLE
def get_pubTitle(json_data):
    try:
        publTitle = re.findall(r'(\"publicationTitle\"\:[\s\S]+?\")\,\s\"',json_data,re.DOTALL)
        return(pubTitle[0])
    except:
        pubTitle = '"publicationTitle":"null",'
        return(pubTitle)

#Authors
def get_authors(json_data):
    try:
        authors = re.findall(r'(\"authors\"\:[\s\S]+?)\,\s\"issn',json_data,re.DOTALL)
        return(authors[0])
    except:
        authors = '"authors":"none",'
        return(authors)

#Checking if the citations are present or not
def check_citation_presence(browser):
    try:
        WebDriverWait(20,browser).until(EC.presence_of_element_located((By.XPATH,'//*[@id="LayoutWrapper"]/div[5]/div[3]/div/section[2]/div[2]/div[1]/div[2]/div[1]/button[1]')))
        return(True)
    except:
        #print("null]}")
        return(False)
        #citations_present = False

##Number of IEEE citations
#The position of ieee citations will either be the first or no-where
def num_ieee_citations(citations):
    try:
        temp = re.findall(r'.*IEEE\s\(\d+\)',citations)
        num_ieee_citations = re.findall(r'\d+',temp[0])
        num_ieee_citations = int(num_ieee_citations[0])
        return(num_ieee_citations )
    except:
        return(0)

##Number of NON IEEE CITATIONS
def num_non_ieee_citations(citations):
    try:
        temp = re.findall(r'.*IEEE\s\(\d+\)',citations)
        num_non_ieee_citations = re.findall(r'\d+',temp[0])
        num_non_ieee_citations = int(num_non_ieee_citations[0])
        return(num_non_ieee_citations )
    except:
        return(0)

##LOAD IEEE Citations
def load_ieee_citation(browser):
    while True:
        try:
            element = WebDriverWait(20,browser).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#anchor-paper-citations-ieee > div.load-more-container > button > span')))
            view_button = browser.find_element_by_css_selector('#anchor-paper-citations-ieee > div.load-more-container > button > span')
            view_button.click()
            continue
        except:
            return

##LOAD NON IEEE CiTATION
def load_non_ieee_citations(browser):
        while True:
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#anchor-paper-citations-nonieee > div.load-more-container > button > span')))
                view_button = browser.find_element_by_css_selector('#anchor-paper-citations-nonieee > div.load-more-container > button > span')
                view_button.click()
                continue
            except:
                return
