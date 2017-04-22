import operator

class LearningToRank:
    def __init__(self):
        pass

    def learning_to_rank(self,simscores_across_features, events, members, hybrid_simscores):

        ### Basic Average of simscores
        member_recommendations = {}
        for member in members:
            for event in events:
                for feature in simscores_across_features:
                    hybrid_simscores[member][event] += simscores_across_features[feature][member][event]
            args = sorted(hybrid_simscores[member].items(), key=operator.itemgetter(1))
            member_recommendations[member] = args
        #print "events recommended to user : ", member, " in sorted order : ", args
        return member_recommendations
