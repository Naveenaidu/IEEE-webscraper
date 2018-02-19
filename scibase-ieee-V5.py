import os
import bs4
import re
import sys
import json
import time
import random
import selenium
import requests
import argparse
from requests import ConnectionError
from bs4 import BeautifulSoup
from lxml import html
from lxml.cssselect import CSSSelector
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

global browser
browser = webdriver.PhantomJS()

# ------------------------------------------------------------

# Functions to create the folders and to gather the links of issues and articles

# Gets the home path

def get_path_home(Journal_name):
    print("Creating a home path\n")
    cwd = str(os.getcwd())
    home = str(cwd)+str("/Scibase/")+str(Journal_name)
    os.makedirs(home,exist_ok=True)
    return(home)

#Get Path

def get_path(vol_no,issue_no,home_path):

    # Path for volumes
    print("Creating folder vol "+str(vol_no))
    vol_path = home_path + "/vol_"+ str(vol_no)
    os.makedirs(vol_path,exist_ok=True)

    # Path for issues
    print("Creating folder issue "+str(issue_no))
    issue_path = vol_path +"/issue_"+str(issue_no)
    os.makedirs(issue_path,exist_ok=True)

    return(issue_path)

#Gets the page source

def get_page_source(url):
    global browser
    start_time = time.time()
    print("Getting page source of "+str(url))
    while True:
        try:
            page_source = requests.get(url)
            page_source = page_source.text
            return(page_source)
        except ConnectionError:
            print("Trying to reconnect to the server...")
            if (time.time() > start_time + connection_timeout):
                try:
                    time.sleep(80)
                    browser = webdriver.Firefox()
                    browser.get(url)
                    page_source = str(browser.page_source)
                    browser.quit()
                    return(page_source)
                except:
                    raise Exception('Unable to get updates after {} seconds of ConnectionErrors'.format(connection_timeout))
            else:
                print("Trying to reconnect to the server...")
                time.sleep(60)
                continue
        except OSError:
            print("Trying to reconnect to the server...")
            time.sleep(80)
            browser = webdriver.PhantomJS()
            browser.get(url)
            page_source = str(browser.page_source)
            browser.quit()
            return(page_source)

        except:
            print("ERROR COLLECTING THE PAGE SOURCE FROM "+ str(url))
            return('error')
            break

#Load the webpage in the selenium browser

def load_webpage(link,browser):
    connection_timeout = 180
    start_time = time.time()
    print("\nWaiting for the response from the url")

    while True:
        try:
            browser.get(link)
            break
        except ConnectionError:
            print("Trying to reconnect to the server...")
            if (time.time() > start_time + connection_timeout):
                try:
                    time.sleep(80)
                    browser = webdriver.Firefox()
                    browser.get(link)
                    break
                except:
                    raise Exception('Unable to get updates after {} seconds of ConnectionErrors'.format(connection_timeout))
            else:
                print("Trying to reconnect to the server...")
                time.sleep(60)
                continue

        except:
            print("ERROR COLLECTING THE PAGE SOURCE FROM "+ str(url))
            return('error')
            break




# Writing the link of the issue to the file. We will use this link to extract article links

def write_issue_links(issue_url,filePath):
    file_object = open(filePath,"w")
    full_url = "http://ieeexplore.ieee.org" + str(issue_url)
    file_object.write(full_url)
    print("Issue url written into file")
    file_object.close()

# Get the current Issue

def create_current_issue_dir(source,home_path,issue_url):
    print("Creating Current issue directory")
    soup = BeautifulSoup(source,"html.parser")
    issue_vol_info = soup.find("div",{"class":"breadcrumbs"}).text
    vol = re.findall(r'Volume\s(\d+)',issue_vol_info,re.DOTALL)
    issue = re.findall(r'Issue\s(\d+)',issue_vol_info,re.DOTALL)
    issue_path = get_path(vol[0],issue[0],home_path)
    issue_file_path = os.path.join(issue_path,issue[0])+'.txt'
    print("Writing the issue url of vol "+ str(issue[0]))
    write_issue_links(issue_url,issue_file_path)

