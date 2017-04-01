from __future__ import unicode_literals
import codecs
import sys
import requests
import time
from collections import defaultdict
import logging
import json

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

api_key= "102c4a7355cf112b28151213b1f3b"

def create_json_file(dictionary, filename):
    json_repr = json.dumps(dictionary)
    f = open(filename, "w")
    f.write(json_repr)
    f.close()

def main():
    logging.info('Main Started')
    cities = [("College Station", "TX")]
    cities_groups_dict = get_groups_from_cities(cities)

    logging.info('Groups retrieval for all cities completed')
    for city in cities:
        logging.info('Numbers for groups found for city %s : %s', city, len(cities_groups_dict[city]))

        logging.info('------- Members retrieval for all groups started ---------')
        group_members_dict = get_members_from_groups(cities_groups_dict[city])
        create_json_file(group_members_dict, "cities/"+ city[0]+"/group_members.json")
        logging.info('------- Members retrieval for all groups completed ---------')

        logging.info('------- Events retrieval for all groups started ---------')
        group_events_dict = get_events_from_groups(cities_groups_dict[city])
        create_json_file(group_events_dict, "cities/" + city[0] + "/group_events.json")
        logging.info('------- Events retrieval for all groups completed ---------')

        for group in group_events_dict:
            for event in group_events_dict[group]:
                event_info = get_event_info(event)

        for group in group_members_dict:
            for member in group_members_dict[group]:
                member_info = get_member_info(member)

        #WRITE TO FILE!! - TODO


def get_groups_from_cities(cities):
    #return dict containing cities vs group_ids
    city_groups = defaultdict(lambda: list)
    def get_results(params):
        request = requests.get("http://api.meetup.com/2/groups", params = params)
        handle_throttling(request.headers)
        data = request.json()
        return data

    for (city, state) in cities:
        group_ids = []
        per_page = 200
        results_count = per_page
        offset = 0
        while results_count == per_page:
            response = get_results({"sign":"true","country":"US", "city":city,\
                                    "state":state, "radius": 1, "key":api_key, "order": 'id',\
                                    "page": per_page, "offset": offset})
            offset += 1
            results_count = response['meta']['count']
            for group in response['results']:
                group_ids.append(group['id'])
        city_groups[(city, state)] = group_ids
    return city_groups

def get_members_from_groups(group_ids):
    #return dict containing group vs list of member ids
    group_members_dict = defaultdict(lambda: [])
    def get_results(params):
        request = requests.get("http://api.meetup.com/2/members", params = params)
        handle_throttling(request.headers)
        data = request.json()
        return data
    countGroupsDone = 0
    for group in group_ids:
        per_page = 200
        results_count = per_page
        offset = 0
        member_ids = []
        while results_count == per_page:
            response = get_results({"group_id": group, "page": per_page, "offset": offset, "key": api_key})
            offset += 1
            results_count = response['meta']['count']
            for member in response['results']:
                member_ids.append(member['id'])
        group_members_dict[group] = member_ids
        countGroupsDone += 1
        if countGroupsDone %100 == 0:
            logging.info('Number of Groups Done : %s', countGroupsDone)
    return group_members_dict

def get_events_from_groups(group_ids):
    #return dict containing group vs list of event ids
    group_events_dict = defaultdict(lambda: [])
    def get_results(params):
        request = requests.get("http://api.meetup.com/2/events", params = params)
        handle_throttling(request.headers)
        data = request.json()
        return data

    countGroupsDone = 0
    for group in group_ids:
        per_page = 200
        offset = 0
        results_count = per_page
        event_ids = []
        while results_count == per_page:
            response = get_results({"group_id": group, "page": per_page, "offset": offset, "key": api_key})
            offset += 1
            results_count = response['meta']['count']
            for member in response['results']:
                event_ids.append(member['id'])
        group_events_dict[group] = event_ids
        countGroupsDone += 1
        if countGroupsDone % 100 == 0:
            logging.info('Number of Groups Done : %s', countGroupsDone)
    return group_events_dict

def get_rsvp_from_events(event_ids):
    #return dict containing event vs list of rsvps (member) ids
    event_rsvps = defaultdict(lambda: list)
    def get_results(params):
        request = requests.get("http://api.meetup.com/2/rsvps", params = params)
        handle_throttling(request.headers)
        data = request.json()
        return data

    for event_id in event_ids:
        rsvp_ids = []
        per_page = 200
        results_count = per_page
        offset = 0
        while results_count == per_page:
            response = get_results({"key":api_key, "page": per_page, "offset": offset, "event_id": event_id})
            offset += 1
            results_count = response['meta']['count']
            for rsvp in response['results']:
                rsvp_ids.append(rsvp['member']['member_id'])
        event_rsvps[event_id] = rsvp_ids
    return event_rsvps

def get_member_info(member_id):
    #return dict member attributes
    member_info = dict()
    def get_results(params):
        request = requests.get("http://api.meetup.com/2/members", params = params)
        handle_throttling(request.headers)
        data = request.json()
        return data

    response = get_results({"key":api_key, "member_id": member_id})
    member_info["id"] = member_id
    member_info["lat"] = response["results"][0]["lat"]
    member_info["lon"] = response["results"][0]["lon"]
    return member_info

def get_event_info(event_id):
    #return dict event attributes
    event_info = dict()

    def get_results(params):
        request = requests.get("http://api.meetup.com/2/events", params=params)
        handle_throttling(request.headers)
        data = request.json()
        return data

    response = get_results({"key": api_key, "event_id": event_id})
    print event_id, response
    event_info["id"] = event_id
    event_info["lat"] = response["results"][0]["venue"]["lat"]
    event_info["lon"] = response["results"][0]["venue"]["lon"]
    event_info["description"] = response["results"][0]["description"]
    return event_info

def handle_throttling(headers):
    remaining = headers['X-RateLimit-Remaining']
    resetTime = headers['X-RateLimit-Reset']
    if int(remaining) < 4:
        time.sleep(float(resetTime))


if __name__=="__main__":
    main()




## Run this script and send it into a csv:
## python meetup-pages-names-dates.py > meetup_groups.csv
