import operator

class LearningToRank:
    def __init__(self):
        pass

    def learning_to_rank(self,simscores_across_features, events, members, hybrid_simscores):

        ### Basic Average of simscores
        member = '12563492'
        for event in events:
            for feature in simscores_across_features:
                hybrid_simscores[member][event] += simscores_across_features[feature][member][event]

        args = sorted(hybrid_simscores[member].items(), key=operator.itemgetter(1))[-6:-1]
        print "Top 5 events recommended to user ", member, " : ", args