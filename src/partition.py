import time
from collections import defaultdict

train_data_interval = ((364 / 2) * 24 * 60 * 60)  # (6 months, or half a year)

def get_timestamps(start_time, end_time):
    return [start_time + train_data_interval for start_time in range(start_time, end_time- 2 * train_data_interval, train_data_interval)]

def get_partitioned_repo_wrapper(timestamp, repo):
    start_time = timestamp - train_data_interval
    end_time = timestamp + train_data_interval
    training_repo = get_partitioned_repo(repo, start_time, timestamp)
    test_repo = get_partitioned_repo(repo, timestamp, end_time)
    return training_repo, test_repo

def get_partitioned_repo(repo, start_time, end_time):

    ## finding all events happened in training interval
    events_info = repo['events_info']
    events_info_in_range = filter_events_info(events_info, start_time, end_time)

    ## finding member info of all those who rsvp to above training_events
    member_events_in_range = dict()
    member_events = repo['members_events']
    members_info = repo['members_info']
    all_event_ids_in_range = sorted(events_info_in_range.keys())
    for member in members_info:
        event_ids_for_member = member_events[member]
        filtered_event_ids = get_intersection(all_event_ids_in_range, event_ids_for_member)
        if len(filtered_event_ids) != 0:
            member_events_in_range[member] = filtered_event_ids

    ## finding all relevant(in time limit) events for all groups
    group_events_in_range = dict()
    group_events = repo['group_events']
    for group_id in group_events:
        event_ids_for_group = group_events[group_id]
        filtered_event_ids = get_intersection(all_event_ids_in_range, event_ids_for_group)
        if len(filtered_event_ids) != 0:
            group_events_in_range[group_id] = filtered_event_ids

    ## finding group of those events which happened in timerange
    event_group_in_range = dict()
    event_group = repo['event_group']
    for event in events_info_in_range:
        if event in event_group:
            event_group_in_range[event] = event_group[event]

    ## finding members info of all those which are involved in timerange
    member_info_in_range = dict()
    for member in member_events_in_range:
        member_info_in_range[member] = members_info[member]

    return {'events_info':events_info_in_range, 'members_events': defaultdict(lambda :[], member_events_in_range), 'members_info': member_info_in_range, 'group_events': group_events_in_range, 'event_group': event_group_in_range}

def get_member_events_dict_in_range(repo, start_time, end_time):
    member_events = repo['members_events']
    sub_member_events = {}
    for member in member_events:
        sub_member_events[member] = filter_events_by_time_range(repo, member_events[member], start_time, end_time)
    return sub_member_events

def filter_events_by_time_range(repo, events, start, end):
    new_event_ids = []
    events_info = repo["events_info"]
    for e in events:
        if events_info[e]['time'] >= start and events_info[e]['time'] <= end:
            new_event_ids.append(e)

    return new_event_ids

def get_intersection(bigger_list, smaller_list):
    common = []
    for element in smaller_list:
        if binarySearch(bigger_list, element):
            common.append(element)
    return common

def binarySearch(alist, item):
    first = 0
    last = len(alist)-1
    found = False

    while first<=last and not found:
        midpoint = (first + last)//2
        if alist[midpoint] == item:
            found = True
        else:
            if item < alist[midpoint]:
                last = midpoint-1
            else:
                first = midpoint+1

    return found

def filter_events_info(events_info, start, end):
    new_events_info = {}
    for e in events_info:
        if events_info[e]['time'] >= start and events_info[e]['time'] <= end:
            new_events_info[e] = events_info[e]

    return new_events_info