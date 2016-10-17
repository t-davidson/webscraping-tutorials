#Started April 18, 2016, last edit May 9, 2016
#CamDep-Stenograme.py

""" Scrapes and stores html of transcripts from Romanian Chamber of Deputies. """

import time
import random
import requests
import codecs
import json
import os
import re
import natsort
from bs4 import BeautifulSoup

def Scarpe():
    """ Scrapes the html of transcripts of Lower House sessions (LH only or joint meetings with Senate). """

    for x in range(1,7661):
        url = 'http://www.cdep.ro/pls/steno/steno2015.stenograma?ids=' + str(x) + '&idl=1'

        #for transparent research, tell sysadmin who I am
        headers = {'user-agent' : 'Mozilla 45.0 (Linux Mint 17); Radu Parvulescu/Cornell University/rap348@cornell.edu'}

        #stagger requests so we don't overload target site
        time.sleep(random.uniform(1,3))

        #get html text and transmit header
        html = requests.get(url, headers=headers).text

        #get date-time you retrieved document
        retrieved = time.time()
    
        #dump into dictionary
        data = {'number':x, 'html':html, 'retrieved':retrieved, 'url':url}

        #dump in file, line-delimited json
        out_file_name = str(x) + '.txt'
        with codecs.open(out_file_name, 'w', encoding='UTF8') as outfile:
            outfile.write(json.dumps(data))    
            outfile.write('\n')

        #tells me where I am
        print x

def ExtractSpeech():

    """ Extracts the speech and vital information from the html. 

    PreC: Reads line-delimited json .txt files in current folder. """

    #loop over html files in directory, in natural order
    for FILE in natsort.natsorted(os.listdir('.')):

        #tell me where I am                  
        print FILE

        if FILE.endswith('.txt'):
            with codecs.open(FILE, 'r', encoding='UTF8') as in_file:
                for line in in_file:
                    dictio = json.loads(line)
                    #take out HTML
                    html = dictio['html'] 
        
                    #this is how website indexes beginning and end of
                    #speeches. Extract speeches and get date of debate
                    speeches = re.findall(r'<!-- START=(.*?)<!-- END -->', html, re.DOTALL)
                    #ignore pages with no speeches, make year-month-day
                    #title of debate
                    if len(speeches) > 0:
                        date = re.findall(r'<title>(.*?)</title>', html, re.DOTALL)[0]
                        #joint sessions of lower & upper houses don't 
                        #give the date, for some strange reason
                        if 'din ' in date:
                            date = date.partition('din ')[2]
                            date = re.sub(r'\s+', ' ', date)
                            date = re.split(' ', date)  
                            date = date[2] + '-' + date[1] + '-' + date[0] 
                            #dump in files
                            out_file_name = 'debate'+ '_' + str(date) + '.txt'

                        else:
                            date = 'Joint Session, raw file ' + str(FILE)
                            #dump in files
                            out_file_name = 'debate'+ '_' + str(date)


                        with codecs.open(out_file_name, 'w', encoding='UTF8') as outfile:
                            outfile.write(date)
                            outfile.write('\n')

                            #iterate over speeches
                            for s in speeches:
                                text = s.partition('-->\n')[2]
                                soup = BeautifulSoup(text, 'lxml')
                                speech = soup.get_text()
                                outfile.write(speech)
          

if __name__ == '__main__':

    ExtractSpeech()

