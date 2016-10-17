from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver # This code is necessary to pull from Javascript
driver = webdriver.PhantomJS()

def page_iterator(BASE_URL, NUMBER_OF_PAGES_TRUMP):
    for i in range(1, NUMBER_OF_PAGES_TRUMP + 1):
        url = BASE_URL + str(i)
        yield url
        i+=1

def get_page_content(url):
    driver.get(url)  # Get the webpage
    # Convert it to a BS object - "soup"
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def find_valid_links(soup):
    press_release_urls = []
    # FINDING AND STORING LINKS TO INDIVIDUAL PRESS RELEASES
    for link in soup.findAll('a', href=True):
        candidate_link = link['href']
        # two simple criteria for determining if this is a press release url
        if "press-release" in candidate_link:
            if len(candidate_link) > MIN_TRUMP_URL_LEN:
                press_release_urls.append(candidate_link)
    return press_release_urls

def process_press_releases(press_release_urls, VISITED_URLS):
    for pr_url in press_release_urls:
        if pr_url not in VISITED_URLS:
            time.sleep(1) # limit calls to 1 per second

            soup = get_page_content(pr_url)
            content = soup.find_all('p') #gets all objects with 'p' html tag
            paragraphs = []
            for c in content:
                c_text = c.getText()
                paragraphs.append(c_text)
            # we don't need the first or last 5 elements
            # so we slice them out (this is through trial and error)
            trimmed_paragraphs = paragraphs[1:-5]
            press_release_text = "".join(trimmed_paragraphs)

            # CREATING DICTIONARY
            press_release_dict = {
                "text": press_release_text,
                "url": pr_url,
                "author": "Trump",
            }
            VISITED_URLS.add(pr_url)
            yield press_release_dict

def write_to_json(press_release_dict):
            with open(OUTPUT_PATH, 'a') as f:
                # turns dict into valid json string on 1 line
                j = json.dumps(press_release_dict) + '\n'
                # writes j to file f
                f.write(j)

if __name__ == '__main__':

    # Website url
    BASE_URL = "https://www.donaldjtrump.com/press-releases/P"

    # Constants
    NUMBER_OF_PAGES_TRUMP = 1000

    # Min length of a valid press release url
    MIN_TRUMP_URL_LEN = 50

    # Where we save the data output
    OUTPUT_PATH = '../data/trump_website.json'

    # This set will contain all visited press release urls
    VISITED_URLS = set()

    pages = page_iterator(BASE_URL, NUMBER_OF_PAGES_TRUMP)
    for p in pages:
        soup = get_page_content(p)
        prs = find_valid_links(soup)
        processed_prs = process_press_releases(prs, VISITED_URLS)
        for pprs in processed_prs:
            print(pprs['text'])
            write_to_json(pprs)
