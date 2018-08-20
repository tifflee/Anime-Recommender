import os
import json
import requests
from bs4 import BeautifulSoup

######################
# helper functions
######################
##recursively look/return for an item in dict given key
def find_item(obj, key):
    item = None
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = find_item(v, key)
            if item is not None:
                return item

##recursivley check for items in a dict given key
def keys_exist(obj, keys):
    for key in keys:
        if find_item(obj, key) is None:
            return(False)
    return(True)

##send attach (pic prolly) via messenger to id
def send_attachment(send_id, attach_url):
    params  = {"access_token": os.environ['access_token']}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {
                        "id": send_id
                        },
                        "message": {
                            "attachment": {
                                "type": "image", 
                                "payload": {
                                    "url": attach_url, "is_reusable": True
                                }
                            }
                        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

##send txt via messenger to id
def send_message(send_id, msg_txt):
    params  = {"access_token": os.environ['access_token']}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {"id": send_id},
                       "message": {"text": msg_txt}})
                       
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
        
def getAnimeRecs(anime, recNum):
    animeSearch = anime.replace(" ", "%20")
    baseUrl = "https://myanimelist.net/search/all?q=" + animeSearch
    html1 = requests.urlopen(baseUrl)
    soup = BeautifulSoup(html1, 'html.parser')
    animeUrl = soup.find("article").findAll("a")[0]['href'] + "/userrecs"
    html2 = requests.urlopen(animeUrl)
    soup = BeautifulSoup(html2, 'html.parser')
    currentRec = soup.findAll("tr")[0].findAll("tr")[4+recNum]
    imageUrl = currentRec.findAll("div")[0].find("img")["data-src"].replace("/r/50x70", "")
    animeTitle = currentRec.findAll("div")[3].text.strip().replace(" addpermalink", "")
    animeDesc = currentRec.findAll("div")[4].text.strip().replace("\r", " ").split("\xa0")[0]
    return (imageUrl, animeTitle, animeDesc)

#-----------------------------------------------------------

def lambda_handler(event, context):
    #debug
    print("event:" )
    print(event)
    
    #handle webhook challenge
    if keys_exist(event, ["params","querystring","hub.verify_token","hub.challenge"]):
        v_token   = str(find_item(event,'hub.verify_token'))
        challenge = int(find_item(event,'hub.challenge'))
        if (os.environ['verify_token'] == v_token):
            return(challenge)
            
    #handle messaging events
    if keys_exist(event, ['body-json','entry']):
        event_entry0 = event['body-json']['entry'][0]
        if keys_exist(event_entry0, ['messaging']):
            messaging_event = event_entry0['messaging'][0]
            msg_txt   = messaging_event['message']['text']
            sender_id = messaging_event['sender']['id']
            send_message(sender_id, "Getting Recommendations...")
            animeRec = getAnimeRecs(msg_txt, 0)
            send_attachment(sender_id, animeRec[0])
            send_message(sender_id, animeRec[1])
            send_message(sender_id, animeRec[2])
    
    return(None)
