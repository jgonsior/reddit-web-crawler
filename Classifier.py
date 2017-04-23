__author__ = 'julius'
import numbers


class Classifier:
    '''
    Takes a feature vector and and a post as input,
    then computes the difference between the ideal feature vector and the
    post features

    --> maybe there are some features that are leading to multiple feature vectors, f.e. if a=10 then b=true else if a=5 then b=false
    '''

    def classifyNaive(self, post, ideal_features):
        estimated_nLikes = 0

        # to_be_classified_post has feature a=5, then look what the training set says about a=5 and add this to estimated nLikes
        for feature in post.features:
            estimated_nLikes += ideal_features[feature][post.features[feature]]

        estimated_nLikes = estimated_nLikes / len(post.features)
        difference = abs(estimated_nLikes - post.nLikes)

        print("Naive Prediction: \t\t" + "{:5.2f}".format(estimated_nLikes) + "\t\t Real: " + str(
            post.nLikes) + "\t\t Difference: " + "{:5.2f}".format(difference))
        return difference

    def classifyKNearestNeighbours(self, unclassified_post, post_list, k, to_be_used_features, weights):
        nearest_posts = set()

        count_nearest_posts = 0
        biggest_nearest_distance = 0
        biggest_nearest_post = None

        for classified_post in post_list.values():
            if classified_post.fb_id == unclassified_post.fb_id:
                continue
            if not unclassified_post.id in classified_post.distances:
                # generate distance between unclassified_post and labeld posts

                distance = 0

                for unclassified_feature in to_be_used_features:
                    if unclassified_post.features[unclassified_feature] != 'unknown' or (
                                isinstance(unclassified_post.features[unclassified_feature], list) and len(
                                    unclassified_post.features[unclassified_feature]) < 0):
                        # leave one feature out :-)


                        # test if discrete or continous feature
                        # distance +1 means that they are not the same, distance +0 means that they are the same
                        if isinstance(classified_post.features[unclassified_feature],
                                      numbers.Number) and not isinstance(
                                classified_post.features[unclassified_feature], bool):
                            # continous
                            distance += abs(
                                classified_post.features[unclassified_feature] - unclassified_post.features[
                                    unclassified_feature]) * weights[unclassified_feature]
                        elif isinstance(classified_post.features[unclassified_feature], list):

                            a = set(classified_post.features[unclassified_feature])
                            b = set(unclassified_post.features[unclassified_feature])
                            merge = a & b
                            union = a.union(b)
                            # print("\tunclassified: " + str(list(b)))
                            # print("\tclassified: " + str(list(a)))
                            # print("====================================================================")
                            count_merge = len(merge)
                            count_union = len(union)
                            # print("\tclassi_len" + str(classified_len) + "\tunclassi_len" + str(unclassified_len) + "\tlongest_length" + str(longest_length) + "\t common:" + str(common_elements))
                            # print("\tmerge: " + str(list(merge)) + "\t union: " + str(list(union)) + "\t\t\t\t\t+=" + str(1-count_merge/count_union))
                            if count_union != 0:
                                distance += (1 - (count_merge / count_union)) * weights[unclassified_feature]

                        else:
                            # discrete
                            # print(unclassified_feature)

                            if classified_post.features[unclassified_feature] != unclassified_post.features[
                                unclassified_feature]:
                                # print("\tdifferent"+"\tunclassified: " + str(unclassified_post.features[unclassified_feature]) + "\t\t\t classified: " + str(classified_post.features[unclassified_feature]))
                                distance += weights[unclassified_feature]
                                # else:
                                # print("\tsame"+"\tunclassified: " + str(unclassified_post.features[unclassified_feature]) + "\t\t\t classified: " + str(classified_post.features[unclassified_feature]))
                    else:
                        distance += 1

                classified_post.distances[unclassified_post.id] = distance
                unclassified_post.distances[classified_post.id] = distance
            else:
                distance = classified_post.distances[unclassified_post.id]

            if count_nearest_posts == 0:
                biggest_nearest_post = classified_post
                biggest_nearest_distance = distance

            if count_nearest_posts <= k:
                if distance > biggest_nearest_distance:
                    biggest_nearest_distance = distance
                    biggest_nearest_post = classified_post
                nearest_posts.add(classified_post)
                count_nearest_posts += classified_post.representativeFor
                continue

            add = False

            # if classified_post.distance == 0:
            # print("aunclassified: \t" + str(unclassified_post.features))
            # print("anear: \t\t\t" + str(classified_post.features))
            # print("adist: \t" + str(classified_post.distance) + "\tnear: " + str(classified_post.nLikes) + "\t uncla:" + str(unclassified_post.nLikes))


            # test if post is nearer then the k posts in the nearest_posts set
            if distance < biggest_nearest_distance:
                add = True
                small_post = classified_post

            # remove the post with the biggest distance from set and add the new one
            if add:
                # add classified post
                nearest_posts.add(classified_post)
                count_nearest_posts += classified_post.representativeFor
                # remove old "biggest" post
                nearest_posts.remove(biggest_nearest_post)
                count_nearest_posts -= biggest_nearest_post.representativeFor
                #find new old "biggest" post

                for near_post in nearest_posts:
                    if near_post.distances[unclassified_post.id] >= small_post.distances[unclassified_post.id]:
                        biggest_nearest_post = near_post
                        biggest_nearest_distance = near_post.distances[unclassified_post.id]


        # generate estimated nLikes based on the mean of the k nearest neighbours
        estimated_nLikes = 0
        total_distance = 0

        for near_post in nearest_posts:
            # print("len:" + str(len(nearest_posts)) + "\t var:" + str(count_nearest_posts))
            # print(str(near_post.distances[unclassified_post.id]))
            if near_post.distances[unclassified_post.id] == 0:
                # print("unclassified: \t" + str(unclassified_post.features))
                # print("near: \t\t\t" + str(near_post.features))
                # print(                    "dist: \t" + str(distances[near_post.id]) + "\tnear: " + str(near_post.nLikes) + "\t uncla:" + str(                    unclassified_post.nLikes))
                near_post.distances[unclassified_post.id] = 0.000001
                unclassified_post.distances[near_post.id] = 0.000001

            estimated_nLikes += near_post.nLikes * near_post.representativeFor * (
                1 / near_post.distances[unclassified_post.id])
            total_distance += near_post.representativeFor * (1 / near_post.distances[unclassified_post.id])
        estimated_nLikes = estimated_nLikes / total_distance

        abs_difference = abs(estimated_nLikes - unclassified_post.nLikes)
        if unclassified_post.nLikes == 0:
            rel_difference = (estimated_nLikes + 1) / 1 * 100
        else:
            rel_difference = (estimated_nLikes / unclassified_post.nLikes) * 100
        '''print(str(k) + "-nearest neighbours: \t" + "{:5.2f}".format(estimated_nLikes) + "\t\t Real: " + str(
            unclassified_post.nLikes) + "\t\t Abs Difference: " + "{:5.2f}".format(
            abs_difference) + "\t\t Rel Difference: " + "{:5.2f}".format(rel_difference) + "%")'''
        return [rel_difference, estimated_nLikes]