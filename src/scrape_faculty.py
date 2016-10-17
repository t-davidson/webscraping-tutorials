import requests
import string
from bs4 import BeautifulSoup as BS
from time import sleep

def getSoup(url):
    """Input: A valid url.
    Gets the HTML associated with a url and
    converts it to a BeautifulSoup object.
    Then sleeps for a short time.
    Returns: A BeautifulSoup object."""
    html = requests.get(url)
    soup = BS(html.content, "html.parser")
    sleep(0.25)
    return soup

def getFacultyPages(base_url):
    """Input: The base url for the
    Cornell sociology faculty site.
    Finds all valid links to faculty profiles
    then visits each link and gets the soup
    object.
    Returns: An iterator of faculty profiles
    soup objects"""
    soup = getSoup(base_url)
    links = soup.findAll('a', href=True)
    profiles = []
    for l in links:
        if "/people/faculty/" in l['href']:
            profiles.append(l['href'])
    profiles = [x for x in profiles if x.endswith('faculty/') == False]
    profiles = set(profiles)
    for p in profiles:
        yield getSoup(p)

def getFacultyInfo(soup):
    """Input: A soup object related to a faculty webpage.
    Finds the section of the page with the class
    entry-content, based on inspection of relevant pages,
    Returns: A soup object with the relevant content."""
    info = soup.find('div', {'class': 'entry-content'})
    return info

def getTitleAndEducation(info):
    """Input: A soup object output by getFacultyInfo()
    that contains information on a faculty member.
    This function parses this object to get the title
    and education for a given faculty member.
    Reutrns: A tuple containing title and education
    strings."""
    info_refined = info.findAll('h4')
    titles = info_refined[0].text
    title_and_education = titles.split('PhD')
    title = title_and_education[0]
    title = ''.join(x for x in title if x not in string.punctuation)
    education = 'PhD'+title_and_education[1]
    education = education.split('Curriculum')[0]
    return title, education

def getFacultyName(soup):
    """Input: The soup object for a faculty page.
    Gets the faculty members name as it appears on the page.
    Returns: The name as a string."""
    name_info = soup.findAll('h1', {'class':'entry-title'})
    name = name_info[0].text
    return name

if __name__ == '__main__':
    URL = "http://www.soc.cornell.edu/people/faculty/"
    faculty_pages= getFacultyPages(URL)
    faculty_info = {}
    for fp in faculty_pages:
        name = getFacultyName(fp)
        print("Getting information for ", name)
        try:
            info = getFacultyInfo(fp)
            title, education = getTitleAndEducation(info)
            print("Information obtained for ", name)
        except:
            print("Failed to get info from page for ", name)
            title, education = None, None
        faculty_info[name] = {'title':title, 'education':education}
    print(faculty_info)
