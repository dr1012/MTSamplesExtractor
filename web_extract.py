###################################################################################
######  This code is based on the following source:
####### https://realpython.com/python-web-scraping-practical-introduction/
####### Author: Colin Okeefe
####### Date: Jan 23, 2018
#####################################################################################


##### To launch the code, in the command line write:  python web_extract.py text_folder_name
##### Where text_folder_name is the folder into which you want the text to be written to

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import sys


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None



def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def extract_sample(url, output_directory):
    """
    Extracts the html from the webpage, finds the div tag with the id = 'sampletext' and performs text splitting to remove any other html elements.
    It then writes the reamining text to a new txt file in a directory specified by output_directory.
    """
    raw_html =  simple_get(url)  
    try:
        html = BeautifulSoup(raw_html, 'html.parser')  
    except TypeError:
        print('THE ERROR OCCURED AT THIS URL: '+ str(url))
        print('RAW HTML: ')
        print('\n')
        print(raw_html)
        

    for p in html.select('div'):
        try:
            if p['id'] == 'sampletext':
                text = p.get_text()
        except KeyError:
            continue

    #https://stackoverflow.com/questions/904746/how-to-remove-all-characters-after-a-specific-character-in-python

    text = text.split('Sample Type', 1)[-1]
    text = text.split('Keywords', 1)[0]
    text = text.replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')
    text = text.replace('(Medical Transcription Sample Report)', '')
    text = text.rstrip()
    

    title = text.split('Sample Name: ')[-1]
    title = title.split('Description: ')[0]
    text = text.split(title)[-1]
    title = title.replace ('\n', '')
    title = title.replace(' ', '_')
    title = title.replace('-','')
    title = title.replace('/','_')
    

    
    file_name = output_directory + '/' +  title + '.txt'

    

    text_file = open(file_name, "w+")
    text_file.write(text)
    text_file.close()


#https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text
def retrieve_top_layer_urls(url):
    """
    Retrieves the url of the subsections without the MTSamples website.

    """
    links =[]
    raw_html =  simple_get(url)  
    html = BeautifulSoup(raw_html, 'html.parser')  
    for link in html.find_all('a'):
        links.append(link.get('href'))
    links = [x for x in links if x is not None] 
    links =  [x for x in links if x.startswith('/site/pages/browse')]
    del links[:40]  
    
    links =  [ ('http://mtsamples.com' + x) for x in links ]

    return links




    
def retrieve_bottom_layer_urls(url):
    """
    Retrieves the url of the inidividual sample pages from the subsection pages. This has some redudancy as a url may appear multiple times on page. In the end it 
    doesn't matter because the extract_sample() function will overwrite any already existing documents with the same name. 
    """
    links =[]
    raw_html =  simple_get(url)  
    html = BeautifulSoup(raw_html, 'html.parser')  
    for link in html.find_all('a'):
        links.append(link.get('href'))
    links = [x for x in links if x is not None]

   
    links =  [x for x in links if x.startswith('/site/pages/sample.asp')]
    
    links =  [ ('http://mtsamples.com' + x) for x in links ]

   
    return links



def mt_samples_extractor():
    """
    This function loops through all the available url links that link to inidividual samples and then calls the extract_sample() function to extract the text from the sample pages.
    """
    top_level_links = retrieve_top_layer_urls('http://mtsamples.com/')

    for x in top_level_links:
        bottom_level_links = retrieve_bottom_layer_urls(x)
        for y in bottom_level_links:
            extract_sample(y, sys.argv[1])


mt_samples_extractor()