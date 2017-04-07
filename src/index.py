from preprocessing import *
import sys, getopt

def content_classifier(repo):
    #Wrapper for content classification.
    #call train and test for all member and
    #events and print the results.

    #train(repo, ...)
    #test(repo, ...)
    pass

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["city="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    city = None
    for o, a in opts:
        if o in ("-c", "--city"):
            city = a

    group_members, group_events = load_groups("../crawler/cities/" + city + "/group_members.json",
                                                            "../crawler/cities/" + city + "/group_events.json")
    events_info = load_events("../crawler/cities/" + city + "/events_info.json")
    members_info = load_members("../crawler/cities/" + city + "/members_info.json")
    member_events = load_rsvps("../crawler/cities/" + city + "/rsvp_events.json")

    repo = dict()
    repo['events_info'] = events_info
    repo['members_info'] = members_info
    repo['members_events'] = member_events

    #Call content based classifer train and test functions from here. Pass the repo
    #as an argument to these functions.
    content_classifier(repo)

    print len(events_info)
    print len(members_info)
    print len(member_events)

help_text = """Usage: python index.py -c|--city CITY_NAME"""

def usage():
    print help_text

if __name__ == "__main__":
    main()