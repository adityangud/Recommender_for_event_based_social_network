import json
from collections import defaultdict
import heapq

global_member_events = defaultdict(lambda :[])
global_events_info_map = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda: 0.0)))

def initialize(city):
    global global_member_events
    global global_events_info_map
    rsvp_json_file = open("../../crawler/cities/" + city + "/rsvp_events.json")
    json_str = rsvp_json_file.read()
    event_members_map = json.loads(json_str)

    global_member_events = defaultdict(lambda: [])
    for event in event_members_map:
        member_ids = event_members_map[event]
        for member in member_ids:
            global_member_events[member].append(event)

    events_json_file = open("../../crawler/cities/" + city + "/events_info.json")
    json_str = events_json_file.read()
    global_events_info_map = json.loads(json_str)


def get_rsvp_events_from_member_in_range(member_id, start_time, end_time, city):
    global global_member_events
    global global_events_info_map

    ## Filtering
    result_event_ids = []
    for event_id in global_member_events[member_id]:
        if global_events_info_map[event_id]['time'] >=start_time and global_events_info_map[event_id]['time'] <= end_time:
            result_event_ids.append(event_id)

    return result_event_ids

def find_best_users(city, start_time, end_time, number_of_best_users):

    members_json_file = open("../../crawler/cities/" + city + "/members_info.json")
    json_str = members_json_file.read()
    members_map = json.loads(json_str)

    member_events_map = defaultdict(lambda :[])
    for member in members_map:
        member_events_map[member] = len(get_rsvp_events_from_member_in_range(member, start_time, end_time, city))


    return sorted(member_events_map, key=member_events_map.get, reverse=True)[:number_of_best_users]



def main():
    initialize('LCHICAGO')
    print len(get_rsvp_events_from_member_in_range('4445443', 1372639655, 1388450855, 'LCHICAGO'))
    # print find_best_users('LCHICAGO', 1372639655, 1388450855, 10)

if __name__ == "__main__":
    main()
