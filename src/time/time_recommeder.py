import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import datetime

class TimeRecommender:
    def __init__(self):
        self.days_of_the_week = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, \
                            'Friday': 5, 'Saturday': 6}

    def add_time_vector(self, event_time, timevector):
        dotw = self.days_of_the_week[datetime.fromtimestamp(event_time/1000).strftime("%A")]
        hour = int(datetime.fromtimestamp(event_time/1000).strftime("%A"))
        timevector[dotw * 24 + hour] += 1

    def get_time_vector(self, event_time):
        dotw = self.days_of_the_week[datetime.fromtimestamp(event_time/1000).strftime("%A")]
        hour = int(datetime.fromtimestamp(event_time/1000).strftime("%A"))
        vec = [0 for i in xrange(24*7)]
        vec[dotw * 24 + hour] = 1
        return vec

    # TODO - Ideas for summing (direct sum, weighted sum(timed, event_importance)).
    def train(self, training_events_dict, info_repo):
        ## input : dict([user, list of events_ids])
        events_info = info_repo["events_info"]
        self.training_vecs = {}

        #TEST: Print training events for 11173777
        #print "Training events ", training_events_dict['11173777']

        for user_id in training_events_dict:
            timevector = [0 for x in xrange(24 * 7)]
            for event_id in training_events_dict[user_id]:
                self.add_time_vector(events_info[events_info]["time"], timevector)
            self.training_vecs[user_id] = timevector

    # Transform - form vectors for a user's past events. Sum these vectors to form user vector. Calculate similarity scores and rank events.
    def test(self, member_id, potential_events, info_repo, simscores):
        ## input : member_id, list_of_events
        ## output : [cosine similarity scores]
        member_vec = self.training_vecs[member_id]
        events_info = info_repo["events_info"]
        test_events_vecs = np.array([self.get_time_vector(events_info[event_id]["time"]) for event_id in potential_events])
        similarity_scores = cosine_similarity(member_vec, test_events_vecs).flatten()
        for i in xrange(len(potential_events)):
            simscores[member_id][potential_events[i]] = similarity_scores[i]

        # TEST: Pick top 5 similar scores. Print all events. Print top 5 events.
        #args =  similarity_scores.argsort()[:-5:-1]
        #print "All event ids ", info_repo["members_events"]['11173777']
        #top_5_recommended_events = []
        #for i in args:
        #    top_5_recommended_events.append(potential_events[i])
