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

citationCount = 0

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
################################################################
#THE BELOW FUNCTIONS ARE FOR CITATIONS
##Get the content of each citation paragraph
def get_citation_tag(x,name,tree):
    citations_tag = '#anchor-paper-citations-'+str(name)+' > div:nth-child(' + str(x) + ') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'
    citations = tree.cssselect(citations_tag)[0].text
    return(citations_tag)

##EXTRA CITATION SOUP OBJECT. GETS THE PP.,VOL, etc.
#All the citations are under the class "description ng-binding". Here we are getting the soup list of all the citations.
def extra_citat_info_tag(soup):#Pass the soup of the completely loaded page with cit.
    citations_extra =  soup.find_all("div",{"class":"description ng-binding"})
    return(citations_extra)

##CITATION Authors
def get_citation_authors(citation_tag):
    try:
        citations_authors = re.findall(r'([A-Za-z\s\.\-]+)\,\s',citation_tag,re.DOTALL)
        error_catch = citations_authors[len(citations_authors)-1]#CAtching the error when no authors are present. CAN BE IMPROVED
        a = '"authors":['
        b = ""
        for z in range(0,len(citations_authors)-1):
            b = b + '"'+str(citations_authors[z])+'",'
        #Printing the final author with appropriate tags
        c = '"'+str(citations_authors[len(citations_authors)-1])+'"],'
        authors = a+b+c
        return(authors)

    except:
        authors = '"authors":["none"],'
        return(authors)

##CITATION ARTICLE NAME
def get_citation_article_name(citation_tag):
    try:
        citations_article_name = re.findall(r'\"(.+)\"',citation_tag,re.DOTALL)
        article_name = '"article name":"'+str(citations_article_name[0])+'",'
        return(article_name)
    except:
        article_name = '"Article Name":"none",')
        return(article_name)

##JOURNAL NAME
def get_citation_journal(x,name):
    try:
        citations_journal_cssselector = '#anchor-paper-citations-'+str(name) +'> div:nth-child(' + str(x) +') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > em:nth-child(1)'
        citations_journal_tag = tree.cssselect(citations_journal_cssselector)[0]
        journal_name = '"Journal Name":"'+str(citations_journal_tag.text)+'",'
        return(journal_name)
    except:
        journal_name = '"Journal Name":"none",'
        return(journal_name)

## CITATION VOLUME
def get_citation_vol(citation):
    try:
        citations_vol = re.findall(r'vol\.\s([0-9A-Za-z\-]+)',citation,re.DOTALL)
        citation_vol = '"vol.": "'+str(citations_vol[0])+'",'
        return(citation_vol)
    except:
        citation_vol = '"vol":"none",'
        return(citation_vol)

## CITATION PP.
def get_citation_pp(citation):
    try:
        citations_pp = re.findall(r'pp\.\s([A-Za-z0-9\-]+)',citation,re.DOTALL)
        citation_pp = '"pp.": "'+str(citations_pp[0])+'",'
        return(citation_pp)
    except:
        citation_pp = '"pp.":"none",'
        return(citation_pp)

## CITATION YEAR
def get_citation_year(citation):
    try:
        citations_year = re.findall(r'\,\s([0-9]+)',citation,re.DOTALL)
        citation_year = '"Year": "'+str(citations_year[0])+'",'
        return(citation_year)
    except:
        citation_year = '"Year":"none",'
        return(citation_year)

##CITATION ISSN
def get_citation_issn(citation):
    try:
        citations_issn = re.findall(r'ISSN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_issn = '"ISSN": "'+str(citations_issn[0])+'",'
        return(citation_issn)
    except:
        citation_issn= '"ISSN":"none",'
        return(citation_issn)

##CITATION ISBN
def get_citation_isbn(citation):
    try:
        citations_isbn = re.findall(r'ISBN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_isbn = '"ISBN": "'+str(citations_isbn[0])+'",'
        return(citation_isbn)
    except:
        citation_isbn = '"ISBN":"none",'
        return(citation_isbn)
##################################################################
def get_citation(num_citations,name,tree,soup):#soup of the completely loaded page
#The citations are first scraped using bs4 using extra_citat_info_tag. Once we get the list of all the posibile values of citations from the soup object, we loop through them.
#The get_citation_tag is used to get the particular division where the x'th citation is present using css selector
    citation_json = '"{"'+str(name)+'-citations":[{'
    citations_extra_info = extra_citat_info_tag(soup)
    for x in range(2,num_citations+2):
        citation = get_citation_tag(x,name,tree)
        cit_author = get_citation_authors(citation)
        cit_article_name = get_citation_article_name(citation)
        cit_journal_name = get_citation_journal(citation)
        #Getting the extra info of citations
        cit_extra_info = citations_extra_info[citationCount++].text

        cit_vol = get_citation_vol(cit_extra_info)
        cit_pp = get_citation_pp(cit_extra_info)
        cit_year = get_citation_year(cit_extra_info)
        cit_issn = get_citation_issn(cit_extra_info)
        cit_isbn = get_citation_isbn(cit_extra_info)

        #Making the json of the citation
        citation_json+= cit_author + cit_article_name + cit_journal_name + cit_vol + cit_pp + cit_year + cit_issn + cit_isbn

        if( x <= num_citations): # x<= num_ieee_citations
            citation_json+= "},"
        else:
            citation_json+= "}"

    citation_json+= "]},"
    return(citation_json)     
