import requests
import re
from bs4 import BeautifulSoup

"""i
Dictionary mit userName(String) als Key und user object als Values
---"---- für topic

--> nix ist doppelt vorhanden!!
"""

class Topic:
    def __init__(self, name):
        self.name = name
        self.users = set()


class User:
    def __init__(self, name):
        self.name = name
        self.commentedTopics = set()
        self.createdTopics = set()

    def printTopics(self):
        for topic in self.commentedTopics:
            print("\ttopic: " + topic.name)

def openUrlAndReturnContent(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"}
    response = requests.get(url, headers=headers)
    return response.text

frontPage = openUrlAndReturnContent("http://reddit.com/")

#key: userName (String)
#values: userObject (User)
userDict = {}
topicDict = {}

topicsPattern = re.compile('http://www.reddit.com/r/\w*/comments/\w*/\w*/')

for topicUrl in re.findall(topicsPattern, frontPage):
    if topicUrl not in topicDict:
        topic = Topic(topicUrl)
        topicDict[topicUrl] = topic
    else:
        topic = topicDict[topicUrl]

    print("Found: " + topicUrl)

    topicHtml = openUrlAndReturnContent(topicUrl)
    
    #remove sidebar with moderators from topicHtml
    topicSoup = BeautifulSoup(topicHtml)

    sidebar = topicSoup.find_all(attrs={"class": "sidecontentbox"})
    sidebar[0].replace_with("")

for tag in soup.find_all(re.compile("t")):
    print(tag.name)



    userPattern = re.compile('http://www.reddit.com/user/(\w+)')
    for userName in re.findall(userPattern, str(topicSoup)):
        if userName not in userDict:
            user = User(userName)
            userDict[userName] = user
        else:
            user = userDict[userName]
        
        topic.users.add(user)
        user.commentedTopics.add(topic)
        print("\tuser: " + userName)

for userName in userDict.keys() :
    print("user: " + userName)
    userDict[userName].printTopics()
