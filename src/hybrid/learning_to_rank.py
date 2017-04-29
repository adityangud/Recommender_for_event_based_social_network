import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt

class LearningToRank:
    def __init__(self):
        pass

    def learning(self,simscores_across_features, test_events, all_members_rsvpd_events, test_members, f, algolist, number_of_members, partition_number):
        training_data_features_list = []
        train_y = []
        feature_names = []
        training_members = int(0.8 * number_of_members)
        for feature in simscores_across_features:
            features = []
            feature_names.append(feature)
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

        classifier = LinearSVC()
        if 'svm' in algolist:
            classifier = LinearSVC()
            classifier.fit(final_training_data_features_list, final_train_y)

            ## Finding important features
            coef = classifier.coef_.ravel()
            # create plot
            plt.figure(partition_number, figsize=(5, 10))
            ax = plt.subplot(211)
            self.plot_feature_importance(ax, "Linear SVM classifier", coef, partition_number, feature_names)

            predictions = classifier.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "SVM -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'mlp' in algolist:
            classifier = MLPClassifier()
            classifier.fit(final_training_data_features_list, final_train_y)
            predictions = classifier.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "MLP -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'nb' in algolist:
            classifier = GaussianNB()
            classifier.fit(final_training_data_features_list, final_train_y)
            predictions = classifier.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "NB -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        if 'rf' in algolist:
            classifier = RandomForestClassifier()
            classifier.fit(final_training_data_features_list, final_train_y)

            ## Finding important features
            importances = classifier.feature_importances_
            ## Create plot
            plt.figure(partition_number, figsize=(5, 10))
            ax = plt.subplot(212)
            self.plot_feature_importance(ax, "Random Forest Classifier", importances, partition_number, feature_names)

            predictions = classifier.predict(final_test_data_features_list)
            prfs = precision_recall_fscore_support(final_test_y, predictions, labels=[0, 1])
            f.write(
                "RF -> Precision : " + str(prfs[0][1]) + " Recall : " + str(prfs[1][1]) + " F-measure : " + str(prfs[2][1]) + "\n")
            f.flush()
        plt.tight_layout()
        plt.savefig("figures/feature_importance/" + str(partition_number) + "_partition.png")

    def plot_feature_importance(self, ax, title, importances, partition_number, feature_names):
        ax.set_title(title)
        plt.bar(np.arange(4), importances, color='blue')
        feature_names = np.array(feature_names)
        plt.xticks(np.arange(0, 4) + 1.0 / 2, feature_names, rotation=60, ha='right')