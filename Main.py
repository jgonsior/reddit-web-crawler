__author__ = 'julius'

import threading
from queue import Queue
import pprint
import numbers

import matplotlib.pyplot as pyplot
import matplotlib

import DbConnector
import Trainer
import Classifier


lock = threading.Lock()

k_list = [10]  # try different ones!, even 0
'''
weights = {"nComments": 3.19,
           "inlineReferences": 2.94,
           "relationship": 3.79,
           "visibility": 3.33,
           "daysSinceBegin": 5.53,
           "hashTag": 3.29,
           "education": 3.47,
           "religion": 3.70,
           "referencedPeople": 2.99,
           "photo": 3.01,
           "smiley": 3.17,
           "companies": 3.41,
           "friends": 4.70,
           "link": 3.07,
           "languages": 3.82,
           "locations": 3.37,
           "author": 3.85,
           "mood": 3.14,
           "politics": 3.69,
           "gender": 3.48}
'''
weights = {"nComments": 7,
           "inlineReferences": 2.94,
           "relationship": 3.79,
           "visibility": 3.33,
           "daysSinceBegin": 6,
           "hashTag": 3.29,
           "education": 8,
           "religion": 3.70,
           "referencedPeople": 2.99,
           "photo": 3.01,
           "smiley": 3.17,
           "companies": 9,
           "friends": 7,
           "link": 3.07,
           "languages": 8,
           "locations": 8,
           "author": 10,
           "mood": 6,
           "politics": 1,
           "gender": 3}


def generate_correlation():
    to_be_used_features = ['inlineReferences', 'photo', 'referencedPeople', 'daysSinceBegin', 'nComments', 'link',
                           'smiley', 'friends', 'hashTag', 'education']
    db = DbConnector.DbConnector()

    post_list = db.get_posts(1000, True)
    post_list.update(db.get_posts(2500, False))

    for feature in to_be_used_features:
        x = list()
        y = list()
        for post in post_list.values():
            x.append(post.original_features[feature])
            y.append(post.nLikes)

        pyplot.plot(x, y, '.')
        pyplot.yscale('symlog')
        pyplot.xscale('symlog')
        # pyplot.xticks(range(len(x)), x, rotation=45)
        #pyplot.yticks(range(len(y)), y, rotation=45)
        #pyplot.yscale('symlog')
        #pyplot.xscale('symlog')

        #ax = fig.add_subplot(111)

        #a = [i for i in range(250)]
        #line, = ax.plot(a, color='red')
        #ax.set_yticks(y)
        #ax.set_xticks(x)
        #ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        #ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        #ax.set_xticks(np.arange(0,150, 5))
        #ax.set_yticks(np.arange(0,150, 5))
        #pyplot.grid(True)
        #pyplot.set_size_inches(18.5,10.5)
        pyplot.savefig('0co' + feature + '.svg')
        pyplot.close()


def get_feature_count():
    to_be_used_features = ['gender']
    '''sorted(["nComments", "inlineReferences", "relationship", "visibility", "daysSinceBegin", "hashTag",
                           "education", "religion", "referencedPeople", "photo", "smiley", "companies", "friends",
                           "link",
                           "languages", "locations", "author", "mood", "politics", "gender"])'''
    db = DbConnector.DbConnector()

    post_list = db.get_posts(100000, True)

    count_features = dict()
    for feature in to_be_used_features:
        count_features[feature] = 0
    gender_set = set()
    for post in post_list.values():
        for feature in to_be_used_features:
            gender_set.add(post.features[feature])
            if isinstance(post.features[feature], list) and len(post.features[feature]) == 0:
                continue
            if post.features[feature] == 'unknown':
                continue
            if isinstance(post.features[feature], numbers.Number) and post.features[feature] == 0:
                continue
            count_features[feature] += 1

    for g in gender_set:
        print(g)
    for feature in to_be_used_features:
        print(str(count_features[feature]/23141*100) + "\t\t\t: " + feature  )




#generate_correlation()


