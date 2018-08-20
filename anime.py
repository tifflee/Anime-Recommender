# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 13:29:36 2018

@author: janes
"""
import urllib.request
from bs4 import BeautifulSoup

def getAnimeRecs(anime, recNum):
    animeSearch = anime.replace(" ", "%20")
    baseUrl = "https://myanimelist.net/search/all?q=" + animeSearch
    html1 = urllib.request.urlopen(baseUrl)
    soup = BeautifulSoup(html1, 'html.parser')
    animeUrl = soup.find("article").findAll("a")[0]['href'] + "/userrecs"
    html2 = urllib.request.urlopen(animeUrl)
    soup = BeautifulSoup(html2, 'html.parser')
    currentRec = soup.findAll("tr")[0].findAll("tr")[4+recNum]
    imageUrl = currentRec.findAll("div")[0].find("img")["data-src"].replace("/r/50x70", "")
    animeTitle = currentRec.findAll("div")[3].text.strip().replace(" addpermalink", "")
    animeDesc = currentRec.findAll("div")[4].text.strip().replace("\r", " ").split("\xa0")[0]
    return (imageUrl, animeTitle, animeDesc)