# Gets the issue url and as well as pass the file_paths for storing the article_urls from a issue

def get_issue(url):
##It goes to the journal url, gets the issue_urls from the source code and store them in the particular filePath
##We first use re to get the vol_no and issue_no and use these to create the path where the url of that issue should be stored
##Then using that path we store the issue_url in that file.
## Now inorder to provide the path where the article link is stored we store the file_paths in a list and return it back to the main()
    source = get_page_source(url)
    print("Collecting the soup object for getting issue_urls")
    soup =BeautifulSoup(source,"html.parser")
    x = soup.find_all("div",{"class":"volumes"})
    y = (x[0].contents[1])

    #Setting the variables for the directory storage
    #journal_name = "XYZ"
    home_path = get_path_home(journal_name)
    create_current_issue_dir(source,home_path,url)


    soup = BeautifulSoup(str(y),"html.parser")
    #'x' stores the contents under the tag ("div":"volumes") which contains the list of numbers of volumes and articles.we use this data to create the folders
    for x in soup.find_all("li"):
        issue_vol_info = str(x.text)
        issue_url = x.contents[1].get('href')
        vol = re.findall(r'Vol\:\s(\d+)',issue_vol_info,re.DOTALL)
        issue = re.findall(r'Issue\:\s(\d+)',issue_vol_info,re.DOTALL)
        try:
            issue_path = get_path(vol[0],issue[0],home_path)
        except IndexError:
            print("Error here " + str(issue_vol_info) )
            continue
        file_path = os.path.join(issue_path,issue[0])+'.txt'
        print("Writing the issue url of vol "+ str(issue[0]))
        write_issue_links(issue_url,file_path)
        print("\n")

        #This stores the path to the home directory of the issue
        issue_home_dir.append(issue_path)
        #This has the path to the issue url file
        issue_link_path.append(file_path)


    print("Collected and stored Issue URL\n")
    sleep2 = random.uniform(20.5,70.5)
    print("Sleepin for : " +str(sleep2))
    time.sleep(sleep2)

# Every issue has articles. These articles are split into various pages. This gets the number of pages the articles are split into.

def get_number_pages_issue_url(issue_url):

    print("Getting the number of pages in issue_url:")
    source = get_page_source(issue_url)
    if(str(source) == str('error')):
        return('error')
    soup = BeautifulSoup(source,"html.parser")
    next_page  = soup.find("div",{"class":"pagination"})
    soup1 = BeautifulSoup(str(next_page),"html.parser")
    pages = 0
    for page_number in soup1.find_all("a"):
        pages+= 1

    #There might be only 1 page
    if(pages > 0):
        pages-= 2
    else:
        pages = 1

    return(pages)

#  Gets all the links to the articles present in that issue.

def get_article_links(issue_url):
    url1 = ""
    article_link_text = ""
    pages = get_number_pages_issue_url(issue_url)

    if(str(pages) == str('error')):
        article_link_text = ''
        return(article_link_text)

    print("pages:= " + str(pages))
    sleep_time = random.uniform(10.5,35.5)
    print("Sleeping for "+str(sleep_time))
    time.sleep(sleep_time)
    for x in range(1,pages+1):

        url1 = issue_url +"&pageNumber=" + str(x)
        source = get_page_source(url1)
        print("Getting all the article links from pageNumber: "+ str(x))
        soup = BeautifulSoup(source,"html.parser")

        for link in soup.find_all("div",{"class":"txt"}):
            try:
                y= (link.contents[3]).contents[1]
                y = y.get("href")
                article_link = "http://ieeexplore.ieee.org" + str(y)
                article_link_text+= str(article_link)+str("citations?ctx=citations")+"\n"
            except:
                continue
    #Retruns a all the article_links in a string format
    return(article_link_text)

# This gets the article_urls from the issue_page_url and stores them in a file

