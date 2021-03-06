## This script combines both extact_article_from issue.py and Extract_Issue_Links.py
import os
import bs4
import requests
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
from collections import OrderedDict
import time
import random
browser = webdriver.PhantomJS()

global browser
#Stores the url of all the links where the errors have occured
errors = []

##Gets the page source
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

##Gets the home path
def get_path_home(base_path,Journal_name):
    print("Creating a home path\n")
    home = "/home/theprophet/Scibase/"+str(Journal_name)+"/"
    os.makedirs(home,exist_ok=True)
    return(home)

## Gets Path work
def get_path_vol(home_path,vol_no):
    print("Creating folder vol "+str(vol_no))
    vol = home_path + "vol_"+ str(vol_no)+"/"
    os.makedirs(vol,exist_ok=True)
    return(vol)

##Gets Path Issue
def get_path_issue(vol_path,issue_no):
    print("Creating folder issue "+str(issue_no))
    issue = vol_path +"issue_"+str(issue_no)
    os.makedirs(issue,exist_ok=True)
    return(issue)

##Get the current Issue
def create_current_issue_dir(source,home_path,issue_url):
    print("Creating Current issue directory")
    soup = BeautifulSoup(source,"html.parser")
    issue_vol_info = soup.find("div",{"class":"breadcrumbs"}).text
    #issue_vol_info = current_issue_info.text
    vol = re.findall(r'Volume\s(\d+)',issue_vol_info,re.DOTALL)
    issue = re.findall(r'Issue\s(\d+)',issue_vol_info,re.DOTALL)
    issue_path = get_path(vol[0],issue[0],home_path)
    issue_file_path = os.path.join(issue_path,issue[0])+'.txt'
    print("Writing the issue url of vol "+ str(issue[0]))
    write_issue_links(issue_url,issue_file_path)

##Get Path
def get_path(vol,issue,home_path):

    volume_path = get_path_vol(home_path,vol)
    issue_path = get_path_issue(volume_path,issue)

    return(issue_path)

##
def write_issue_links(issue_url,filePath):
    file_object = open(filePath,"w")
    full_url = "http://ieeexplore.ieee.org" + str(issue_url)
    file_object.write(full_url)
    print("Issue url written into file")
    file_object.close()

##Gets the issue url and as well as pass the file_paths for storing the article_urls from a issue
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
    base_path = "/home/theprophet/Scibase/"
    home_path = get_path_home(base_path,"HELLO")
    create_current_issue_dir(source,home_path,url)

    ##This stores the path of each issue
    article_link_path = []
    issue_link_path=[]
    links=[]

    soup = BeautifulSoup(str(y),"html.parser")
    #'x' stores the issue link
    for x in soup.find_all("li"):
        issue_vol_info = str(x.text)
        issue_url = x.contents[1].get('href')
        vol = re.findall(r'Vol\:\s(\d+)',issue_vol_info,re.DOTALL)
        issue = re.findall(r'Issue\:\s(\d+)',issue_vol_info,re.DOTALL)
        issue_path = get_path(vol[0],issue[0],home_path)
        file_path = os.path.join(issue_path,issue[0])+'.txt'
        print("Writing the issue url of vol "+ str(issue[0]))
        write_issue_links(issue_url,file_path)
        print("\n")

        #This stores the path where the article links under a issue needs to be stored
        article_link_path.append(issue_path)
        #This has the path to the issue url file
        issue_link_path.append(file_path)


    print("Collected and stored Issue URL\n")
    links.append(article_link_path)
    links.append(issue_link_path)
    sleep2 = random.uniform(20.5,50.5)
    print("Sleepin for : " +str(sleep2))
    time.sleep(sleep2)

    return(links)

def get_number_pages_issue_url(issue_url):

    print("Getting the number of pages in issue_url:")
    source = (requests.get(issue_url)).text
    soup = BeautifulSoup(source,"html.parser")
    next_page  = soup.find("div",{"class":"pagination"})
    soup1 = BeautifulSoup(str(next_page),"html.parser")
    pages = 0
    for page_number in soup1.find_all("a"):
        pages+= 1
    pages-= 2

    return(pages)



def get_article_links(issue_url):
    global url
    article_link_text = ""
    pages = get_number_pages_issue_url(issue_url)
    print("pages:= " + str(pages))
    sleep3 = random.uniform(10.5,15.5)
    print("Sleeping for "+str(sleep3))
    time.sleep(sleep3)
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
                article_link_text+= str(article_link)+str("citations?anchor=anchor-paper-citations-ieee&ctx=citations")+"\n"
            except:
                continue
    #Retruns a all the article_links in a string format
    return(article_link_text)

