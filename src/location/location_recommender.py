import numpy as np
from sklearn.neighbors.kde import KernelDensity
from collections import defaultdict

class LocationRecommender:

    def __init__(self):
        pass

    # Applying KDE (assuming normal PDF)
    def train(self, training_events_dict, info_repo):
        ## input : dict([user, list of event ids])
        events_info = info_repo["events_info"]
        self.training_vecs = {}
        for user_id in training_events_dict:
            lat_list = []
            lon_list = []
            for event_id in training_events_dict[user_id]:
                lat = events_info[event_id]["lat"]
                lon = events_info[event_id]["lon"]
                loc = [lat, lon]
                lat_list.append(lat)
                lon_list.append(lon)
            self.training_vecs[user_id] = np.vstack((lat_list, lon_list)).T

    def test(self, member_id, potential_events, info_repo, simscores):
        ## input : member_id, list of potential events
        ## output : PDE scores
        events_info = info_repo["events_info"]
        member_events = np.array(self.training_vecs[member_id])
        #print "member id : ", member_id
        #print "events : ", member_events

        # Found no past history for this user, return.
        # Sorry, can't help without history as no data to fit distribution.
        if len(member_events) == 0:
            return

        kde = KernelDensity(kernel='gaussian').fit(member_events)
        similarity_scores = []
        for event_id in potential_events:
            lat = events_info[event_id]["lat"]
            lon = events_info[event_id]["lon"]
            similarity_scores.append(simscores[member_id][event_id])
            simscores[member_id][event_id] = np.exp(kde.score([np.array([lat, lon]).T]))
        #print simscores
        #TEST: Pick top 5 similar scores. Print all events. Print top 5 events.
        #similarity_scores = np.array(similarity_scores)
        #args = similarity_scores.argsort()[:-5:-1]
        #print "All event ids ", info_repo["members_events"]['11173777']
        #top_5_recommended_events = []
        #for i in args:
        #   top_5_recommended_events.append(potential_events[i])
        #print top_5_recommended_events





