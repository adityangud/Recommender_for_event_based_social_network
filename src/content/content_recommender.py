class ContentRecommender:

    def __init__(self):
        pass

#TODO - Fit - form a vocab using training events(all valid events).
#TODO - Ideas for vocab (1 gram, 2 gram or ngram).
    def train(self, training_events):
        ## input : dict([user, list of events])
        ## output : dict([user, tfidf - vector])
        pass

#TODO - Transform - form vectors for a user's past events. Sum these vectors to form user vector. Calculate similarity scores and rank events.
#TODO - Ideas for summing (direct sum, weighted sum(timed, event_importance)).
    def test(self, member_id, potential_events):
        ## input : member_id, list_of_events
        ## output : [event : cosine similarity score]
        pass