max_w = 6
for weight in weights.keys():
    weights[weight] = (weights[weight]) ** 11 / max_w ** 11

pprint.pprint(weights)

to_be_used_features2 = ["nComments", "inlineReferences", "relationship", "visibility", "daysSinceBegin", "hashTag",
                        "education", "religion", "referencedPeople", "photo", "smiley", "companies", "friends", "link",
                        "languages", "locations", "author", "mood", "politics", "gender"]

features_without_bool = ['author', 'companies', 'daysSinceBegin', 'education', 'friends', 'languages', 'locations',
                         'mood', 'nComments', 'smiley']
features_lists = ['education', 'languages', 'locations', 'companies']
feature_int = ['daysSinceBegin', 'education', 'friends', 'hashTag', 'nComments', 'smiley', 'link']
feature_bool = ['inlineReferences', 'photo', 'referencedPeople']
feature_string = ['gender', 'author', 'mood', 'politics', 'relationship', 'religion', 'visibility']

for feature in to_be_used_features2:
    to_be_used_features = None
    to_be_used_features = [feature]

    db = None
    db = DbConnector.DbConnector()

    # db.fetch_new_remote_data()
    x = None
    y = None
    x = list()
    y = list()

    # to_be_used_features = ['gender']
    KNearestNeighboursDifference = None
    KNearestNeighboursDifference = {}

    count = None
    count = {}
    for k in k_list:
        KNearestNeighboursDifference[k] = 0
        count[k] = 0


    def match_post(post, post_list, classifier, k):
        result = threading.local()
        result.x_y = classifier.classifyKNearestNeighbours(post, post_list, k, to_be_used_features, weights)
        result.y = result.x_y[0]
        result.x = result.x_y[1]
        with lock:
            x.append(post.nLikes)
            y.append(result.x)
            if result.y > 100:
                KNearestNeighboursDifference[k] += (result.y / 100) * post.representativeFor
            else:
                if result.y == 0:
                    KNearestNeighboursDifference[k] += 0 * post.representativeFor
                else:
                    KNearestNeighboursDifference[k] += (100 / result.y) * post.representativeFor
            count[k] += post.representativeFor
            if count[k] % 10 == 0:
                print(count[k])
                print(str(k) + "\tKNearestNeighboursDifference:\t" + str(
                    KNearestNeighboursDifference[k] / count[k]))


    def worker():
        while True:
            item = q.get()
            match_post(item[0], post_list, classifier, item[1])
            q.task_done()


    trainer = Trainer.Trainer()

    classifier = Classifier.Classifier()

    naiveDifference = 0

    post_list = db.get_posts(1000, True)
    post_list.update(db.get_posts(2500, False))

    trainer.generate_concrete_feature_means(post_list, to_be_used_features)

    q = Queue()

    for i in range(4):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for i in range(1):
        for post in post_list.values():
            for k in k_list:
                q.put((post, k))

                #match_post(post, post_list, classifier, k)

    q.join()

    #print("naiveDifference:\t\t\t\t" + str(naiveDifference))
    for k in k_list:
        print(count[k])
        print(str(k) + "KNearestNeighboursDifference:\t" + str(KNearestNeighboursDifference[k] / len(post_list)))

        fig = pyplot.figure(33)
        pyplot.plot(x, y, '.')
        pyplot.yscale('symlog')
        pyplot.xscale('symlog')

        ax = fig.add_subplot(111)

        a = [i for i in range(250)]
        line, = ax.plot(a, color='red')
        ticks = [0, 1, 2, 3, 4, 6, 8, 10, 14, 19, 27, 39, 55, 77, 100, 150, 250]
        ax.set_yticks(ticks)
        ax.set_xticks(ticks)
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        #ax.set_xticks(np.arange(0,150, 5))
        #ax.set_yticks(np.arange(0,150, 5))
        pyplot.grid(True)
        #pyplot.show()
        pyplot.savefig(feature + str(KNearestNeighboursDifference[k] / len(post_list)) + '.svg', bbox_inches='tight')
        pyplot.close()