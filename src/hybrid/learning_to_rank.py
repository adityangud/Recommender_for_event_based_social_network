import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.svm import LinearSVC


class LearningToRank:
    def __init__(self):
        pass

    def learning(self,simscores_across_features, test_events, all_members_rsvpd_events, test_members, f, algolist, number_of_members):
        training_data_features_list = []
        train_y = []
        training_members = int(0.8 * number_of_members)
        for feature in simscores_across_features:
            features = []
            for member in test_members[:training_members]:
                for event in test_events:
                    features.append(simscores_across_features[feature][member][event])
            final_features = np.array(features)
            training_data_features_list.append(final_features)

        for member in test_members[:training_members]:
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
            for member in test_members[training_members:]:
                for event in test_events:
                    features.append(simscores_across_features[feature][member][event])
            final_features = np.array(features)
            test_data_features_list.append(final_features)

        for member in test_members[training_members:]:
            for event in test_events:
                if event in all_members_rsvpd_events[member]:
                    test_y.append(1)
                else:
                    test_y.append(0)

        final_test_data_features_list = np.column_stack(test_data_features_list)
        final_test_y = np.array(test_y)
        classification_algo = LinearSVC()
        if 'svm' in algolist:
            classification_algo = MLPClassifier()
            classification_algo.fit(final_training_data_features_list, final_train_y)
            predictions = classification_algo.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "SVM -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'mlp' in algolist:
            classification_algo = MLPClassifier()
            classification_algo.fit(final_training_data_features_list, final_train_y)
            predictions = classification_algo.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "MLP -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'nb' in algolist:
            classification_algo = GaussianNB()
            classification_algo.fit(final_training_data_features_list, final_train_y)
            predictions = classification_algo.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "NB -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'rf' in algolist:
            classification_algo = RandomForestClassifier()
            classification_algo.fit(final_training_data_features_list, final_train_y)
            predictions = classification_algo.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "RF -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()


