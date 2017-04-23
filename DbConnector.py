__author__ = 'julius'
import sqlite3
import json
import numbers
import datetime
import re

import dateutil.parser

from User import User
from Post import Post


class DbConnector:
    """ Class that encapsulates all the database connection """

    def __init__(self):
        self.locale_connection = sqlite3.connect('fbmining.db')
        self.remote_connection = 'hui' '''psycopg2.connect(database="", user="",
                                                  password="",
                                                  host="",
                                                  port=)'''

        self.locale_cursor = self.locale_connection.cursor()

    ''' self.remote_connection = psycopg2.connect(database="", user="",
                                               password="",
                                               host="",
                                               port=)'''

    ''' self.attributesList = ["id", "fb_id", "name", "first_name", "middle_name", "last_name", "gender", "locale",
                            "username", "link", "website", "locations", "bio", "quotes", "relationship", "family",
                            "age"]'''

    '''
    Fetches newly found users from the database and saves them locally
    If there are some features that has already been calculated, then they are added too
    '''


    def fetch_new_remote_data(self):
        # fetches new ones from the database
        remote_cursor = self.remote_connection.cursor()
        remote_cursor.execute(
            "SELECT p.id, p.fb_id, p.content, u.id, u.fb_id, u.url, u.name, i.info, (SELECT count(*) FROM friends f WHERE f.user_id = u.id) as freunde FROM posts p JOIN users u ON p.poster_id = u.id JOIN profile_data i ON i.user_id = u.id WHERE char_length(((content->'ownContent')->'text')::TEXT) > 3;")
        post_list = self.get_posts()
        user_list = self.get_users()

        for data in remote_cursor.fetchall():
            post = Post()
            post.id = data[0]

            # test if post already exists
            if self.is_post_in_local_database(post) == False and not post.id in post_list:
                post_list[post.id] = post

                post.fb_id = data[1]
                post.content = data[2]
                if 'nLikes' in post.content['meta']:
                    post.nLikes = post.content['meta']['nLikes']
                    if not post.nLikes.isdigit():
                        del post_list[post.id]
                        continue

                if 'nComments' in post.content['meta']:
                    post.nComments = int(post.content['meta']['nComments'])
                if 'posted_at_original' in post.content['meta']:
                    # parse time!

                    timeOfPublication = post.content['meta']['posted_at_original']
                    posted_at = dateutil.parser.parse(post.content['meta']['accessed_at'])
                    # print(posted_at)

                    time = 0
                    month = 0
                    year = 0
                    day = 0
                    '''forbidden_posts = ['November 2013','3. März','8. Januar', 'September 2012', '4. September 2005', 'Juni 2012', '11. August', 'September 2011', 'September 2006', '7. Januar']
                    end = False
                    for forbidden in forbidden_posts:
                        if forbidden == timeOfPublication:
                            del post_list[post.id]
                            end = True
                            break
                    if end:
                        continue'''
                    if "Gestern" == timeOfPublication:
                        del post_list[post.id]
                        post.timeOfPublication = "hui"
                        continue
                    if "Minuten" in timeOfPublication:
                        published_at = posted_at + datetime.timedelta(
                            minutes=int(timeOfPublication[:timeOfPublication.find("Minuten")]))
                    elif "Std." in timeOfPublication:
                        published_at = posted_at + datetime.timedelta(
                            minutes=int(timeOfPublication[:timeOfPublication.find("Std.")]))
                    elif "Gestern" in timeOfPublication:
                        '''print(timeOfPublication)
                        print(timeOfPublication[-2:])
                        print(timeOfPublication[-5:-3])'''
                        published_at = datetime.datetime(year=posted_at.year, month=posted_at.month,
                                                         day=posted_at.day - 1, minute=int(timeOfPublication[-2:]),
                                                         hour=int(timeOfPublication[-5:-3]))
                    elif "Gerade eben" in timeOfPublication:
                        published_at = posted_at
                    else:
                        if "um" not in timeOfPublication:
                            del post_list[post.id]
                            post.timeOfPublication = "hui"
                            continue
                        # parse 28. Dezember 2014 um 13:56
                        month_list = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
                                      "September", "Oktober", "November", "Dezember"]
                        for m in month_list:
                            if m in timeOfPublication:
                                month = month_list.index(m) + 1

                                if "rn" in timeOfPublication:
                                    print(timeOfPublication)

                                day = int(timeOfPublication[:(timeOfPublication.find(m) - 2)])
                                time = str(timeOfPublication[-5:])
                                if timeOfPublication[(timeOfPublication.find(m) + len(m) + 1):-9] != '':
                                    year = timeOfPublication[(timeOfPublication.find(m) + len(m) + 1):-9]
                                else:
                                    year = posted_at.year
                                break
                        published_at = datetime.datetime(year=int(year), month=month, day=day, minute=int(time[3:]),
                                                         hour=int(time[:2]))

                        first_date = datetime.datetime(year=2009, month=12, day=28)

                        delta = (published_at - first_date).days
                post.timeOfPublication = published_at
                post.daysSinceBegin = delta

                # test if user already exists
                user = User()
                user.id = data[3]

                if str(user.id) in user_list.keys():
                    user = user_list.get(str(data[3]))
                else:
                    user_list[str(user.id)] = user
                    user.fb_id = data[4]
                    user.url = data[5]
                    user.name = data[6]
                    user.info = data[7]
                    user.friends = data[8]
                    self.save_user(user)

                post.author = user

                # generate possible post features
                post.original_features = {}

                # posted_at
                if post.timeOfPublication != "hui":
                    post.original_features['daysSinceBegin'] = post.daysSinceBegin

                # visibility
                if 'visibility' in post.content['meta']:
                    post.original_features['visibility'] = post.content['meta']['visibility']
                else:
                    post.original_features['visibility'] = 'unknown'

                # number of friends
                post.original_features['friends'] = post.author.friends

                # mood
                if 'mood' in post.content['ownContent']:
                    if post.content['ownContent']['mood'] != '':
                        post.original_features['mood'] = post.content['ownContent']['mood']
                    else:
                        post.original_features['mood'] = ''
                else:
                    post.original_features['mood'] = 'unknown'

                # referenced people?
                if 'referencedPeople' in post.content['meta']:
                    post.original_features['referencedPeople'] = True
                else:
                    post.original_features['referencedPeople'] = False

                # inline references?
                if post.content['ownContent']['references']:
                    post.original_features['inlineReferences'] = True
                else:
                    post.original_features['inlineReferences'] = False

                # photo attached?
                if 'photos' in post.content:
                    post.original_features['photo'] = True
                else:
                    post.original_features['photo'] = False

                # smileys in text?
                post.original_features['smiley'] = post.content['ownContent']['html'].count(
                    '<img src="https://fbstatic-a.akamaihd.net')

                # link shared?
                post.original_features['link'] = post.content['ownContent']['text'].count('http://')

                # author
                post.original_features['author'] = str(post.author.id)

                # hashtag
                post.original_features['hashTag'] = post.content['ownContent']['text'].count("#")

                # living place
                post.original_features['locations'] = set()
                if 'locations' in post.author.info:
                    for location in post.author.info['locations']:
                        post.original_features['locations'].add(location['value'])
                post.original_features['locations'] = list(post.original_features['locations'])

                post.original_features['languages'] = set()

                post.original_features['gender'] = 'unknown'
                post.original_features['religion'] = 'unknown'
                post.original_features['politics'] = 'unknown'
                post.original_features['relationship'] = 'unknown'

                if 'attributes' in post.author.info:
                    for attribute in user.info['attributes']:
                        # gender
                        if attribute['name'] == 'gender':
                            post.original_features['gender'] = attribute['value']

                        # languages
                        elif attribute['name'] == 'languages':
                            langString = attribute['value'].replace(",", "").replace("und", "")
                            for language in langString.split(" "):
                                post.original_features['languages'].add(language)
                            if '' in post.original_features['languages']:
                                post.original_features['languages'].remove('')

                        # religion
                        elif attribute['name'] == 'religion':
                            post.original_features['religion'] = attribute['value']

                        # political view
                        elif attribute['name'] == 'politics':
                            post.original_features['politics'] = attribute['value']

                post.original_features['languages'] = list(post.original_features['languages'])
                # relationship
                if 'relationship' in post.author.info:
                    # special keywords:
                    relationshipKeyWords = ['In einer Beziehung', 'Single', "Es ist kompliziert", 'Verheiratet',
                                            'Verlobt', 'Verwitwet', 'Geschieden', "In einer Lebensgemeinschaft",
                                            'In einer offenen Beziehung', 'Getrennt', 'Lebenspartnerschaft']
                    for keyword in relationshipKeyWords:
                        if keyword in post.author.info['relationship']['relationship']:
                            post.original_features['relationship'] = keyword
                            break

                # company/jobs
                post.original_features['companies'] = set()
                if 'jobs' in post.author.info:
                    for job in post.author.info['jobs']:
                        post.original_features['companies'].add(job['company'])
                post.original_features['companies'] = list(post.original_features['companies'])

                # education
                post.original_features['education'] = set()
                if 'education' in post.author.info:
                    for education in post.author.info['education']:
                        post.original_features['education'].add(education['institution'])
                post.original_features['education'] = list(post.original_features['education'])

                # nComments
                post.original_features['nComments'] = post.nComments

                # countOfWords
                post.original_features['countOfWords'] = len(re.findall(r'\w+', post.content['ownContent']['text']))

            else:
                continue

        # normalize numerical features

        # find biggest value
        biggest_features = post_list[next(iter(post_list))].original_features
        for post in post_list.values():
            for feature in post.original_features:
                if isinstance(post.original_features[feature], numbers.Number) and not isinstance(
                        post.original_features[feature], bool):
                    if post.original_features[feature] > biggest_features[feature]:
                        biggest_features[feature] = post.original_features[feature]

        # normalize it now really
        for post in post_list.values():
            post.features = {}
            for feature in post.original_features:
                if isinstance(post.original_features[feature], numbers.Number) and not isinstance(
                        post.original_features[feature], bool):
                    post.features[feature] = post.original_features[feature] / biggest_features[feature]
                else:
                    post.features[feature] = post.original_features[feature]
            self.save_post(post)

        self.locale_connection.commit()


    '''
    test if user already exists
    '''


    def is_user_in_local_database(self, user):
        sqlIf = "SELECT count(*) FROM USERS WHERE id=" + user.id
        ifResult = self.locale_cursor.execute(sqlIf)
        ifResultResult = ifResult.fetchone()

        if (ifResultResult[0] >= 1):
            return True
        else:
            return False


    def is_post_in_local_database(self, post):
        sqlIf = "SELECT count(*) FROM posts WHERE id=" + str(post.id)
        ifResult = self.locale_cursor.execute(sqlIf)
        ifResultResult = ifResult.fetchone()

        if (ifResultResult[0] >= 1):
            return True
        else:
            return False


    '''
    If the user already exists in the database it isn't really saved at all
    '''


    def save_user(self, user):
        self.locale_cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?)",
                                   (user.id, user.fb_id, user.name, user.url, json.dumps(user.info), user.friends))


    def save_post(self, post):
        self.locale_cursor.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?)", (
            post.id, post.fb_id, json.dumps(post.content), post.author.id, post.nLikes, post.nComments,
            post.timeOfPublication, json.dumps(post.features), json.dumps(post.original_features), post.daysSinceBegin))


    def get_posts(self, limit, with_null):
        post_list = {}
        if not with_null:
            with_null = "WHERE nLikes IS NOT NULL"
        else:
            with_null = ""
        for row in self.locale_cursor.execute(
                                        "SELECT *, count(*) FROM posts  " + with_null + " GROUP BY features, timeOfPublication, nLikes, nComments, originalFeatures, content, id, fb_id LIMIT " + str(
                        limit)).fetchall():
            post = Post()
            post.id = row[0]
            post.fb_id = row[1]
            post.content = json.loads(row[2])
            post.author = self.get_user(row[3])
            if row[4]:
                post.nLikes = row[4]
            else:
                post.nLikes = 0
            post.nComments = row[5]
            post.timeOfPublication = row[6]
            post.features = json.loads(row[7])
            post.original_features = json.loads(row[8])
            post.daysSinceBegin = row[9]
            post.representativeFor = row[10]
            post_list[post.id] = post
        return post_list


    def get_user(self, id):
        row = self.locale_cursor.execute("SELECT * FROM users WHERE id ='" + id + "'").fetchone()
        user = User()
        user.id = row[0]
        user.fb_id = row[1]
        user.name = row[2]
        user.url = row[3]
        user.info = json.loads(row[4])
        user.friends = row[5]
        return user


    def get_users(self):
        userList = {}
        for row in self.locale_cursor.execute("SELECT * FROM users").fetchall():
            user = User()
            user.id = row[0]
            user.fb_id = row[1]
            user.name = row[2]
            user.url = row[3]
            user.info = json.loads(row[4])
            user.friends = row[5]
            userList[str(user.id)] = user
        return userList
