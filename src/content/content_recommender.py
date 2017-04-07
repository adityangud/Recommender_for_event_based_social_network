import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class ContentRecommender:

    def __init__(self):
        self.word_tfidf = TfidfVectorizer(ngram_range=(1, 1), analyzer='word', sublinear_tf=True, max_df=0.5, stop_words='english', norm="l2")

#TODO - Fit - form a vocab using training events(all valid events).
#TODO - Ideas for vocab (1 gram, 2 gram or ngram).
    def train(self, training_events_dict, info_repo):
        ## input : dict([user, list of events_ids])
        events_info = info_repo["events_info"]
        self.training_vecs = {}
        training_events = np.array([events_info[event_id]["description"] for user_id in training_events_dict for event_id in training_events_dict[user_id]])
        self.word_tfidf.fit(training_events)
        for user_id in training_events_dict:
            training_event = ""
            for event_id in training_events_dict[user_id]:
                training_event += events_info[event_id]["description"]
            training_vec = self.word_tfidf.transform(np.array([training_event]))
            self.training_vecs[user_id] = training_vec
        #print self.word_tfidf.vocabulary
        pass

#TODO - Transform - form vectors for a user's past events. Sum these vectors to form user vector. Calculate similarity scores and rank events.
#TODO - Ideas for summing (direct sum, weighted sum(timed, event_importance)).
    def test(self, member_id, potential_events, info_repo):
        ## input : member_id, list_of_events
        ## output : [cosine similarity scores]
        member_vec = self.training_vecs[member_id]
        events_info = info_repo["events_info"]
        test_events = np.array([events_info[event_id]["description"] for event_id in potential_events])
        test_events_vecs = self.word_tfidf.transform(test_events)
        similarity_scores = cosine_similarity(member_vec, test_events_vecs)
        return similarity_scores
