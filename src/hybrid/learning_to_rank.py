import operator

class LearningToRank:
    def __init__(self):
        pass

    def learning_to_rank(self,simscores_across_features, events, members, hybrid_simscores):

        ### Basic Average of simscores
        for member in members:
            for event in events:
                for feature in simscores_across_features:
                    hybrid_simscores[member][event] += simscores_across_features[feature][member][event]

        args = sorted(hybrid_simscores['12563492'].items(), key=operator.itemgetter(1))[-6:-1]
        print "Top 5 events recommended to user 12563492", args