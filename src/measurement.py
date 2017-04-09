from collections import defaultdict
member_feature_accuracy = defaultdict(lambda :defaultdict(lambda :None))

class Accuracy:
    def __init__(self):
        self.percentage_sum = 0.0
        self.average = 0.0
        self.count = 0

    def update_average(self, recommedation_accuracy):
        self.percentage_sum += recommedation_accuracy
        self.count += 1
        self.average = self.percentage_sum / self.count

    def get_average(self):
        return self.average

#This is a temporary function designed to measure how accurately we predict
#future events. This measures the running average accuracy of a given feature's
#prediction for a given member_id across all the different partitions.
def top_5_recommendation_measurement(top_events, all_events, member_id, feature):
    accuracy_obj = member_feature_accuracy[feature][member_id]
    if accuracy_obj == None:
        accuracy_obj = Accuracy()
        member_feature_accuracy[feature][member_id] = accuracy_obj

    intersection = sum([1 for x in top_events if x in all_events])
    union = max(len(top_events), len(all_events))
    recommedation_accuracy = intersection / float(union) * 100.0
    accuracy_obj.update_average(recommedation_accuracy)
    print "Recommendation accuracy for", feature , member_id, "is :", accuracy_obj.get_average(), "Percent"
