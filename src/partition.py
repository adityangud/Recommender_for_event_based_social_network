train_data_interval = ((364 / 2) * 24 * 60 * 60)  # (6 months, or half a year)

def get_timestamps(start_time, end_time):
    return [start_time + train_data_interval for start_time in range(start_time, end_time- 2 * train_data_interval, train_data_interval)]

def get_partitioned_repo(timestamp, repo):

    start_time = timestamp - train_data_interval
    end_time = timestamp + train_data_interval

    ## finding all events happened in training interval
    events_info = repo['events_info']

    events_info_in_range = filter_events_info(events_info, start_time, end_time)
    member_events_in_range = dict()

    ## finding member info of all those who rsvp to above training_events
    member_events = repo['members_events']
    members_info = repo['members_info']
    for member in members_info:
        event_ids_for_member = member_events[member]
        filtered_event_ids = get_intersection(event_ids_for_member, events_info_in_range.keys())
        if len(filtered_event_ids) != 0:
            member_events_in_range[member] = filtered_event_ids

    ## finding members info of all those which are involved in timerange
    member_info_in_range = dict()
    for member in member_events_in_range:
        member_info_in_range[member] = members_info[member]


    return {'events_info':events_info_in_range, 'members_events': member_events_in_range, 'members_info': member_info_in_range}

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
        if events_info[e]['time']/1000 >= start and events_info[e]['time']/1000 <= end:
            new_event_ids.append(e)

    return new_event_ids

def get_intersection(list1, list2):
    return list(set(list1).intersection(set(list2)))

def filter_events_info(events_info, start, end):
    new_events_info = {}
    for e in events_info:
        if (events_info[e]['time']/1000) >= start and (events_info[e]['time']/1000) <= end:
            new_events_info[e] = events_info[e]

    return new_events_info