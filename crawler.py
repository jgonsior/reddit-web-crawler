import requests
import re


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

userSet = set()
topicSet = set()

topicsPattern = re.compile('http://www.reddit.com/r/\w*/comments/\w*/\w*/')
for topicUrl in re.findall(topicsPattern, frontPage):
    topic = Topic(topicUrl)
    topicSet.add(topic)

    print("Found: " + topicUrl)

    topicHtml = openUrlAndReturnContent(topicUrl)

    userPattern = re.compile('http://www.reddit.com/user/(\w+)')
    for userName in re.findall(userPattern, topicHtml):
        user = User(userName)
        userSet.add(user)
        topic.users.add(user)
        user.commentedTopics.add(topic)
        #print("\tuser: " + userName)

for user in userSet :
    print("user: " + user.name)
    user.printTopics()
