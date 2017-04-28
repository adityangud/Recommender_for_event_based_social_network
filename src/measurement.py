from collections import defaultdict
member_feature_accuracy = defaultdict(lambda :None)

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
def recommendation_measurement(test_members_sorted_events, all_members_rsvpd_events, test_members):
    for member_id in test_members:
        accuracy_obj = member_feature_accuracy[member_id]
        if accuracy_obj == None:
            accuracy_obj = Accuracy()
            member_feature_accuracy[member_id] = accuracy_obj

        # sorted_events = [(event_id, score)]
        rsvpd_events = all_members_rsvpd_events[member_id]
        union = len(rsvpd_events)
        top_sorted_events = test_members_sorted_events[member_id][-union:]
        intersection = sum([1 for x in top_sorted_events if x[0] in rsvpd_events])
        if union != 0:
            recommedation_accuracy = intersection / float(union) * 100.0
        else:
            recommedation_accuracy = 100.0
        accuracy_obj.update_average(recommedation_accuracy)
        print "Recommendation accuracy for", member_id, "is :", recommedation_accuracy, "  and cumulative avg : ", accuracy_obj.get_average(), "Percent"


