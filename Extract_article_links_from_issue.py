# This script combines both extact_article_from issue.py and Extract_Issue_Links.py
import os
import re
import requests
from bs4 import BeautifulSoup


# Gets the page source
def get_page_source(url):
    print("Getting page source of "+str(url))
    try:
        page_source = requests.get(url)
    except:
        try:
            page_source = requests.get(url)
        except:
            print("URL IS INVALID OR CHECK THE INTERNET CONNECTION")
    page_source = page_source.text
    return(page_source)

# Gets the home path


def get_path_home(base_path, Journal_name):
    print("Creating a home path\n")
    home = "/home/theprophet/Scibase/"+str(Journal_name)+"/"
    os.makedirs(home, exist_ok=True)
    return(home)

# Gets Path work


def get_path_vol(home_path, vol_no):
    print("Creating folder vol "+str(vol_no))
    vol = home_path + "vol_" + str(vol_no)+"/"
    os.makedirs(vol, exist_ok=True)
    return(vol)

# Gets Path Issue


def get_path_issue(vol_path, issue_no):
    print("Creating folder issue "+str(issue_no))
    issue = vol_path + "issue_"+str(issue_no)
    os.makedirs(issue, exist_ok=True)
    return(issue)

# Get the current Issue


def create_current_issue_dir(source, home_path, issue_url):
    print("Creating Current issue directory")
    soup = BeautifulSoup(source, "html.parser")
    issue_vol_info = soup.find("div", {"class": "breadcrumbs"}).text
    #issue_vol_info = current_issue_info.text
    vol = re.findall(r'Volume\s(\d+)', issue_vol_info, re.DOTALL)
    issue = re.findall(r'Issue\s(\d+)', issue_vol_info, re.DOTALL)
    issue_path = get_path(vol[0], issue[0], home_path)
    issue_file_path = os.path.join(issue_path, issue[0])+'.txt'
    print("Writing the issue url of vol " + str(issue[0]))
    write_issue_links(issue_url, issue_file_path)

# Get Path


def get_path(vol, issue, home_path):

    volume_path = get_path_vol(home_path, vol)
    issue_path = get_path_issue(volume_path, issue)

    return(issue_path)

##


def write_issue_links(issue_url, filePath):
    file_object = open(filePath, "w")
    full_url = "http://ieeexplore.ieee.org" + str(issue_url)
    file_object.write(full_url)
    print("Issue url written into file")
    file_object.close()

# Gets the issue url and as well as pass the file_paths for storing the article_urls from a issue


def get_issue(url):
    # It goes to the journal url, gets the issue_urls from the source code and store them in the particular filePath
    # We first use re to get the vol_no and issue_no and use these to create the path where the url of that issue should be stored
    # Then using that path we store the issue_url in that file.
    # Now inorder to provide the path where the article link is stored we store the file_paths in a list and return it back to the main()
    source = get_page_source(url)
    print("Collecting the soup object for getting issue_urls")
    soup = BeautifulSoup(source, "html.parser")
    x = soup.find_all("div", {"class": "volumes"})
    y = (x[0].contents[1])

    # Setting the variables for the directory storage
    base_path = "/home/theprophet/Scibase/"
    home_path = get_path_home(base_path, "HELLO")
    create_current_issue_dir(source, home_path, url)

    # This stores the path of each issue
    article_link_path = []
    issue_link_path = []
    links = []

    soup = BeautifulSoup(str(y), "html.parser")
    # 'x' stores the issue link
    for x in soup.find_all("li"):
        issue_vol_info = str(x.text)
        issue_url = x.contents[1].get('href')
        vol = re.findall(r'Vol\:\s(\d+)', issue_vol_info, re.DOTALL)
        issue = re.findall(r'Issue\:\s(\d+)', issue_vol_info, re.DOTALL)
        issue_path = get_path(vol[0], issue[0], home_path)
        file_path = os.path.join(issue_path, issue[0])+'.txt'
        print("Writing the issue url of vol " + str(issue[0]))
        write_issue_links(issue_url, file_path)
        print("\n")

        # This stores the path where the article links under a issue needs to be stored
        article_link_path.append(issue_path)
        # This has the path to the issue url file
        issue_link_path.append(file_path)

    print("Collected and stored Issue URL\n")
    links.append(article_link_path)
    links.append(issue_link_path)

    return(links)


def get_number_pages_issue_url(issue_url):
    print("Getting the number of pages in issue_url:")
    source = (requests.get(issue_url)).text
    soup = BeautifulSoup(source, "html.parser")
    next_page = soup.find("div", {"class": "pagination"})
    soup1 = BeautifulSoup(str(next_page), "html.parser")
    pages = 0
    for page_number in soup1.find_all("a"):
        pages += 1
    pages -= 2

    return(pages)


def get_article_links(issue_url):
    global url
    article_link_text = ""
    pages = get_number_pages_issue_url(issue_url)
    print("pages:= " + str(pages))
    for x in range(1, pages+1):

        url1 = issue_url + "&pageNumber=" + str(x)
        source = get_page_source(url1)
        print("Getting all the article links from pageNumber: " + str(x))
        soup = BeautifulSoup(source, "html.parser")

        for link in soup.find_all("div", {"class": "txt"}):
            try:
                y = (link.contents[3]).contents[1]
                y = y.get("href")
                article_link = "http://ieeexplore.ieee.org" + str(y)
                article_link_text += str(article_link)+str(
                    "citations?anchor=anchor-paper-citations-ieee&ctx=citations")+"\n"
            except:
                continue
    # Retruns a all the article_links in a string format
    return(article_link_text)

# This gets the article_urls from the issue_page_url and stores them in a file


def store_article_url(path_list):
    '''
    article_link_path[] gives us the directory where the article_url.txt file will be stored.
    issue_link_path[] gives the path from where the url of the issue can be read from.
    '''
    pointer = 0
    article_link_path = path_list[0]
    issue_link_path = path_list[1]
    article_path = ""

    '''
    Lets store the value of x in the below loop in a variable so that if anywhere the script stops we can start from that script. Say the script
    stops at x=3. That means the script has stopped at the issue 3 of some volume. We can  find that path from article_link_path[x].
    So by changing the for loop range from range(x,len(issue_link_path)) we can continue from the part where we left off.
    '''
    for x in range(0, len(issue_link_path)):
        pointer = x
        print("x := " + str(pointer))
        article = article_link_path[x]
        issue = issue_link_path[x]

        article_path = str(article) + str("/article_url.txt")

        with open(issue, "r") as content_file:
            print("Reading Issue_url from " + str(issue))
            issue_url = content_file.read()
            print("issue_url:= "issue_url)
            article_links = get_article_links(issue_url)

        with open(article_path, "w+") as content_file:
            print("Writing the article_links at path " + str(article_path)+"\n")
            content_file.write(article_links)
            print("--------------------------------")

        # print(issue_url+"\n")


def main(url):

    print("Starting get_issue()...")

    path_list = get_issue(url)
    print("\nStarting store_article_url()...\n")
    store_article_url(path_list)


if __name__ == "__main__":
    # url of the most recent issue of a journal'
    global url
    url = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=6536343&punumber=6528086'
    main(url)