def store_article_url(browser):

    global issue_pointer
    '''
    issue_home_dir[] gives us the home directory of issue.
    issue_link_path[] gives the path from where the url of the issue can be read from.
    '''
    article_path = ""

    '''
    Lets store the value of x in the below loop in a variable so that if anywhere the script stops we can start from that script. Say the script
    stops at x=3. That means the script has stopped at the issue 3 of some volume. We can  find that path from issue_home_dir[x].
    So by changing the for loop range from range(x,len(issue_link_path)) we can continue from the part where we left off.
    '''
    for x in range(issue_pointer,len(issue_link_path)):

        if(x%100 == 0):
            time.sleep(100)
        print("Article pointer := "+ str(x) )

        article_folder = str(issue_home_dir[x]) +str("/article")
        os.makedirs(str(article_folder),exist_ok=True)
        article_path = str(article_folder)+ str("/article_url.txt")

        # Gets the article links from a issue url

        with open(issue_link_path[x],"r") as content_file:
            print("Reading Issue_url from "+ str(issue_link_path[x]))
            issue_url = content_file.read()
            print("issue_url:= " + str(issue_url))
            article_links = get_article_links(issue_url)

        with open(article_path,"w+") as content_file:
            print("Writing the article_links at path "+ str(article_path)+"\n")
            content_file.write(article_links)
            print("--------------------------------")

# --------------------------------------------------------

# Functions to get the data from the article links. Using Selenium to scrape DATA

# Get soup

def get_soup(browser):
    source = str(browser.page_source)
    soup = BeautifulSoup(source,'html.parser')
    return(soup)

#Most part of the article data is stored in the 'global.document.metadata' of the page source. REGEX is used to scrape them.

def get_metadata(browser):
    print("\n Fetching the metadata from the page source\n")
    str_soup = str(get_soup(browser))
    metadata = re.findall(r'global\.document\.metadata=(\{[\s\S]+\})\;',str_soup,re.DOTALL)
    metadata = json.dumps(json.loads(metadata[0],object_pairs_hook=OrderedDict))
    return(metadata)

# Get the ISSN from the article

def get_issn(json_data):
    print("Fetching the ISSN....")
    try:
        issn = re.findall(r'(\"issn\"\:[\s\S]+?\,)\s\"article',json_data,re.DOTALL)
        return(issn[0])
    except:
        issn = '"issn":"none",'
        return(issn)

# Abstract

def get_abstract(json_data):
    print("Fetching the Abstract....")
    try:
        abstract = re.findall(r'(\"abstract\"\:[\s\S]+?\.\"\,)\s',json_data,re.DOTALL)
        return(abstract[0])
    except:
        abstract = '"abstract":"null",'
        return(abstract)

# Metrics

def get_metrics(json_data):
    print("Fetching the Metrics....")
    try:
        metrics = re.findall(r'(\"metrics\"\:[\s\S]+?\}\,)\s\"',json_data,re.DOTALL)
        return(metrics[0])
    except:
        metrics = '"metrics":"null",'
        return(metrics)

# DOI

