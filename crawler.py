import requests
import re
"""
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
    response = requests.get(url)
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

    userPattern = re.compile('http://www.reddit.com/user/(\w+)')
    for userName in re.findall(userPattern, topicHtml):
        if userName not in userDict:
            user = User(userName)
            userDict[userName] = user
        else:
            user = userDict[userName]
        
        topic.users.add(user)
        user.commentedTopics.add(topic)
        #print("\tuser: " + userName)

for userName in userDict.keys() :
    print("user: " + userName)
    userDict[userName].printTopics()
