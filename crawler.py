import urllib.request
import re


def openUrlAndReturnContent(url):
    response = urllib.request.urlopen(url)
    return response.read().decode(response.headers.get_content_charset())

frontPage = openUrlAndReturnContent("http://reddit.com/")
#alle links zu unterseiten extrahieren
topicsPattern = re.compile('http://www.reddit.com/r/\w*/comments/\w*/\w*/')
for topicUrl in re.findall(topicsPattern, frontPage):
    print("Found: " + topicUrl)




