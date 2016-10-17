import requests
import string
from bs4 import BeautifulSoup as BS
from time import sleep

def getSoup(url):
    html = requests.get(url)
    soup = BS(html.text, "html.parser")
    sleep(0.25)
    return soup

def getFacultyPages(base_url):
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
    info = soup.find('div', {'class': 'entry-content'})
    return info

def getTitleAndEducation(info):
    info_refined = info.findAll('h4')
    titles = info_refined[0].text
    title_and_education = titles.split('PhD')
    title = title_and_education[0]
    title = ''.join(x for x in title if x not in string.punctuation)
    education = 'PhD'+title_and_education[1]
    education = education.split('Curriculum')[0]
    return title, education

def getFacultyName(soup):
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
