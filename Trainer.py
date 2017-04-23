import numbers
import statistics

__author__ = 'julius'


class Trainer:
    '''
    Returns a feature vector, which can then be used by a classifier to classify a post
    '''

    def __init__(self):
        self.db = ""
        self.post_list = ""

    # generate mean for each concrete possible value
    def generate_concrete_feature_means(self, post_list, to_be_used_features):
        result = {}
        possible_features = set()

        for feature in to_be_used_features:
            result[feature] = dict()
            print(feature)

            # first get possible values for the feature
            for post in post_list.values():
                if isinstance(post.original_features[feature], list):
                    for element in post.original_features[feature]:
                        result[feature][element] = list()
                else:
                    result[feature][post.original_features[feature]] = list()

            # compute list of nLikes
            for post in post_list.values():
                if isinstance(post.original_features[feature], list):
                    for element in post.original_features[feature]:
                        result[feature][element].append(post.nLikes)
                else:
                    result[feature][post.original_features[feature]].append(post.nLikes)

            for distribution in result[feature].keys():
                # print("\t" + str(sorted(result[feature][distribution])))

                mean = statistics.mean(result[feature][distribution])

                if (len(result[feature][distribution]) > 1):
                    sample_standard_deviation = statistics.stdev(result[feature][distribution], mean)
                else:
                    sample_standard_deviation = result[feature][distribution][0]

                result[feature][distribution] = mean

                # print('\tmean: ' + "{:10.2f}".format(result[feature][distribution]) + '\tvari: ' + "{:10.2f}".format(
                # sample_standard_deviation) + '\t\t\t' + str(distribution))

                # remove feature from every post, that has an nLike that is more far away than one sample standard deviation :-)
                for post in post_list.values():
                    if isinstance(post.features[feature], list):
                        if distribution in post.features[feature] and (
                                        post.nLikes < (mean - sample_standard_deviation) or post.nLikes > (
                                            mean + sample_standard_deviation)):
                            # print("removing " + feature + str(distribution) + " from " + str(post.nLikes))
                            post.features[feature].remove(distribution)
                    else:
                        if post.features[feature] == distribution and (
                                        post.nLikes < (mean - sample_standard_deviation) or post.nLikes > (
                                            mean + sample_standard_deviation)):
                            # print("removing " + feature + str(distribution) + " from " + str(post b b.nLikes))
                            post.features[feature] = 'unknown'

        return result


    # old function for naivePrediction
    def get_possible_features(self):
        possible_features = set()
        for post in self.post_list.values():
            for key in post.features:
                possible_features.add(key)

        return possible_features

    # deprecated function for naive Prediction
    def get_feature_vector(self):
        result = {}

        for feature in self.get_possible_features():
            result[feature] = {}
            # print(feature)

            # first get possible values for the feature
            set_of_values = set()
            for post in self.post_list.values():

                if feature in post.features:
                    set_of_values.add(post.features[feature])
                else:
                    set_of_values.add('')

            # prepare list of nLikes
            distribution_dictionary = {}
            for value in set_of_values:
                distribution_dictionary[value] = []

            # compute list of nLikes
            for post in self.post_list.values():
                if feature in post.features:
                    distribution_dictionary[(post.features[feature])].append(post.nLikes)
                else:
                    distribution_dictionary[''].append(post.nLikes)

            for distribution in distribution_dictionary:
                average_nLikes = 0
                for nLike in distribution_dictionary[distribution]:
                    if isinstance(nLike, numbers.Number):
                        average_nLikes += nLike
                average_nLikes = average_nLikes / len(distribution_dictionary[distribution])
                result[feature][distribution] = average_nLikes
                # print('\t' + "{:10.2f}".format(average_nLikes) + ' \t\t\t' + str(distribution))
        return result