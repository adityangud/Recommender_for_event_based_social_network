import numpy as np

class GrpFreqRecommender:

    def __init__(self):
        pass

    def train(self, training_events_dict, info_repo):
        self.training_vecs = training_events_dict

    def test(self, member_id, potential_events, info_repo, simscores):
        event_group = info_repo["event_group"]
        group_events = info_repo["group_events"]
        user_attended_event_ids = set(self.training_vecs[member_id])
        if len(user_attended_event_ids) == 0:
            return
        similarity_scores = []
        for i in xrange(len(potential_events)):
            event_id = potential_events[i]
            group_id = event_group[event_id]
            group_event_ids = group_events[group_id]
            user_attended_group_events = user_attended_event_ids.intersection(group_event_ids)
            score = float(len(user_attended_group_events)) / len(user_attended_event_ids)
            similarity_scores.append(score)
            simscores[member_id][event_id] = score
        # print simscores
        # TEST: Pick top 5 similar scores. Print all events. Print top 5 events.
        #similarity_scores = np.array(similarity_scores)
        #args = similarity_scores.argsort()[:-5:-1]
        #print "All event ids ", info_repo["members_events"]['11173777']
        #top_5_recommended_events = []
        #for i in args:
        #   top_5_recommended_events.append(potential_events[i])
        #print top_5_recommended_events
