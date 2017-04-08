import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
class ContentRecommender:

    def __init__(self):
        self.word_tfidf = TfidfVectorizer(ngram_range=(1, 1), analyzer='word', sublinear_tf=True, max_df=0.5, stop_words='english', norm="l2")

    # Fit - form a vocab using training events(all valid events).
    # Ideas for vocab (1 gram, 2 gram or ngram).
    # TODO - Ideas for summing (direct sum, weighted sum(timed, event_importance)).
    def train(self, training_events_dict, info_repo):
        ## input : dict([user, list of events_ids])
        events_info = info_repo["events_info"]
        self.training_vecs = {}

        #TEST: Print training events for 11173777
        #print "Training events ", training_events_dict['11173777']
        training_events = np.array([events_info[event_id]["description"] for user_id in training_events_dict for event_id in training_events_dict[user_id]])
        self.word_tfidf.fit(training_events)
        for user_id in training_events_dict:
            training_event = ""
            for event_id in training_events_dict[user_id]:
                training_event += events_info[event_id]["description"] + " "
            training_vec = self.word_tfidf.transform(np.array([training_event]))
            self.training_vecs[user_id] = training_vec

    # Transform - form vectors for a user's past events. Sum these vectors to form user vector. Calculate similarity scores and rank events.
    def test(self, member_id, potential_events, info_repo, simscores):
        ## input : member_id, list_of_events
        ## output : [cosine similarity scores]
        member_vec = self.training_vecs[member_id]
        events_info = info_repo["events_info"]
        test_events = np.array([events_info[event_id]["description"] for event_id in potential_events])
        test_events_vecs = self.word_tfidf.transform(test_events)
        similarity_scores = cosine_similarity(member_vec, test_events_vecs).flatten()
        for i in xrange(len(potential_events)):
            simscores[member_id][potential_events[i]] = similarity_scores[i]

        # TEST: Pick top 5 similar scores. Print all events. Print top 5 events.
        #args =  similarity_scores.argsort()[:-5:-1]
        #print "All event ids ", info_repo["members_events"]['11173777']
        #top_5_recommended_events = []
        #for i in args:
        #    top_5_recommended_events.append(potential_events[i])
