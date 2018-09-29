import os
import re
import selenium
import requests
from bs4 import BeautifulSoup


def get_page_source(url):
    try:
        page_source = requests.get(url)
    except:
        try:
            page_source = requests.get(url)
        except:
            print("URL IS INVALID OR CHECK THE INTERNET CONNECTION")
    page_source = page_source.text
    return(page_source)


def get_path_home(base_path, Journal_name):
    home = "/home/theprophet/Scibase/"+str(Journal_name)+"/"
    os.makedirs(home, exist_ok=True)
    return(home)


def get_path_vol(home_path, vol_no):
    vol = home_path + "vol " + str(vol_no)+"/"
    os.makedirs(vol, exist_ok=True)
    return(vol)


def get_path_issue(vol_path, issue_no):
    issue = vol_path + "issue "+str(issue_no)
    os.makedirs(issue, exist_ok=True)
    return(issue)


def create_current_issue_dir(source, home_path, issue_url):
    soup = BeautifulSoup(source, "html.parser")
    issue_vol_info = soup.find("div", {"class": "breadcrumbs"}).text
    #issue_vol_info = current_issue_info.text
    vol = re.findall(r'Volume\s(\d+)', issue_vol_info, re.DOTALL)
    issue = re.findall(r'Issue\s(\d+)', issue_vol_info, re.DOTALL)
    complete_path = get_path(vol[0], issue[0], home_path)
    write_issue_links(issue_url, complete_path)


def get_path(vol, issue, home_path):

    volume_path = get_path_vol(home_path, vol)
    issue_path = get_path_issue(volume_path, issue)
    file_path = os.path.join(issue_path, issue)+'.txt'
    return(file_path)


def write_issue_links(issue_url, filePath):
    file_object = open(filePath, "w")
    full_url = "http://ieeexplore.ieee.org" + str(issue_url)
    file_object.write(full_url)


def get_issue(url):

    source = get_page_source(url)
    soup = BeautifulSoup(source, "html.parser")
    x = soup.find_all("div", {"class": "volumes"})
    y = (x[0].contents[1])

    # Setting the variables for the directory storage
    base_path = "/home/theprophet/Scibase/"
    home_path = get_path_home(base_path, "HELLO")
    create_current_issue_dir(source, home_path, url)

    soup = BeautifulSoup(str(y), "html.parser")
    # x stores the issue link
    for x in soup.find_all("li"):
        issue_vol_info = str(x.text)
        issue_url = x.contents[1].get('href')
        vol = re.findall(r'Vol\:\s(\d+)', issue_vol_info, re.DOTALL)
        issue = re.findall(r'Issue\:\s(\d+)', issue_vol_info, re.DOTALL)
        create_current_issue_dir(source, home_path, issue_url)
        complete_path = get_path(vol[0], issue[0], home_path)
        write_issue_links(issue_url, complete_path)


def main():
    url = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=6536343&punumber=6528086'
    get_issue(url)


if __name__ == "__main__":
    main()
