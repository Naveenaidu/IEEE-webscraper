
import bs4
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from lxml import html
from lxml.cssselect import CSSSelector

true = "true"
false = "false"

browser= webdriver.PhantomJS();
article_link= "http://ieeexplore.ieee.org/document/1262027"


#Initialize the Browser
browser = webdriver.PhantomJS();
browser.get(article_link)
WebDriverWait(browser,20)
wait = WebDriverWait(browser,15)
citations_present = True

page_source = browser.page_source
soup = BeautifulSoup(page_source,'html.parser')
soup_str = str(soup)


'''
BETTER THING WOULD BE TO FIRST STORE THE SOURCE ON THE COMPUTER THEN SCRAPE. REDUCES THE CHANCES OF FAILURE.
text = open("/home/theprophet/Atom/Scibase/article-page-source.txt")
text = str(text.read())
'''

metadata = re.findall(r'global\.document\.metadata=(\{[\s\S]+\})\;',soup_str,re.DOTALL)
json_data = json.dumps(json.loads(metadata[0]))
file_object = open("sourcePage_from_phantomjsBrowser2.txt","w")
file_object.write(json_data)
file_object.close

'''''''''

#In order to avoid error where we have no issn
try:
    issn = re.findall(r'("issn":[\s\[\{\"\w\:\-\,\}]*])',json_data,re.DOTALL)
    print("{"+issn[0]+",")
except:
    print('{"issn":"none",')

#Adding ? to + in [\s\S]+? make the + which is a greedy operator lazy i.e it will try to match as few times as possible
#[\s\S] means any space or non space character. It matches all characters
try:
    abstract = re.findall(r'(\s\"abstract\"\:[\s\S]+?\.\"\,)',json_data,re.DOTALL)
    print(abstract[0])
except:
    abstract = re.findall(r'(\s\"abstract\"\:[\s\S]+?\"\,)',json_data,re.DOTALL)
    print(abstract[0])

#METRICS
metrics = re.findall(r'("metrics":[\s\{\w\"\:\,]*})',json_data,re.DOTALL)
print(metrics[0]+",")

#DOI
#Problem with the abstract for the link http://ieeexplore.ieee.org/document/6546378/
try:
    doi = re.findall(r'(\"doi\"\:[\s\S]+?\"\,)',json_data,re.DOTALL)
    print(doi[0])
except:
    print('"abstract":"none",')

#TITLE
title = re.findall(r'(\"title\"\:[\s\S]+?\"\,)',json_data,re.DOTALL)
print(title[0])

#publicationTitle
publicationTitle = re.findall(r'(\"publicationTitle\"\:[\s\S]+?\"\,)',json_data,re.DOTALL)
print(publicationTitle[0])

#We are getting the content between two keywords using regex. The () is the grouping element that gets displayed.
t=re.findall(r'("authors":\s\[\{\"affiliation\"\:[\S\s]*)\,\s+\"isDynamicHtml\"\:',json_data,re.DOTALL)
if(t):
    print(t[0]+",")
else:
    t = re.findall(r'("authors":\s\[\{\"affiliation\"\:[\S\s]*)\,\s+\"pubLink\"\:',json_data,re.DOTALL)
    print(t[0]+",")



##########################CITATIONS##################################################
######################################################################################################################################
url = "http://ieeexplore.ieee.org/document/6740844/citations"
browser = webdriver.PhantomJS();
browser.get(url)
WebDriverWait(browser,20)
wait = WebDriverWait(browser,15)
citations_present = True



######################################################################################################################################
#First task is to check if the citations are present in the document. If they aren't then their is no use of going ahead.
try:
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="LayoutWrapper"]/div[5]/div[3]/div/section[2]/div[2]/div[1]/div[2]/div[1]/button[1]')))
except:
    print("NO CITATIONS PRESENT")
    citations_present = False
#####################################################################################################################################################
if(citations_present):
    #Clicking the view all button  of the carousel view of the citations..so that the first set of citations load up.
    #TO DO:- CHANGE THE XPATH IF THE ADVERTISEMENTS IN THE PAGE ARE PRESENT FOR THE VIEW ALL BUTTON. OR FIND A BETTER METHOD
    try:
        element = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="6740844"]/div/div[4]/div/div[2]/a[13]')))
    except:
        print ("The internet connection is slow. Please try after some time. If it persists check the script.")
        exit()

    view_button = browser.find_element_by_xpath('//*[@id="6740844"]/div/div[4]/div/div[2]/a[13]')
    view_button.click()

    ################################################################################################

    #The page is now loaded with the first set of citations. Get the page source

    page_source = browser.page_source
    soup = BeautifulSoup(page_source,'html.parser')


    #The class of both the ieee citations and non ieee citatioin are same so we first will get the number of citation and use that numbers
    #segregate them inot IEEE and OTHER PUBLICATONS

    #There are two cases. 1)There are both ieee citations and others and 2)Either ieee or other
    #So store the length of the array. The length of array is either 1 or 2. If it is 1 it first checks if it is ieee citations if not it goes to except
    # If 2 is the length then in the second loop it checks for other citations
    num_citations = soup.find_all('h2',{'class':'document-ft-section-header ng-binding'})
    num_ieee_citations = 0;
    num_non_ieee_citations = 0;
    length = len(num_citations)
    for x in range(0,length):
        try:
            temp = re.findall(r'.*IEEE\s\(\d+\)',str(num_citations[x].text))
            temp = temp[0]
            num_ieee_citations = re.findall(r'\d+',temp)
            num_ieee_citations = int(num_ieee_citations[0])
            num_non_ieee_citations = int(0)

        except:
            temp = re.findall(r'.*Other.*',str(num_citations[x].text))
            temp = temp[0]
            num_non_ieee_citations =  re.findall(r'\d+',temp)
            num_non_ieee_citations = int(num_non_ieee_citations[0])
            if(num_ieee_citations == 0):
                num_ieee_citations = int(0)

    #Clicking the "View All" button associated to both ieee citation and non ieee_citations to get the complete list of citations.
    #While loop is used to make infinite loops in python

    ################################################################################################

    #To get all the citations of ieee
    while True:
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#anchor-paper-citations-ieee > div.load-more-container > button > span')))
            view_button = browser.find_element_by_css_selector('#anchor-paper-citations-ieee > div.load-more-container > button > span')
            view_button.click()
            continue
        except:
            break

    #To get all the citations of non ieee
    while True:
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#anchor-paper-citations-nonieee > div.load-more-container > button > span')))
            view_button = browser.find_element_by_css_selector('#anchor-paper-citations-nonieee > div.load-more-container > button > span')
            view_button.click()
            continue
        except:
            break

    #Page_source is now loaded with all the citaions.

    page_source = browser.page_source
    soup = BeautifulSoup(page_source,"html.parser")
    file_object = open("page_source_full_citations.txt","w")
    file_object.write(str(soup))
    file_object.close()
    #print(soup)

    #############################################################################################################################

    ''''''
    --> lxml module is used so that i can get the data using XPATH of the element. BeautifulSoup doesn't allow XPATH.
    -->Two ways here get the data :-
        1)Beautiful soup and use re to extract the data and sort them into categories.
         it but then it would lead to a problem handling errors of such long strings.
        2)Use both lxml and bs4. lxml to get the normal data and bs4 to get the extra info such as pp,year,issn and stuff.

    ''''''



    #Page_source is now loaded with all the citaions.
    text = open("/home/theprophet/Atom/Scibase/page_source_full_citations.txt")
    text = str(text.read())

    soup = BeautifulSoup(text,'html.parser')
    citations_extra = soup.find_all("div",{"class":"description ng-binding"})

    #####Using LXML######
    tree = html.fromstring(text)

    ####PUTTING THEM IN JSON format
    y = 0 #needed to select the appropriate value from the soup object.
    print('[')
    print('{"ieee-citations":[')
    for x in range(2,num_ieee_citations+2):#num_citations+2
        ieee_citations_tag = '#anchor-paper-citations-ieee > div:nth-child(' + str(x) + ') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'
        ieee_citations = tree.cssselect(ieee_citations_tag)[0].text

        ##########Authors###########

        try:
            ieee_citations_authors = re.findall(r'([A-Za-z\s\.\-]+)\,\s',ieee_citations,re.DOTALL)
            error_catch = ieee_citations_authors[len(ieee_citations_authors)-1]#CAtching the error when no authors are present. CAN BE IMPROVED
            print('{"authors":[')
            for z in range(0,len(ieee_citations_authors)-1):
                print('"'+str(ieee_citations_authors[z])+'",')
            #Printing the final author with appropriate tags
            print('"'+str(ieee_citations_authors[len(ieee_citations_authors)-1])+'"],')

        except:
            print('{"authors":["none"],')
        ########################CiTATION ARTICLE NAME####################################
        #There are cases when the article name is not PRESENT
        try:
            ieee_citations_article_name = re.findall(r'\"(.+)\"',ieee_citations,re.DOTALL)
            print('"article name":"'+str(ieee_citations_article_name[0])+'",')
        except:
            print('"Article Name":"none",')

        ############################Journal ############################
        try:
            ieee_citations_journal_cssselector = '#anchor-paper-citations-ieee > div:nth-child(' + str(x) +') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > em:nth-child(1)'
            ieee_citations_journal_tag = tree.cssselect(ieee_citations_journal_cssselector)[0]
            print('"Journal Name":"'+str(ieee_citations_journal_tag.text)+'",')
        except:
            print('"Journal Name":"none",')



        ######Extra Info#####################
        ieee_citations_extra_info = citations_extra[y].text#This will help us getting the extra info
        y = y+1

        #We stored all the soup data into ieee_citations_extra which is a list. We are looping through that list.


        #############EXTRA INFO OF IEEE CITATIONS(PP.,YEAR,ISSN)#####################
        try:
            ieee_citations_vol = re.findall(r'vol\.\s([0-9A-Za-z\-]+)',ieee_citations_extra_info,re.DOTALL)
            print('"vol.": "'+str(ieee_citations_vol[0])+'",')
        except:
            print('"vol":"none",')

        try:
            ieee_citations_pp = re.findall(r'pp\.\s([A-Za-z0-9\-]+)',ieee_citations_extra_info,re.DOTALL)
            print('"pp.": "'+str(ieee_citations_pp[0])+'",')
        except:
            print('"pp.":"none",')

        try:
            ieee_citations_year = re.findall(r'\,\s([0-9]+)',ieee_citations_extra_info,re.DOTALL)
            print('"Year": "'+ str(ieee_citations_year[0])+'",')
        except:
            print('"Year":"none",')

        try:
            ieee_citations_issn = re.findall(r'ISSN\s([0-9\-A-Z]+)',ieee_citations_extra_info,re.DOTALL)
            print('"ISSN": "'+ str(ieee_citations_issn[0])+'",')
        except:
            print('"ISSN":"none",')

        try:
            ieee_citations_isbn = re.findall(r'ISBN\s([0-9\-A-Z]+)',ieee_citations_extra_info,re.DOTALL)
            print('"ISBN": "'+ str(ieee_citations_isbn[0])+'"')
        except:
            print('"ISBN":"none"')
        ####Ending tags for json format
        ##The last isbn should not have a ',' after '}'
        if( x <= num_ieee_citations): # x<= num_ieee_citations
            print("},")
        else:
            print("}")
    print(']},')

    #######NON IEEE CITATIONS#########
    y=num_ieee_citations #setting the value to make the soup object point the non_ieee_citations
    print('{"non-ieee-citations":[')
    #print("---------------------Other Citations---------------")
    for x in range(2,num_non_ieee_citations+2):#num_citations+2
        non_ieee_citations_tag = '#anchor-paper-citations-nonieee > div:nth-child(' + str(x) + ') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'
        non_ieee_citations = tree.cssselect(non_ieee_citations_tag)[0].text

        ##########Authors###########
        #Getting the individual authors
        try:
            non_ieee_citations_authors = re.findall(r'([A-Za-z\s\.\-]+)\,\s',non_ieee_citations,re.DOTALL)
            error_catch = non_ieee_citations_authors[len(non_ieee_citations_authors)-1]#CAtching the error when no authors are present. CAN BE IMPROVED
            print('{"authors":[')
            for z in range(0,len(non_ieee_citations_authors)-1):
                print('"'+str(non_ieee_citations_authors[z])+'",')
            #Printing the final author with appropriate tags
            print('"'+str(non_ieee_citations_authors[len(non_ieee_citations_authors)-1])+'"],')

        except:
            print('{"authors":["none"],')
        ########################CiTATION ARTICLE NAME####################################
        #There are cases when the article name is not PRESENT
        try:
            non_ieee_citations_article_name = re.findall(r'\"(.+)\"',non_ieee_citations,re.DOTALL)
            print('"article name":"'+str(non_ieee_citations_article_name[0])+'",')
        except:
            print('"Article Name":"none",')

        ############################Journal ############################
        try:
            non_ieee_citations_journal_cssselector = '#anchor-paper-citations-nonieee > div:nth-child(' + str(x) +') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > em:nth-child(1)'
            non_ieee_citations_journal_tag = tree.cssselect(non_ieee_citations_journal_cssselector)[0]
            print('"Journal Name":"'+str(non_ieee_citations_journal_tag.text)+'",')
        except:
            print('"Journal Name":"none",')



        ######Extra Info#####################
        non_ieee_citations_extra_info = citations_extra[y].text#This will help us getting the extra info
        y=y+1
        #We stored all the soup data into ieee_citations_extra which is a list. We are looping through that list.


        #############EXTRA INFO OF NON_IEEE CITATIONS(PP.,YEAR,ISSN)#####################
        try:
            non_ieee_citations_vol = re.findall(r'vol\.\s([0-9A-Za-z\-]+)',non_ieee_citations_extra_info,re.DOTALL)
            print('"vol.": "'+str(non_ieee_citations_vol[0])+'",')
        except:
            print('"vol":"none",')

        try:
            non_ieee_citations_pp = re.findall(r'pp\.\s([A-Za-z0-9\-]+)',non_ieee_citations_extra_info,re.DOTALL)
            print('"pp.": "'+str(non_ieee_citations_pp[0])+'",')
        except:
            print('"pp.":"none",')

        try:
            non_ieee_citations_year = re.findall(r'\,\s([0-9]+)',non_ieee_citations_extra_info,re.DOTALL)
            print('"Year": "'+ str(non_ieee_citations_year[0])+'",')
        except:
            print('"Year":"none",')

        try:
            non_ieee_citations_issn = re.findall(r'ISSN\s([0-9\-A-Z]+)',non_ieee_citations_extra_info,re.DOTALL)
            print('"ISSN": "'+ str(non_ieee_citations_issn[0])+'",')
        except:
            print('"ISSN":"none",')

        try:
            non_ieee_citations_isbn = re.findall(r'ISBN\s([0-9\-A-Z]+)',non_ieee_citations_extra_info,re.DOTALL)
            print('"ISBN": "'+ str(non_ieee_citations_isbn[0])+'"')
        except:
            print('"ISBN":"none"')
        ####Ending tags for json format
        if( x <= num_non_ieee_citations): # x<= num_non_ieee_citations
            print("},")
        else:
            print("}")
    print(']}]}')
'''''''''
