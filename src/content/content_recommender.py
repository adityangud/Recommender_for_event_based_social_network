class ContentRecommender:

    def __init__(self):
        pass

    def train(self, training_events):
        ## input : dict([user, list of events])
        ## output : dict([user, tfidf - vector])
        pass

    def test(self, member_id, potential_events):
        ## input : member_id, list_of_events
        ## output : [event : cosine similarity score]
        pass