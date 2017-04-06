from collections import defaultdict
from helper import *

def load_groups(group_members_file, group_events_file):
    group_members = read_json(group_members_file)
    group_events = read_json(group_events_file)
    return group_members, group_events


def load_events(events_info_file):
    events_info = read_json(events_info_file)
    return events_info

def load_members(members_info_file):
    members_info = read_json(members_info_file)
    return members_info

def load_rsvps(rsvps_file):
    event_rsvps = read_json(rsvps_file)
    member_events = defaultdict(lambda : [])
    for event in event_rsvps:
        member_ids = event_rsvps[event]
        for member in member_ids:
            member_events[member].append(event)

    return member_events