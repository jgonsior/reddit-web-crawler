import requests
import re


def openUrlAndReturnContent(url):
    response = requests.get(url)
    return response.text

frontPage = openUrlAndReturnContent("http://reddit.com/")

#alle links zu unterseiten extrahieren
topicsPattern = re.compile('http://www.reddit.com/r/\w*/comments/\w*/\w*/')
for topicUrl in re.findall(topicsPattern, frontPage):
    print("Found: " + topicUrl)

    #open topic
    topicHtml = openUrlAndReturnContent(topicUrl)

    userPattern = re.compile('http://www.reddit.com/user/\w*')
    for user in re.findall(userPattern, topicHtml):
        print("\tuser: " + user)

