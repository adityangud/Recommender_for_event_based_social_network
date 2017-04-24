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


    def learning(self,simscores_across_features, test_events, all_members_rsvpd_events, test_members):
        from sklearn import svm
        import numpy as np
        from sklearn.svm import LinearSVC
        training_data_features_list = []
        train_y = []
        for feature in simscores_across_features:
            features = []
            for member in test_members[:3]:
                for event in test_events:
                    features.append(simscores_across_features[feature][member][event])
            final_features = np.array(features)
            training_data_features_list.append(final_features)

        for member in test_members[:3]:
            for event in test_events:
                if event in all_members_rsvpd_events[member]:
                    train_y.append(1)
                else:
                    train_y.append(0)

        final_training_data_features_list = np.column_stack(training_data_features_list)
        final_train_y = np.array(train_y)

        test_data_features_list = []
        test_y = []
        for feature in simscores_across_features:
            features = []
            for member in test_members[3:]:
                for event in test_events:
                    features.append(simscores_across_features[feature][member][event])
            final_features = np.array(features)
            test_data_features_list.append(final_features)

        for member in test_members[3:]:
            for event in test_events:
                if event in all_members_rsvpd_events[member]:
                    test_y.append(1)
                else:
                    test_y.append(0)

        final_test_data_features_list = np.column_stack(test_data_features_list)
        final_test_y = np.array(test_y)
        #svm = svm.SVC(C=0.3, kernel='linear', probability=True, verbose=True)
        svm = LinearSVC()
        svm.fit(final_training_data_features_list, final_train_y)
        print "score : ", svm.score(final_test_data_features_list, final_test_y)


