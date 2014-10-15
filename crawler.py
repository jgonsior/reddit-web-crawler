import urllib.request
import re

response = urllib.request.urlopen('http://reddit.com/')
html = response.read().decode(response.headers.get_content_charset())

#alle links zu unterseiten extrahieren
topicsPattern = re.compile('http://www.reddit.com/r/\w*/comments/\w*/\w*/')
for topicUrl in re.findall(topicsPattern, html):
    print("Found: " + topicUrl)