def get_doi(json_data):
    print("Fetching the D.O.I....")
    try:
        doi = re.findall(r'(\"doi\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(doi[0])
    except:
        doi = '"doi":"null",'
        return(doi)

# TITLE

def get_title(json_data):
    print("Fetching the Title....")
    try:
        title = re.findall(r'(\"title\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(title[0])
    except:
        title = '"title":"null",'
        return(title)

# Publication TITLE

def get_pubTitle(json_data):
    print("Fetching the PublicationTitle....")
    try:
        pubTitle = re.findall(r'(\"publicationTitle\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(pubTitle[0])
    except:
        pubTitle = '"publicationTitle":"null",'
        return(pubTitle)

# Authors

def get_authors(json_data):
    print("Fetching the Authors....")
    try:
        authors = re.findall(r'(\"authors\"\:[\s\S]+?\,)\s\"issn',json_data,re.DOTALL)
        return(authors[0])
    except:
        authors = '"authors":"none",'
        return(authors)

# Keywords

def get_keywords(json_data):
    try:
        keywords = re.findall(r'("keywords":[\s\S]+\]\,)',json_data,re.DOTALL)
        return(keywords[0])
    except:
        keywords = '"keywords":"none",'
        return(keywords)

#Checking for the presence of citation

def check_citation_presence(json_data):
    print("\nChecking for the presence of citations")
    check = re.findall(r'\"citationCountPaper\"\:\s([0-9]+)\,\s\"',json_data,re.DOTALL)
    if(int(check[0]) > 0):
        return(True)
    else:
        return(False)

# Number of IEEE citations

#The position of ieee citations will either be the first or no-where

def get_num_ieee_citations(citations,link):
    global error;
    print("Fetching the number of IEEE citations....")
    try:
        temp = re.findall(r'.*IEEE\s\(\d+\)',citations,re.DOTALL)
        num_ieee_citations = re.findall(r'\d+',temp[0])
        num_ieee_citations = int(num_ieee_citations[0])
        return(num_ieee_citations)
    except IndexError:
        #errors.append(link)
        print("No IEEE citations")
        return(0)
    except:
        return(0)

# Number of NON IEEE CITATIONS

def get_num_non_ieee_citations(citations,link):
    print("Fetching the number of NON-IEEE citations\n")
    try:
        temp = re.findall(r'\sOther[\s\S]+\s\(\d+\)',citations,re.DOTALL)
        num_non_ieee_citations = re.findall(r'\d+',temp[0])
        num_non_ieee_citations = int(num_non_ieee_citations[0])
        return(num_non_ieee_citations )
    except IndexError:
        #errors.append(link)
        print("No non-IEEE citations")
        return(0)
    except:
        return(0)

# Load all citations. The citations are delivered via AJAX. So we need to press "view-all" button to load all citations

def load_citation(browser,name):
    print("Loading All Citations.....")
    while True:
        try:
            element = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#anchor-paper-citations-'+str(name)+' > div.load-more-container > button > span')))
            view_button = browser.find_element_by_css_selector('#anchor-paper-citations-'+str(name)+' > div.load-more-container > button > span')
            view_button.click()
            continue
        except:
            return

# ---------------------------------------------------------------------------

# Functions to get the information of a citation.

# Get the content of each citation paragraph. The entire citation information is present in the tag.
#This tag doesn't include the information like pp.,vol,etc

def get_citation_tag(x,name,tree):

    citations_tag = '#anchor-paper-citations-'+str(name)+' > div:nth-child(' + str(x) + ') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'
    citations = tree.cssselect(citations_tag)[0].text
    return(citations)

# Getting the extra information of the citations

#All the citations are under the class "description ng-binding". Here we are getting the soup list of all the citations.

def extra_citat_info_tag(soup):#Pass the soup of the completely loaded page with cit.
    citations_extra =  soup.find_all("div",{"class":"description ng-binding"})
    return(citations_extra)

# Citation Authors

def get_citation_authors(citation_tag):
    #print("Fetching the Citation authors....")
    try:
        citations_authors = re.findall(r'([A-Za-z\s\.\-]+)\,\s',citation_tag,re.DOTALL)
        error_catch = citations_authors[len(citations_authors)-1]#CAtching the error when no authors are present. CAN BE IMPROVED
        a = '"authors":['
        b = ""

        # Putting the authors in the list

        for z in range(0,len(citations_authors)-1):
            b = b + '"'+str(citations_authors[z])+'",'

        # Final author with appropriate tags

        c = '"'+str(citations_authors[len(citations_authors)-1])+'"],'
        authors = a+b+c
        return(authors)
    except:
        authors = '"authors":["none"],'
        return(authors)

# Citation Article Name

def get_citation_article_name(citation_tag):
    #print("Fetching the Citation Article name....")
    try:
        citations_article_name = re.findall(r'\"(.+)\"',citation_tag,re.DOTALL)
        article_name = '"article name":"'+str(citations_article_name[0])+'",'
        return(article_name)
    except:
        article_name = '"Article Name":"none",'
        return(article_name)

# Journal Name

def get_citation_journal(x,name,tree):
    #print("Fetching the Citation Journal Name....")
    try:
        # The journal name is in intalics and is present in a sperate tag

        citations_journal_cssselector = '#anchor-paper-citations-'+str(name) +'> div:nth-child(' + str(x) +') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > em:nth-child(1)'
        citations_journal_tag = tree.cssselect(citations_journal_cssselector)[0]
        journ_name = '"Journal Name":"'+str(citations_journal_tag.text)+'",'
        return(journ_name)
    except:
        journ_name = '"Journal Name":"none",'
        return(journ_name)

# CITATION VOLUME

def get_citation_vol(citation):
    #print("Fetching the Citation volume no....")
    try:
        citations_vol = re.findall(r'vol\.\s([0-9A-Za-z\-]+)',citation,re.DOTALL)
        citation_vol = '"vol.": "'+str(citations_vol[0])+'",'
        return(citation_vol)
    except:
        citation_vol = '"vol":"none",'
        return(citation_vol)

# CITATION PP.

def get_citation_pp(citation):
    #print("Fetching the citation pp. ....")
    try:
        citations_pp = re.findall(r'pp\.\s([A-Za-z0-9\-]+)',citation,re.DOTALL)
        citation_pp = '"pp.": "'+str(citations_pp[0])+'",'
        return(citation_pp)
    except:
        citation_pp = '"pp.":"none",'
        return(citation_pp)

# CITATION YEAR

def get_citation_year(citation):
    #print("Fetching the Citation year....")
    try:
        citations_year = re.findall(r'\,\s([0-9]+)',citation,re.DOTALL)
        citation_year = '"Year": "'+str(citations_year[0])+'",'
        return(citation_year)
    except:
        citation_year = '"Year":"none",'
        return(citation_year)

# CITATION ISSN

def get_citation_issn(citation):
    #print("Fetching the Citationi ISSN ....")
    try:
        citations_issn = re.findall(r'ISSN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_issn = '"ISSN": "'+str(citations_issn[0])+'",'
        return(citation_issn)
    except:
        citation_issn= '"ISSN":"none",'
        return(citation_issn)

# CITATION ISBN

def get_citation_isbn(citation):
    #print("Fetching the Citation ISBN ....")
    try:
        citations_isbn = re.findall(r'ISBN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_isbn = '"ISBN": "'+str(citations_isbn[0])+'"'
        return(citation_isbn)
    except:
        citation_isbn = '"ISBN":"none"'
        return(citation_isbn)

# ----------------------------------------------------------

# Gettings the citations

def get_citation(num_citations,name,tree,soup):

# Soup of the completely loaded page.
# The citations are first scraped using bs4 using extra_citat_info_tag. Once we get the list of all the posibile values of citations from the soup object, we loop through them.
# The get_citation_tag is used to get the particular division where the x'th citation is present using css selector

    print("\nCreating the json_data for the citations :\n")
    global citationCount
    if (name == "nonieee"):
        citationCount = citationCount
        #print(citationCount)
    else:
        citationCount = 0


    citation_json = '{"'+str(name)+'-citations":['
    citations_extra_info = extra_citat_info_tag(soup)
    for x in range(2,num_citations+2):
        print("Fetching "+str(name)+" citations")
        print("Getting citation detail : "+str(x))
        citation = get_citation_tag(x,name,tree) #This gets the complete paragraph of the citation
        cit_author = get_citation_authors(citation)
        cit_article_name = get_citation_article_name(citation)
        cit_journal_name = get_citation_journal(x,name,tree)

        #Getting the extra info of citations

        cit_extra_info = citations_extra_info[citationCount].text
        citationCount+=1

        cit_vol = get_citation_vol(cit_extra_info)
        cit_pp = get_citation_pp(cit_extra_info)
        cit_year = get_citation_year(cit_extra_info)
        cit_issn = get_citation_issn(cit_extra_info)
        cit_isbn = get_citation_isbn(cit_extra_info)

        #Making the json of the citation

        citation_json+= "{"+cit_author + cit_article_name + cit_journal_name + cit_vol + cit_pp + cit_year + cit_issn + cit_isbn

        if( x <= num_citations):
            citation_json+= "},"
        else:
            citation_json+= "}"

    if(name == "ieee"):
        citation_json+= "]},"
    else:
        citation_json+= "]}"

    return(citation_json)

# -------------------------------------------------------------------------
# Functions that get the complete json data from the article url

# Gets the data in json format from  the article url

def get_json_data(metadata,browser,link,article_json_path):
    global citationCount
    global num_tries
    global error_file_object

    # We are testing the number of times get_json_data is called due to Index Error. Which occurs because the IEEE website blocks us out.


    print("Starting the process to get the information about the article in  json format\n")
    json_data="{"
    json_data+= get_issn(metadata) + get_metrics(metadata) +get_doi(metadata)
    json_data+= get_title(metadata)+get_pubTitle(metadata)+get_abstract(metadata)+ get_authors(metadata)+get_keywords(metadata)

    json_data+='"citations":['

    # We are testing the number of times get_json_data is called due to Index Error. Which occurs because the IEEE website blocks us out.

    num_tries+= 1
    if(num_tries > 6):

        # Not writing in a descriptive manner, such as Link:-,Path:-. Reaseon:- Maybe in Future I can automate it.
        # The first line will be the link. Second line --> Path. Followed by "\n".
        error_file_object.write(str(link)+str("\n"))
        error_file_object.write(str(article_json_path)+str("\n\n"))
        print("Error, trying to get the json data from the article link.")
        print("Scrape this article manually. Check error_file.txt for more info")
        json_data+= "scrape this manually]}"
        time.sleep(600)
        return(json_data)

    x = False
    x = check_citation_presence(metadata)

    if ( x == False):
        print("Citation NOT Found\n")
        json_data+= "null]}"
        return(json_data)
    else:

            print("Citations Found\n")
            soup1 = get_soup(browser)
            try:
                num_citations = soup1.find_all('h2',{'class':'document-ft-section-header ng-binding'})
                length = len(num_citations) - 1
                num_ieee_citations = get_num_ieee_citations(str(num_citations[0].text),link)
                num_non_ieee_citations = get_num_non_ieee_citations(str(num_citations[length].text),link)
            except IndexError:

                print("Error at getting json data.Sleeping and changing the browser")
                if(browser.name == "phantomjs"):
                    browser.quit()
                    time.sleep(180.123)
                    browser = webdriver.Firefox()
                    browser.get(link)
                    data = get_json_data(metadata,browser,link,article_json_path)
                    browser.quit()
                    return(data)

                else:
                    browser.quit()
                    time.sleep(180.20)
                    browser = webdriver.PhantomJS()
                    browser.get(link)
                    data = get_json_data(metadata,browser,link,article_json_path)
                    browser.quit()
                    return(data)


            load_citation(browser,"ieee")
            load_citation(browser,"nonieee")


            #Wait for the page to load  with all citations then grab the page source
            WebDriverWait(browser,30)

            soup = get_soup(browser)

            #Declare the tree for lxml
            tree = html.fromstring(str(browser.page_source))

            json_data+= get_citation(num_ieee_citations,"ieee",tree,soup)
            print("IEEE citation data retrieved\n")
            json_data+= get_citation(num_non_ieee_citations,"nonieee",tree,soup)
            print("NON-IEEE citation data retrieved\n")
            citationCount = 0

            #Final tags of Json Data
            json_data+= "]}"
            return(json_data)

# Starts the process of getting the json data from the article

def initialize_article_json_data(link,browser,article_json_path):

    load_webpage(link,browser)
    print("\nBrowser will wait for 30ms for the page to load\n")
    WebDriverWait(browser,10)
    #Get the JSON DATA to extract the first half
    metadata= get_metadata(browser)
    #Get the json data
    json_data = get_json_data(metadata,browser,link,article_json_path)

    return(json_data)


# This function reads the article links from the files and initiates the process of getting the json data

def get_article_info(browser):
    global issue_number
    global num_tries
    global article_number
    article_count = 1
    article_links = []
    browser_count = 0
    for x in range(issue_number,len(issue_home_dir)):

        # Reading from the first article link.
        article_count = 1

        print("------------------------------------------------------------------------------")
        # The path where the article links are stored
        article_home_dir = str(issue_home_dir[x]) + str('/article')
        article_link_file = str(article_home_dir) + str('/article_url.txt')
        print("Issue Number:= "+str(x+1))


        #Reading the links from the article files
        with open(article_link_file,"r") as content_file:
            print("Reading the article_url from file := " + str(article_link_file))
            article_links = content_file.read().splitlines()

        # If the user wants to resume the script from a particular article number of the issue. He gives that number in
        # article_number argument. We then loop through the articles until we reach that number i.e the article_link.
        # The user needs to count the article he wants to continue from. He can do this manually or using only code editors.
        for links in article_links:
            if(int(article_number) > article_count):
                article_count+=1
                continue

            print("\nIssue Number : "+str(x))
            print("Article Number : "+str(article_count)+str("\n"))
            article_number = 1
            num_tries = 0
            if(browser_count == 0):
                print("\nBrowser: FireFox" )
                browser = webdriver.Firefox()
                browser_count = 1
            else:
                print("\nBrowser : PhantomJS")
                browser = webdriver.PhantomJS()
                browser_count = 0



            article_json_folder = str(article_home_dir)+str("/") +str(article_count)
            os.makedirs(article_json_folder,exist_ok = True)
            article_json_path = str(article_json_folder) +str('/') +str(article_count)+str('.json')

            article_count+= 1




            print("\nStarting the process to get the json_data from :- "+str(links)+"\n")
            print("Reading url from:= " + str(article_link_file)+str("\n"))
            json_data = initialize_article_json_data(str(links),browser,article_json_path)
            print("\nPath of storage : " + str(article_json_path)+str("\n"))



            with open(article_json_path,"w+") as data:
                data.write(json_data)

            ##Make the script Sleep
            browser.quit()
            sleep1 = random.uniform(1.5,2.5)
            sleep1 = sleep1*50.3
            print("------------------------------------")
            print("Sleeping for : " + str(sleep1))
            time.sleep(sleep1)
            print("I am AWAKE!!")

# -----------------------------------------------------------

# Functions to start the process from where it has been stopped

def store_directory_path(path):
    cwd = str(os.getcwd())+str("/Scibase/")+str(journal_name)
    dir_path = str(cwd) + str("/directory_path.txt")
    with open(dir_path,"w+") as f:
        f.write(json.dumps(path))

def read_directory_path():
    cwd = str(os.getcwd())+str("/Scibase/")+str(journal_name)+str("/directory_path.txt")
    path = str(cwd)
    source  = open(path).read()
    data = json.loads(str(source))
    return(data)

# ---------------------------------------------------------

# Main function

def main(url):

    global issue_number
    global issue_pointer
    global args
    global issue_home_dir

    if(args.resume == False):

        print("Starting get_issue()...")
        get_issue(url)
        store_directory_path(issue_home_dir)
        print("\nStarting store_article_url()...\n")
        store_article_url(browser)
        time.sleep(100)
        print("---------------------------- GETTING THE JSON DATA --------------------------------------------------")
        print("\nStarting the function get_article_info...\n")
        get_article_info(browser)
        print("------------------Errors--------------------")
        #print_errors()

    if(args.resume):

        # If the script stops while writing article article links:
        # Getting the path from the file


        issue_home_dir = read_directory_path()


        # This case runs when we want to continue writing the article links. When we do that we dont give issue_number as an input

        if((issue_pointer > -1)and(args.issue_number is None)):

            #issue_pointer = int(args.issue_pointer)
            print("-------------------------------------")
            print("Resuming the script")
            print("\nStarting store_article_url()...\n")
            store_article_url(browser)
            time.sleep(100)
            print("--------------- GETTING THE JSON DATA ----------------------")
            print("\nStarting the function get_article_info...\n")
            get_article_info(browser)
            print("------------------Errors--------------------")

        if(issue_number > -1):

            print("Getting Ready.....")
            #time.sleep(40)
            #issue_number = int(args.issue_number)

            print("---------------------------- GETTING THE JSON DATA --------------------------------------------------")
            print("\nStarting the function get_article_info...\n")
            get_article_info(browser)
            print("------------------Errors--------------------")


if __name__ == "__main__":
    #url of the most recent issue of a journal'
    global url
    #url = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=6536343&punumber=6528086'
    url = 'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=6528086'

    # Used to keep track of how many times there is a IndexError at get_json_data. This happens when the IEEE website blocks us out.
    global num_tries
    num_tries = 0

    connection_timeout = 180

    #Storing the path
    global issue_home_dir
    global issue_link_path
    #issue_home_dir stores the home path of a particular issue
    #Contatins the path to the file where issue links are stored
    issue_home_dir = []
    issue_link_path = []

    global journal_name

    # (Don't change). Used to extract the citations.
    global citationCount
    citationCount = 0

    global issue_pointer
    global issue_number
    issue_pointer = 0
    issue_number = 0

    global article_number
    article_number = int(1)

    #Arguments from terminal
    global parser
    parser = argparse.ArgumentParser()

    parser.add_argument("journal_name",help="Enter the journal name")
    parser.add_argument("-url",action = 'store',dest = "url",help = 'Enter the Most recent issue url')
    parser.add_argument("-r",action='store_true',default = False,dest="resume",help="Resumes the script.")
    parser.add_argument('-write_article_link',action='store',dest = 'issue_pointer',help = "Enter the issue  number.",type = int)
    parser.add_argument('-issue_number',action='store',dest='issue_number',help="Enter the json pointer. Use when script fails  while collecting article info",type = int)
    parser.add_argument('-article_number',action='store',dest='article_number',help="Article Number from which you want to run the script from.")

    args = parser.parse_args()

    # If resume option is selected and neither issue_pointer nor issue_number is givern
    '''
    if('-r' in vars(args) and '-sap' not in vars(args)):
        print("Invalid number of arguments")
        parser.error(' The -r argument requires  a value of either -sap or -jp ')
        sys.exit(1)

    if(args.resume and args.issue_pointer and args.json):
        print("Invalid number of arguments.")
        print("I am not dumb,you know!! :) ")
        parser.error('Either the value either for -sap or -jp')
        sys.exit(1)

    '''

    # Issue pointer is used when the issue links are written. But the script failed while writing article links
    # Issue number and article number is given when the the script fails while collecting the json_data.

    args = parser.parse_args()
    journal_name = args.journal_name
    issue_pointer = args.issue_pointer
    if(issue_pointer is None):
        issue_pointer = int(0)
    else:
        issue_pointer = int(args.issue_pointer)

    issue_number = args.issue_number
    if(issue_number is None):
        issue_number = int(0)
    else:
        issue_number = int(args.issue_number)

    article_number = args.article_number
    if(article_number is None):
        article_number = int(1)
    else:
        article_number = int(args.article_number)

    #Creating a error file. This file contains the link of all those articles which have to be scraped manually
    global error_file_path
    global error_file_object
    cwd = os.getcwd()
    home_file_path = str(cwd)+str("/Scibase/")+str(journal_name)
    os.makedirs(home_file_path,exist_ok=True)
    error_file_path = str(home_file_path) + str("/error_file.txt")
    error_file_object = open(error_file_path,"a")


    main(url)
