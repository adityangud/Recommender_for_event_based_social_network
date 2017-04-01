from __future__ import unicode_literals
import codecs
import sys
import requests
import time
from collections import defaultdict
import logging
import json
from socket import error as SocketError

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename='info.log', level=logging.INFO)

api_keys= ["3079444c2336933b243649213d4436", "56515058531323e47727a634743"]
current_index = 0

default_loc = {
    'College Station' :
        {
            'lat':30.600000381469727,
            'lon':-96.29000091552734
        },
    'Chicago' :
        {
            'lat':41.8781,
            'lon':87.6298
        },
    'Phoenix' :
        {
            'lat':33.4484,
            'lon':-112.0740
        },
    'San Jose' :
        {
            'lat':37.3382,
            'lon':-121.8863
        }
}

def main():
    logging.info('Main Started')
    cities = [("Phoenix", "AZ")]
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

        flatten = [item for sublist in group_events_dict.values() for item in sublist]
        set_of_events = set(flatten)
        logging.info('-------- Event RSVPs retrieval for all events started -------')
        event_rsvps_dict = get_rsvp_from_events(set_of_events)
        create_json_file(event_rsvps_dict, "cities/" + city[0] + "/rsvp_events.json")
        logging.info('-------- Event RSVPs retrieval for all events completed -------')


        logging.info('------- Events Info retrieval for all groups started ---------')
        all_events_info = dict()
        for group in group_events_dict:
            logging.info('Numbers for events found for group %s : %s', group, len(group_events_dict[group]))
            all_events_info.update(get_events_info(group_events_dict[group], default_loc[city[0]]['lat'], default_loc[city[0]]['lon']))
        create_json_file(all_events_info, "cities/" + city[0] + "/events_info.json")
        logging.info('------- Events Info retrieval for all groups completed ---------')
        logging.info('Total Number of events in the city %s : %s', city, len(all_events_info))


        logging.info('------- Members Info retrieval for all groups started ---------')
        all_members_info = dict()
        for group in group_members_dict:
            logging.info('Numbers for members found for group %s : %s', group, len(group_members_dict[group]))
            all_members_info.update(get_members_info(group_members_dict[group]))
        create_json_file(all_events_info, "cities/" + city[0] + "/members_info.json")
        logging.info('------- Members Info retrieval for all groups completed ---------')
        logging.info('Total Number of members in the city %s : %s', city, len(all_members_info))


def get_groups_from_cities(cities):
    #return dict containing cities vs group_ids
    city_groups = defaultdict(lambda: list)
    def get_results(params):
        try:
            request = requests.get("http://api.meetup.com/2/groups", params = params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/groups", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
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
                                    "state":state, "radius": 1, "key":api_keys[current_index], "order": 'id',\
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
        try:
            request = requests.get("http://api.meetup.com/2/members", params = params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/members", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
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
            response = get_results({"group_id": group, "page": per_page, "offset": offset, "key": api_keys[current_index]})
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
        try:
            request = requests.get("http://api.meetup.com/2/events", params = params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/events", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
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
            response = get_results({"group_id": group, "page": per_page, "offset": offset, "key": api_keys[current_index]})
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
        try:
            request = requests.get("http://api.meetup.com/2/rsvps", params = params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/rsvps", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
        handle_throttling(request.headers)
        data = request.json()
        return data

    for event_id in event_ids:
        rsvp_ids = []
        per_page = 200
        results_count = per_page
        offset = 0
        while results_count == per_page:
            response = get_results({"key":api_keys[current_index], "page": per_page, "offset": offset, "event_id": event_id})
            offset += 1
            results_count = response['meta']['count']
            for rsvp in response['results']:
                rsvp_ids.append(rsvp['member']['member_id'])
        event_rsvps[event_id] = rsvp_ids
    return event_rsvps

def get_members_info(member_ids):
    #return dict member attributes
    member_info = dict()
    def get_results(params):
        try:
            request = requests.get("http://api.meetup.com/2/members", params = params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/members", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
        handle_throttling(request.headers)
        data = request.json()
        return data

    members_info_dict = dict()
    for i in range(0, len(member_ids), 150):
        sub_member_list = member_ids[i:min(i + 150, len(member_ids))]
        response = get_results({"key":api_keys[current_index], "member_id": ','.join(str(id) for id in sub_member_list), "page": 200})
        for member in response['results']:
            member_info = dict()
            member_info["lat"] = member["lat"]
            member_info["lon"] = member["lon"]
            members_info_dict[member["id"]] = member_info
    return members_info_dict

def get_events_info(event_ids, default_lat, default_lon):
    #return dict event attributes

    def get_results(params):
        try:
            request = requests.get("http://api.meetup.com/2/events", params=params)
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/events", str(params))
            logging.error("Response is : %s", request.json())
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)
        handle_throttling(request.headers)
        data = request.json()
        return data

    events_info_dict = dict()

    for i in range(0, len(event_ids), 150):
        sub_event_list = event_ids[i:min(i + 150, len(event_ids))]
        response = get_results({"key": api_keys[current_index], "event_id": ','.join(sub_event_list), "page": 200})
        for event in response['results']:
            event_info = dict()
            if "venue" in event:
                event_info["lat"] = event["venue"]["lat"]
                event_info["lon"] = event["venue"]["lon"]
            else:
                event_info["lat"] = default_lat
                event_info["lon"] = default_lon
            if "description" in event:
                event_info["description"] = event["description"]
            else:
                event_info["description"] = ""
            events_info_dict[event['id']] = event_info
    return events_info_dict

def handle_throttling(headers):
    global current_index
    remaining = headers['X-RateLimit-Remaining']
    resetTime = headers['X-RateLimit-Reset']
    if int(remaining) < 4:
        current_index = (current_index + 1)%2
        request = requests.get("http://api.meetup.com/2/rsvps", params={'key':api_keys[current_index]})
        new_remaining = request.headers['X-RateLimit-Reset']
        new_reset = request.headers['X-RateLimit-Reset']
        if int(new_remaining) < 4:
            time.sleep(float(new_reset) + 0.5)

def create_json_file(dictionary, filename):
    json_repr = json.dumps(dictionary)
    f = open(filename, "w")
    f.write(json_repr)
    f.close()

if __name__=="__main__":
    main()