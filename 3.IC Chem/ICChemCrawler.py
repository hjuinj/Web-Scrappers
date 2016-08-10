# -*- coding: utf-8 -*-"""
"""
    #TODOs:
        - R mongodb Done
        - small letter captial letters considerations
"c:\Program Files\MongoDB\Server\3.0\bin\mongod.exe" --dbpath e:mongodb\data\
"""
import requests
from bs4 import BeautifulSoup
import codecs
import csv
import re
from pymongo import MongoClient

headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
def getHTML(url):
    r = requests.get(url)
    if r.ok:
        return r.content
    else: return None



def getStaffs(page):
    div_people_list = page.find('ul', attrs={'class' : 'people list'})
    a_s = div_people_list.find_all('a', attrs={'class' : "name-link"})

    # Title bar for the csv files
    staffList = []
    for a in a_s:
        name = a.find('span', attrs={'class' : 'person-name'}).get_text()
        title = a.find('span', attrs={'class' : 'job-title'}).get_text()
        link = a['href']
        staffList.append({
            'name' : name,
            'title' : title,
            'link' : link,
        })
    return staffList

""""
#print outcome
outcome = [["name", "title", "link"]]
for a in a_s:
    name = a.find('span', attrs={'class' : 'person-name'}).get_text()
    title = a.find('span', attrs={'class' : 'job-title'}).get_text()
    link = a['href']
    outcome.append([ name, title, link ])
with codecs.open("./staffList.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(outcome)
"""

def nextPage(page):
    tmp = page.find('a', attrs = {'class' : 'icon next'})
    if tmp:
        return tmp['href']
    else:
        return False

# get the list of paper on a page
def getPapers(page):
    papers = page.find_all('div', attrs = {'class' : 'publication'})
    return papers

# map key value pair of a paper given the div object
# fromWho shows which author's page the paper is from
def registerPaper(paper, fromWho):
    string = paper.p.get_text()

    # remove spaces and split the long stirng into different fields (e.g. author, year, title etc)
    strings = string.strip().split(',')
    fields = [s.strip() for s in strings]
    try:
        year_index = [i for i, item in enumerate(fields) if re.search('^[1|2][0-9]{3}$', item)][0]
    except IndexError:
        paperObj = {
            'from' : fromWho,
            'author(s)' : [author.upper() for author in fields[ : -1]],
            'title' : fields[-1],
            'publication-type' : paper.find('span', attrs = {'class' : 'publication-type'}).get_text(),
        }
        return paperObj

    # remove potential et al. suffix after the last author
    fields[year_index - 1] = fields[year_index - 1].replace('et al.', '' )

    num_citations = paper.find('span', attrs = {'class' : 'publication-citations'})
    if num_citations:
        num_citations = int(num_citations.get_text().split(':')[1])
    else:
        num_citations = 0

    paperObj = {
            'from' : fromWho,
        'author(s)' : [author.upper() for author in fields[ : year_index]],
        'year' : fields[year_index], # using it as category so doesn't need to be type integer
        'title' : fields[year_index + 1],
        'publication-type' : paper.find('span', attrs = {'class' : 'publication-type'}).get_text(),
        'num_citations' : num_citations,
    }
    try:
        paperObj['journal'] = fields[year_index + 2].upper()
        paperObj['others'] = fields[year_index + 3 : ]
    except IndexError:
        pass

    return paperObj

def main():
    # Database prep
    client = MongoClient()
    db = client.ICchem
    db.literatures.drop()
    lit = db.literatures

    # Get all staffs that has their own page
    HOST = "https://www.imperial.ac.uk"
    staffPage = HOST + "/chemistry/about/contacts/all-staff/"
    html = getHTML(staffPage)
    soup = BeautifulSoup(html,'html.parser')
    staffList = getStaffs(soup)

    # Obtain papers for each staff
    for staff in staffList:
        print staff['name']
        start = HOST + staff['link'] + '/publications.html'
        url = start
        while True:
            try:
                html = getHTML(url)
            except requests.ConnectionError:
                break
            soup = BeautifulSoup(html, 'html.parser')
            for i in getPapers(soup):
                #print registerPaper(i)['author(s)']
                #TODO Storage
                lit.insert_one(registerPaper(i, staff['name']))

            url = nextPage(soup)
            if not url : break
            url = start + url

main()
if __name__ == 'main':
    # 5 min
    main()