##This gets the article_urls from the issue_page_url and stores them in a file
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
    for x in range(0,len(issue_link_path)):
        pointer = x
        print("pointer := "+ str(pointer) )
        article = article_link_path[x]
        issue = issue_link_path[x]

        article_path = str(article) + str("/article_url.txt")


        with open(issue,"r") as content_file:
            print("Reading Issue_url from "+ str(issue))
            issue_url = content_file.read()
            print("issue_url:= " + str(issue_url))
            article_links = get_article_links(issue_url)

        with open(article_path,"w+") as content_file:
            print("Writing the article_links at path "+ str(article_path)+"\n")
            content_file.write(article_links)
            print("--------------------------------")


        #print(issue_url+"\n")


################################################################


def get_response(url):
    print("Waiting for thr response from the url")
    global browser
    try:
        browser.get(url)
    except:
        print("Invalid URL")


def get_page_source_selenium(browser):
    page_source1 = browser.page_source
    return (page_source1)

def get_soup(browser):
    response = get_page_source_selenium(browser)
    soup = BeautifulSoup(response,'html.parser')
    return(soup)

def get_metadata(browser):
    print("Fetching the metadata from the page_sorce")
    str_soup = str(get_soup(browser))
    metadata = re.findall(r'global\.document\.metadata=(\{[\s\S]+\})\;',str_soup,re.DOTALL)
    metadata = json.dumps(json.loads(metadata[0],object_pairs_hook=OrderedDict))
    return(metadata)


#Store the data from the above function in a variable and pass it
def get_issn(json_data):
    print("Fetching the ISSN....")
    try:
        issn = re.findall(r'(\"issn\"\:[\s\S]+?\,)\s\"article',json_data,re.DOTALL)
        return(issn[0])
    except:
        issn = '"issn":"none",'
        return(issn)

##Abstract
def get_abstract(json_data):
    print("Fetching the Abstract....")
    try:
        abstract = re.findall(r'(\"abstract\"\:[\s\S]+?\.\"\,)\s',json_data,re.DOTALL)
        return(abstract[0])
    except:
        abstract = '"abstract":"null",'
        return(abstract)
##Metrics
def get_metrics(json_data):
    print("Fetching the Metrics....")
    try:
        metrics = re.findall(r'(\"metrics\"\:[\s\S]+?\}\,)\s\"',json_data,re.DOTALL)
        return(metrics[0])
    except:
        metrics = '"metrics":"null",'
        return(metrics)

