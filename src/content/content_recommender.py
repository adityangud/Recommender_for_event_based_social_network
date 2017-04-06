import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class ContentRecommender:

    def __init__(self):
        self.word_tfidf = TfidfVectorizer(ngram_range=(1, 1), analyzer='word', sublinear_tf=True, max_df=0.5, stop_words='english')

#TODO - Fit - form a vocab using training events(all valid events).
#TODO - Ideas for vocab (1 gram, 2 gram or ngram).
    def train(self, training_events):
        ## input : dict([user, list of events])
        ## output : dict([user, tfidf - vector])
        # Assumed training events to be a list of event_info objects
        training_events = np.array([event.description for event in training_events])
        self.word_tfidf.fit(training_events)
        pass

#TODO - Transform - form vectors for a user's past events. Sum these vectors to form user vector. Calculate similarity scores and rank events.
#TODO - Ideas for summing (direct sum, weighted sum(timed, event_importance)).
    def test(self, member, potential_events):
        ## input : member_id, list_of_events
        ## output : [event : cosine similarity score]
        # Assumed member to be a member_info object and potential_events to be a list of event_info objects

        member_desc = ""
        for event in member.events:
            member_desc += event.description

        member_vec = self.word_tfidf.transform(member_desc)
        test_events = np.array([event.description for event in potential_events])
        test_events_vecs = self.word_tfidf.transform(test_events)
        similarity_scores = cosine_similarity(member_vec, test_events_vecs)
        return similarity_scores
