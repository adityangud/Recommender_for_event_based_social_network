from preprocessing import *
import argparse
from partition import *
from content.content_recommender import ContentRecommender
from temporal.time_recommender import TimeRecommender
from location.location_recommender import LocationRecommender
from group_frequency.grp_freq_recommender import GrpFreqRecommender
from hybrid.learning_to_rank import LearningToRank
import datetime
import time

train_data_interval = ((364 / 2) * 24 * 60 * 60)

def content_classifier(training_repo, test_repo, timestamp, simscores, test_members):
    #Wrapper for content classification.
    #call train and test for all member and
    #events and print the results

    training_events_dict = training_repo['members_events']
    #print training_events_dict['12563492']
    potential_events = list(test_repo['events_info'].keys())

    contentRecommender = ContentRecommender()
    contentRecommender.train(training_events_dict, training_repo)
    test_events_vec = contentRecommender.get_test_events_wth_description(test_repo, potential_events)

    #TEST FOR BEST USERS
    for member in test_members:
         contentRecommender.test(member, potential_events, test_events_vec, simscores)

    # TEST: Call test only for member_id 12563492
    #contentRecommender.test('12563492', potential_events, test_events_vec, simscores)
    # for member_id in train_repo['members_info']:
    #     contentRecommender.test(member_id, potential_events, test_events_vec, simscores)



def time_classifier(training_repo, test_repo, timestamp, simscores, test_members):

    training_events_dict = training_repo['members_events']
    potential_events = list(test_repo['events_info'].keys())

    timeRecommender = TimeRecommender()
    timeRecommender.train(training_events_dict, training_repo)
    test_events_vec = timeRecommender.get_test_event_vecs_with_time(test_repo, potential_events)

    #TEST FOR BEST USERS
    for member in test_members:
         timeRecommender.test(member, potential_events, test_events_vec, simscores)

    #TEST: Call test only for member_id 12563492
    #timeRecommender.test('12563492', potential_events, test_events_vec, simscores)

    # for member_id in training_repo['members_info']:
    #     timeRecommender.test(member_id, potential_events, test_events_vec, simscores)


def loc_classifier(training_repo, test_repo, timestamp, simscores, test_members):
    training_events_dict = training_repo['members_events']
    potential_events = list(test_repo['events_info'].keys())

    locationRecommender = LocationRecommender()
    locationRecommender.train(training_events_dict, training_repo)

    #TEST FOR BEST USERS
    for member in test_members:
        locationRecommender.test(member, potential_events, test_repo, simscores)

    #TEST: Call test only for memeber_id 12563492
    #locationRecommender.test('12563492', potential_events, test_repo, simscores)

    # for member_id in training_repo['members_info']:
    #     locationRecommender.test(member_id, potential_events, test_repo, simscores)


def grp_freq_classifier(training_repo, test_repo, timestamp, simscores, test_members):
    training_events_dict = training_repo['members_events']
    potential_events = list(test_repo['events_info'].keys())

    grp_freq_recommender = GrpFreqRecommender()
    grp_freq_recommender.train(training_events_dict, training_repo)

    #TEST: Call test only for memeber_id 12563492
    #grp_freq_recommender.test('12563492', potential_events, training_repo, simscores)

    for member in test_members:
         grp_freq_recommender.test(member, potential_events, test_repo, simscores)


def main():
    parser = argparse.ArgumentParser(description='Run Event Recommender')
    parser.add_argument('--city', help='Enter the city name')
    parser.add_argument('--algo', nargs='+', help='Enter the classification Algorithm list(svm|mlp|nb|rf)')
    parser.add_argument('--members', help='Enter the number of members on which to run the evaluation')
    args = parser.parse_args()

    city = args.city
    algolist = args.algo
    number_of_members = int(args.members)
    group_members, group_events, event_group = load_groups("../crawler/cities/" + city + "/group_members.json",
                                                            "../crawler/cities/" + city + "/group_events.json")
    events_info = load_events("../crawler/cities/" + city + "/events_info.json")
    members_info = load_members("../crawler/cities/" + city + "/members_info.json")
    member_events = load_rsvps("../crawler/cities/" + city + "/rsvp_events.json")

    repo = dict()
    repo['group_events'] = group_events
    repo['group_members'] = group_members
    repo['events_info'] = events_info
    repo['members_info'] = members_info
    repo['members_events'] = member_events
    repo['event_group'] = event_group

    #simscores_across_features is a dictionary to store similarity score obtained for each feature
    #for each member and for a given event. For example in case of content classifer we will
    #access the similarity score as follows: simscores['content_classifier'][member_id][event_id].
    #We will pass only a specific subdictionary (Ex: simscores['content_classifier']) to the
    #classifier functions, which will work on them and populate them.
    simscores_across_features = defaultdict(lambda :defaultdict(lambda :defaultdict(lambda :0)))
    hybrid_simscores = defaultdict(lambda :defaultdict(lambda :0))

    start_time = 1262304000 # 1st Jan 2010
    end_time = 1388534400 # 1st Jan 2014
    timestamps = get_timestamps(start_time, end_time)
    timestamps = sorted(timestamps, reverse=True)
    count_partition = 1

    f_temp = open('temp_result.txt', 'w+')
    f_temp.write("Using classification algorithms : " + str(algolist) + " and number of members as : " + str(number_of_members) + "\n")

    for t in timestamps:
        start_time = t - train_data_interval
        end_time = t + train_data_interval
        test_members = []
        f = open("scripts/"+city + "_best_users_" + str(start_time) + "_" + str(end_time) + ".txt", "r")
        for users in f:
            test_members.extend(users.split())
        f.close()
        test_members = test_members[:number_of_members]
        print "Partition at timestamp ", datetime.datetime.fromtimestamp(t), " are : "
        training_repo, test_repo = get_partitioned_repo_wrapper(t, repo)
        print "Partitioned Repo retrieved for timestamp : ", datetime.datetime.fromtimestamp(t)

        training_members = set(training_repo['members_events'].keys())
        test_members =  training_members.intersection(set(test_members))
        test_members = list(test_members)
        #Call content based classifer train and test functions from here. Pass the repo
        #as an argument to these functions.
        start = time.clock()
        print "Starting Content Classifier"
        content_classifier(training_repo, test_repo, t, simscores_across_features['content_classifier'], test_members)
        print "Completed Content Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Time Classifier"
        time_classifier(training_repo, test_repo, t, simscores_across_features['time_classifier'], test_members)
        print "Completed Time Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Location Classifier"
        loc_classifier(training_repo, test_repo, t, simscores_across_features['location_classifier'], test_members)
        print "Completed Location Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Group Frequency Classifier"
        grp_freq_classifier(training_repo, test_repo, t, simscores_across_features['grp_freq_classifier'], test_members)
        print "Completed Group Frequency Classifier in ", time.clock() - start, " seconds"

        f_temp.write("============== Starting classification for partition : " +  str(count_partition) + " ===================\n")
        print "============== Starting classification for partition : " +  str(count_partition) + " ==================="
        learningToRank = LearningToRank()
        learningToRank.learning(simscores_across_features, test_repo["events_info"].keys(), test_repo["members_events"], test_members, f_temp, algolist, number_of_members, count_partition)
        f_temp.write("============== Completed classification for partition : " +  str(count_partition) + " ===================\n")
        print "============== Completed classification for partition : " + str(count_partition) + " ==================="
        count_partition += 1
    f_temp.close()

if __name__ == "__main__":
    main()