##DOI
def get_doi(json_data):
    print("Fetching the D.O.I....")
    try:
        doi = re.findall(r'(\"doi\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(doi[0])
    except:
        doi = '"doi":"null",'
        return(doi)

##TITLE
def get_title(json_data):
    print("Fetching the Title....")
    try:
        title = re.findall(r'(\"title\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(title[0])
    except:
        title = '"title":"null",'
        return(title)

##Publication TITLE
def get_pubTitle(json_data):
    print("Fetching the PublicationTitle....")
    try:
        pubTitle = re.findall(r'(\"publicationTitle\"\:[\s\S]+?\"\,)\s\"',json_data,re.DOTALL)
        return(pubTitle[0])
    except:
        pubTitle = '"publicationTitle":"null",'
        return(pubTitle)

#Authors
def get_authors(json_data):
    print("Fetching the Authors....")
    try:
        authors = re.findall(r'(\"authors\"\:[\s\S]+?\,)\s\"issn',json_data,re.DOTALL)
        return(authors[0])
    except:
        authors = '"authors":"none",'
        return(authors)

#Checking if the citations are present or not
def check_citation_presence(metadata):
    print("Checking for the presence of citations")
    check = re.findall(r'\"citationCountPaper\"\:\s([0-9]+)\,\s\"',metadata,re.DOTALL)
    if(int(check[0]) > 0):
        return(True)
    else:
        return(False)



##Number of IEEE citations
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
        errors.append(link)
        return(0)
    except:
        return(0)


##Number of NON IEEE CITATIONS
def get_num_non_ieee_citations(citations,link):
    print("Fetching the number of NON-IEEE citations")
    try:
        temp = re.findall(r'\sOther[\s\S]+\s\(\d+\)',citations,re.DOTALL)
        num_non_ieee_citations = re.findall(r'\d+',temp[0])
        num_non_ieee_citations = int(num_non_ieee_citations[0])
        return(num_non_ieee_citations )
    except IndexError:
        errors.append(link)
        return(0)
    except:
        return(0)

##LOAD IEEE Citations
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


##############################################     FUNCTIONS FOR THE ARTICLE INFO  #############################
#THE BELOW FUNCTIONS ARE FOR CITATIONS
##Get the content of each citation paragraph
def get_citation_tag(x,name,tree):

    citations_tag = '#anchor-paper-citations-'+str(name)+' > div:nth-child(' + str(x) + ') > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)'
    citations = tree.cssselect(citations_tag)[0].text
    return(citations)

##EXTRA CITATION SOUP OBJECT. GETS THE PP.,VOL, etc.
#All the citations are under the class "description ng-binding". Here we are getting the soup list of all the citations.
def extra_citat_info_tag(soup):#Pass the soup of the completely loaded page with cit.
    citations_extra =  soup.find_all("div",{"class":"description ng-binding"})
    return(citations_extra)

##CITATION Authors
def get_citation_authors(citation_tag):
    print("Fetching the Citation authors....")
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
    print("Fetching the Citation Article name....")
    try:
        citations_article_name = re.findall(r'\"(.+)\"',citation_tag,re.DOTALL)
        article_name = '"article name":"'+str(citations_article_name[0])+'",'
        return(article_name)
    except:
        article_name = '"Article Name":"none",'
        return(article_name)

##JOURNAL NAME
def get_citation_journal(x,name,tree):
    print("Fetching the Citation Journal Name....")
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
    print("Fetching the Citation volume no....")
    try:
        citations_vol = re.findall(r'vol\.\s([0-9A-Za-z\-]+)',citation,re.DOTALL)
        citation_vol = '"vol.": "'+str(citations_vol[0])+'",'
        return(citation_vol)
    except:
        citation_vol = '"vol":"none",'
        return(citation_vol)

## CITATION PP.
def get_citation_pp(citation):
    print("Fetching the citation pp. ....")
    try:
        citations_pp = re.findall(r'pp\.\s([A-Za-z0-9\-]+)',citation,re.DOTALL)
        citation_pp = '"pp.": "'+str(citations_pp[0])+'",'
        return(citation_pp)
    except:
        citation_pp = '"pp.":"none",'
        return(citation_pp)

## CITATION YEAR
def get_citation_year(citation):
    print("Fetching the Citation year....")
    try:
        citations_year = re.findall(r'\,\s([0-9]+)',citation,re.DOTALL)
        citation_year = '"Year": "'+str(citations_year[0])+'",'
        return(citation_year)
    except:
        citation_year = '"Year":"none",'
        return(citation_year)

##CITATION ISSN
def get_citation_issn(citation):
    print("Fetching the Citationi ISSN ....")
    try:
        citations_issn = re.findall(r'ISSN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_issn = '"ISSN": "'+str(citations_issn[0])+'",'
        return(citation_issn)
    except:
        citation_issn= '"ISSN":"none",'
        return(citation_issn)

##CITATION ISBN
def get_citation_isbn(citation):
    print("Fetching the Citation ISBN ....")
    try:
        citations_isbn = re.findall(r'ISBN\s([0-9\-A-Z]+)',citation,re.DOTALL)
        citation_isbn = '"ISBN": "'+str(citations_isbn[0])+'"'
        return(citation_isbn)
    except:
        citation_isbn = '"ISBN":"none"'
        return(citation_isbn)
##################################################################
def get_citation(num_citations,name,tree,soup):#soup of the completely loaded page
#The citations are first scraped using bs4 using extra_citat_info_tag. Once we get the list of all the posibile values of citations from the soup object, we loop through them.
#The get_citation_tag is used to get the particular division where the x'th citation is present using css selector
    print("Creating the json_data for the citations ....")
    global citationCount
    if (name == "nonieee"):
        citationCount = citationCount
        print(citationCount)
    else:
        citationCount = 0


    citation_json = '{"'+str(name)+'-citations":['
    citations_extra_info = extra_citat_info_tag(soup)
    for x in range(2,num_citations+2):
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

        if( x <= num_citations): # x<= num_ieee_citations
            citation_json+= "},"
        else:
            citation_json+= "}"

    if(name == "ieee"):
        citation_json+= "]},"
    else:
        citation_json+= "]}"

    return(citation_json)



#GET THE JSON Data
def get_json_data(metadata,browser,link):
    global citationCount

    print("Starting the process to get the information about the article in  json_data")
    json_data="{"
    json_data+= get_issn(metadata) + get_metrics(metadata) +get_doi(metadata)
    json_data+= get_title(metadata)+get_pubTitle(metadata)+get_abstract(metadata)+ get_authors(metadata)

    json_data+='"citations":['

    x = False
    x = check_citation_presence(metadata)

    if ( x == False):
        print("Citation NOT Found")
        json_data+= "null]}"
        return(json_data)
    else:

            print("Citations Found")
            soup1 = get_soup(browser)
            num_citations = soup1.find_all('h2',{'class':'document-ft-section-header ng-binding'})
            length = len(num_citations) - 1
            num_ieee_citations = get_num_ieee_citations(str(num_citations[0].text),link)
            num_non_ieee_citations = get_num_non_ieee_citations(str(num_citations[length].text),link)

            load_citation(browser,"ieee")
            load_citation(browser,"nonieee")


            #Wait for the page to load  with all citations then grab the page source
            WebDriverWait(browser,30)

            source = get_page_source_selenium(browser)
            soup = get_soup(browser)

            #Declare the tree for lxml
            tree = html.fromstring(str(source))

            json_data+= get_citation(num_ieee_citations,"ieee",tree,soup)
            print("IEEE citation data retrieved")
            print(citationCount)
            json_data+= get_citation(num_non_ieee_citations,"nonieee",tree,soup)
            print("NON-IEEE citation data retrieved")
            citationCount = 0

            #Final tags of Json Data
            json_data+= "]}"
            return(json_data)


def get_article_info(path_list,browser):
    article_pointer = 0
    article_json_path = path_list
    article_links = []
    browser_count = 0
    for x in range(0,len(article_json_path)):
        article_count = 0
        article_pointer = x
        article_link_path = str(article_json_path[x]) + str("/article_url.txt")
        print("Article_pointer:= "+str(article_pointer))

        with open(article_link_path,"r") as content_file:
            print("Reading the article_url from file := " + str(article_link_path))
            article_links = content_file.read().splitlines()

        for links in article_links:
            if(browser_count == 0):
                print("Browser: FireFox" )
                browser = webdriver.Firefox()
                browser_count = 1
            else:
                print("Browser : PhantomJS")
                browser = webdriver.PhantomJS()
                browser_count = 0


            print("------------------------------------------------------------------------------")
            print("\nStarting the process to get the json_data from :- "+str(links))
            print("Reading url from:= " + str(article_link_path))
            json_data = get_article_json_data(links,browser)
            article_count+= 1
            json_data_path = str(article_json_path[x])+"/" + str(article_count) + str(".json")
            #json_data_path = str(article_json_path)+"/" +str(article_count) + str(".json")
            print("Path of storage : " + str(json_data_path))

            with open(json_data_path,"w+") as data:
                data.write(json_data)

            ##Make the script Sleep
            browser.quit()
            sleep1 = random.uniform(1.5,2.5)
            sleep1 = sleep1*50.3
            print("Sleeping for : " + str(sleep1))
            time.sleep(sleep1)
            print("I am AWAKE!!")




def get_article_json_data(link,browser):

    get_response(link,browser)
    print("Browser will wait for 30ms for the page to load")
    WebDriverWait(browser,10)
    #Get the JSON DATA to extract the first half
    metadata= get_metadata(browser)
    #Get the json data
    json_data = get_json_data(metadata,browser,link)
    if(json_data == str(0)):
        json_data = get_json_data(metadata,browser,link)
        return(json_data)
    else:
        #ADD A CONDITION HERE. THIS HAPPENS WHEN THERE IS INDEX ERROR
        return(json_data)

def store_directory_path(path):
    dir_path = str(path[0]) + str("/directory_path.txt")
    with open(dir_path,"w+") as f:
        f.write(json.dumps(path))
'''
def read_directory_path():
    path = str("/home/theprophet/Scibase1/HELLO/vol_49/issue_1/directory_path")
    source  = open()
'''
def print_errors():
    global errors
    print("Below are the links whoose json data is not proper")
    for x in errors:
        print(x+"\n")

def main(url):
    global citationCount
    citationCount = 0
    #INITIALIZE THE BROWSER
    print("Starting get_issue()...")
    path_list = get_issue(url)
    store_directory_path(path_list[0])
    #path_list[0] contains the path where the article_links are present
    #path_list[1] contains the path of the file which consists of issue_url
    print("\nStarting store_article_url()...\n")
    store_article_url(path_list)
    time.sleep(100)
    print("---------------------------- GETTING THE JSON DATA --------------------------------------------------")
    print("\nStarting the function get_article_info...\n")
    get_article_info(path_list[0],browser)
    print("------------------Errors--------------------")
    print_errors()


if __name__ == "__main__":
    #url of the most recent issue of a journal'
    global url
    url = 'http://ieeexplore.ieee.org/xpl/tocresult.jsp?isnumber=6536343&punumber=6528086'
    main(url)
