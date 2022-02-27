#!/usr/bin/env python3
from bs4 import BeautifulSoup
import html
import requests
from pathlib import Path
import time

feed_template = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>TITLE</title>
    <itunes:owner>
        <itunes:email>OWNER</itunes:email>
    </itunes:owner>
    <itunes:author>AUTHOR</itunes:author>
    <description>DESCRIPTION</description>
    <itunes:image href="IMAGE_LINK"/>
    <language>en-us</language>
    <link>LINK</link>
    ITEMS  </channel>
</rss>"""

item_template = """    <item>
      <title>TITLE</title>
      <description>DESCRIPTION</description>
      <enclosure url="FILE_URL"
                 type="FILE_TYPE" length="FILE_LENGTH"/>
      <itunes:duration>DURATION</itunes:duration>
      <guid isPermaLink="false">GUID</guid>
    </item>
"""

urls = ["https://oyc.yale.edu/african-american-studies/afam-162", "https://oyc.yale.edu/american-studies/amst-246", "https://oyc.yale.edu/astronomy/astr-160", "https://oyc.yale.edu/biomedical-engineering/beng-100", "https://oyc.yale.edu/chemistry/chem-125a", "https://oyc.yale.edu/chemistry/chem-125b", "https://oyc.yale.edu/classics/clcv-205", "https://oyc.yale.edu/ecology-and-evolutionary-biology/eeb-122", "https://oyc.yale.edu/economics/econ-252-08", "https://oyc.yale.edu/economics/econ-252", "https://oyc.yale.edu/economics/econ-251", "https://oyc.yale.edu/economics/econ-159", "https://oyc.yale.edu/english/engl-300", "https://oyc.yale.edu/english/engl-220", "https://oyc.yale.edu/english/engl-310", "https://oyc.yale.edu/english/engl-291", "https://oyc.yale.edu/environmental-studies/evst-255", "https://oyc.yale.edu/geology-and-geophysics/gg-140", "https://oyc.yale.edu/history/hist-116", "https://oyc.yale.edu/history/hist-119", "https://oyc.yale.edu/history/hist-210", "https://oyc.yale.edu/history/hist-202", "https://oyc.yale.edu/history/hist-234", "https://oyc.yale.edu/history/hist-251", "https://oyc.yale.edu/history/hist-276", "https://oyc.yale.edu/history-of-art/hsar-252", "https://oyc.yale.edu/italian-language-and-literature/ital-310", "https://oyc.yale.edu/molecular-cellular-and-developmental-biology/mcdb-150", "https://oyc.yale.edu/philosophy/phil-181", "https://oyc.yale.edu/death/phil-176", "https://oyc.yale.edu/physics/phys-200", "https://oyc.yale.edu/physics/phys-201", "https://oyc.yale.edu/political-science/plsc-270", "https://oyc.yale.edu/political-science/plsc-114", "https://oyc.yale.edu/introduction-psychology/psyc-110", "https://oyc.yale.edu/psychology/psyc-123", "https://oyc.yale.edu/religious-studies/rlst-152", "https://oyc.yale.edu/religious-studies/rlst-145", "https://oyc.yale.edu/sociology/socy-151", "https://oyc.yale.edu/spanish-and-portuguese/span-300"]


def strip(string):
    to_strip = "\r\n "
    while string[0] in to_strip:
        string = string[1:]
    while string[-1] in to_strip:
        string = string[:-1]
    return string

def session_to_item(session_url):
    print("Fetching session " + session_url)
    s = requests.get(session_url)
    session_soup = BeautifulSoup(s.text, 'html.parser')
    title = session_soup.find(class_='session-title').string.replace(' - ', '')
    description = str(session_soup.find(class_='node-session').p)
    url = session_soup.find('td', class_="views-field-field-audio--file").a['href']
    session_number = session_soup.find(class_="session-number").string
    item = item_template
    item = item.replace("TITLE", html.escape(title))
    item = item.replace("DESCRIPTION", html.escape(description))
    item = item.replace("FILE_URL", html.escape(url))
    item = item.replace("FILE_TYPE", "audio/mp3")
    item = item.replace("FILE_LENGTH", "-1")
    item = item.replace("DURATION", "3600")
    item = item.replace("GUID", html.escape(session_number))
    return item

def course_to_rss(course_url):
    c = requests.get(course_url)
    course_soup = BeautifulSoup(c.text, 'html.parser')
    title = strip(course_soup.find(id='page-title').string)
    professor = course_soup.find(class_="views-field-field-about-the-professor").div.b.string.replace("About ", "")
    description = str(course_soup.find(class_="view-syllabus-course").div.div.find(class_="views-field-body").div.p)
    image_link = course_soup.find(class_="views-field-field-course-header-image").div.img['src']
    course = feed_template
    course = course.replace("TITLE", html.escape(title))
    course = course.replace("OWNER", "Yale Open Courses")
    course = course.replace("AUTHOR", html.escape(professor))
    course = course.replace("DESCRIPTION", html.escape(description))
    course = course.replace("IMAGE_LINK", html.escape(image_link))
    course = course.replace("LINK", html.escape(course_url))
    sessions_table = course_soup.find(class_="views-table").tbody
    sessions = ""
    for session_soup in sessions_table:
        url = BeautifulSoup(str(session_soup), 'html.parser').find('a')
        if url == None:
            continue
        url = url['href']
        try:
            sessions += session_to_item('https://oyc.yale.edu' + url)
        except:
            print("Failed to fetch session " + url)
    course = course.replace("ITEMS", sessions)
    return course

if __name__ == "__main__":
    for url in urls:
        dest = "static/files/feeds/" + url.split("/")[-1] + ".xml"
        if Path(dest).is_file():
            continue
        print("Fetching " + url)
        podcast = course_to_rss(url)
        f = open(dest, "w")
        f.write(podcast)
        f.close()
        print("Written " + dest)
