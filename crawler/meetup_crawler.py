from __future__ import unicode_literals
from __future__ import print_function
import codecs
import sys
import requests
import time
from collections import defaultdict
import logging
import json
from socket import error as SocketError
import configparser
import os.path

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename='info.log', level=logging.INFO)

api_keys= ["API_KEY1", "API_KEY2"]
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
config = configparser.ConfigParser()
config.read('crawler.cfg')
members_groups_done = config.getint('Members', 'groups_done')
events_groups_done = config.getint('Events', 'groups_done')
events_rsvp_done = config.getint('RSVPs', 'events_done')
num_request_attempts = 3

def main():
    logging.info('Main Started')
    cities = [("Phoenix", "AZ")]
    cities_groups_dict = get_groups_from_cities(cities)

    logging.info('Groups retrieval for all cities completed')
    for city in cities:
        logging.info('Numbers for groups found for city %s : %s', city, len(cities_groups_dict[city]))

        logging.info('------- Members retrieval for all groups started ---------')
        group_members_dict = get_members_from_groups(cities_groups_dict[city][members_groups_done:], city, members_groups_done)
        logging.info('------- Members retrieval for all groups completed ---------')

        logging.info('------- Events retrieval for all groups started ---------')
        group_events_dict = get_events_from_groups(cities_groups_dict[city][events_groups_done:], city, events_groups_done)
        logging.info('------- Events retrieval for all groups completed ---------')

        flatten_event = [item for sublist in group_events_dict.values() for item in sublist]
        flatten_event.sort()
        logging.info('-------- Event RSVPs retrieval for all events started -------')
        logging.info('Total Number of Events for RSVP : %s', len(flatten_event))
        event_rsvps_dict = get_rsvp_from_events(flatten_event[events_rsvp_done:], city, events_rsvp_done)
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
        create_json_file(all_members_info, "cities/" + city[0] + "/members_info.json")
        logging.info('------- Members Info retrieval for all groups completed ---------')
        logging.info('Total Number of members in the city %s : %s', city, len(all_members_info))


def get_groups_from_cities(cities):
    #return dict containing cities vs group_ids
    city_groups = defaultdict(lambda: list)
    def get_results(params):
        try:
            request = requests.get("http://api.meetup.com/2/groups", params = params)
            handle_throttling(request.headers)
            data = request.json()
            return data
        except (SocketError, requests.ConnectionError) as e:
            logging.error("Failed for API %s params %s", "http://api.meetup.com/2/groups", str(params))
            logging.error("Socket or Connection Exception occured due to : %s", str(e))
            time.sleep(5)

    for (city, state) in cities:
        group_ids = []
        per_page = 200
        results_count = per_page
        offset = 0
        while results_count == per_page:
            response = get_results({"sign":"true","country":"US", "city":city,\
                                    "state":state, "radius": 10, "key":api_keys[current_index], "order": 'id',\
                                    "page": per_page, "offset": offset})
            offset += 1
            results_count = response['meta']['count']
            for group in response['results']:
                group_ids.append(group['id'])
        city_groups[(city, state)] = group_ids
    return city_groups

def get_members_from_groups(group_ids, city, members_groups_done):
    #return dict containing group vs list of member ids
    group_members_dict = defaultdict(lambda: [])
    def get_results(params):
        retry = 0
        while retry < num_request_attempts:
            retry += 1
            try:
                request = requests.get("http://api.meetup.com/2/members", params = params)
                if request.status_code == 500:
                    eprint("Error code: 500", request.text)
                    time.sleep(10)
                else:
                    handle_throttling(request.headers)
                    data = request.json()
                    return data
            except:
                logging.error("Failed for API %s params %s", "http://api.meetup.com/2/members", str(params))
                eprint(sys.exc_info())
                time.sleep(10)

        if retry >= num_request_attempts:
            eprint("Retried the request the maximum of", num_request_attempts, "times! Giving up!")
            exit(request.status_code);

    countGroupsDone = members_groups_done
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
        if countGroupsDone %10 == 0:
            ## filename, dictionary, Config Parent Key, Config Sub Key
            dump_data_and_update_config("group_members.json", group_members_dict, city[0], 'Members', 'groups_done', countGroupsDone)
            logging.info('Number of Groups Done : %s', countGroupsDone)

    dump_data_and_update_config("group_members.json", group_members_dict, city[0], 'Members', 'groups_done', countGroupsDone)
    logging.info('Number of Groups Done : %s', countGroupsDone)
    return get_json_file("cities/" + city[0] + "/" + "group_members.json")

def get_events_from_groups(group_ids, city, event_groups_done):
    #return dict containing group vs list of event ids
    group_events_dict = defaultdict(lambda: [])
    def get_results(params):
        retry = 0
        while retry < num_request_attempts:
            retry += 1
            try:
                request = requests.get("http://api.meetup.com/2/events", params = params)
                if request.status_code == 500:
                    eprint("Error code: 500", request.text)
                    time.sleep(10)
                else:
                    handle_throttling(request.headers)
                    data = request.json()
                    return data
            except:
                logging.error("Failed for API %s params %s", "http://api.meetup.com/2/events", str(params))
                eprint(sys.exc_info())
                time.sleep(10)
        if retry >= num_request_attempts:
            eprint("Retried the request the maximum of", num_request_attempts, "times! Giving up!")
            exit(request.status_code);

    countGroupsDone = event_groups_done
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
        if countGroupsDone % 10 == 0:
            ## filename, dictionary, Config Parent Key, Config Sub Key
            dump_data_and_update_config("group_events.json", group_events_dict, city[0], 'Events', 'groups_done', countGroupsDone)
            logging.info('Number of Groups Done : %s', countGroupsDone)
    dump_data_and_update_config("group_events.json", group_events_dict, city[0], 'Events', 'groups_done', countGroupsDone)
    logging.info('Number of Groups Done : %s', countGroupsDone)
    return get_json_file("cities/" + city[0] + "/" + "group_events.json")

def get_rsvp_from_events(event_ids, city, events_rsvp_done):
    #return dict containing event vs list of rsvps (member) ids
    event_rsvps = defaultdict(lambda: list)
    def get_results(params):
        retry = 0
        while retry < num_request_attempts:
            retry += 1
            try:
                request = requests.get("http://api.meetup.com/2/rsvps", params = params)
                if request.status_code == 500:
                    eprint("Error code: 500", request.text)
                    time.sleep(10)
                else:
                    handle_throttling(request.headers)
                    data = request.json()
                    return data
            except:
                logging.error("Failed for API %s params %s", "http://api.meetup.com/2/rsvps", str(params))
                eprint(sys.exc_info())
                time.sleep(10)
        if retry >= num_request_attempts:
            eprint("Retried the request the maximum of", num_request_attempts, "times! Giving up!")
            exit(request.status_code);

    countEventsDone = events_rsvp_done
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
        countEventsDone+=1
        if countEventsDone%100 == 0:
            dump_data_and_update_config("rsvp_events.json", event_rsvps, city[0], 'RSVPs', 'events_done', countEventsDone)
            logging.info('Number of Events Done : %s', countEventsDone)
    dump_data_and_update_config("rsvp_events.json", event_rsvps, city[0], 'RSVPs', 'events_done', countEventsDone)
    logging.info('Number of Events Done : %s', countEventsDone)
    return get_json_file("cities/" + city[0] + "/" + "rsvp_events.json")

def get_members_info(member_ids):
    #return dict member attributes
    member_info = dict()
    def get_results(params):
        retry = 0
        while retry < num_request_attempts:
            retry += 1
            try:
                request = requests.get("http://api.meetup.com/2/members", params = params)
                if request.status_code == 500:
                    eprint("Error code: 500", request.text)
                    time.sleep(10)
                else:
                    handle_throttling(request.headers)
                    data = request.json()
                    return data
            except:
                logging.error("Failed for API %s params %s", "http://api.meetup.com/2/members", str(params))
                eprint(sys.exc_info())
                time.sleep(10)
        if retry >= num_request_attempts:
            eprint("Retried the request the maximum of", num_request_attempts, "times! Giving up!")
            exit(request.status_code);

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
        retry = 0
        while retry < num_request_attempts:
            retry += 1
            try:
                request = requests.get("http://api.meetup.com/2/events", params=params)
                if request.status_code == 500:
                    eprint("Error code: 500", request.text)
                    time.sleep(10)
                else:
                    handle_throttling(request.headers)
                    data = request.json()
                    return data
            except:
                logging.error("Failed for API %s params %s", "http://api.meetup.com/2/events", str(params))
                eprint(sys.exc_info())
                time.sleep(10)
        if retry >= num_request_attempts:
            eprint("Retried the request the maximum of", num_request_attempts, "times! Giving up!")
            exit(request.status_code);


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
    f = open(filename, "w+")
    f.write(json_repr)
    f.close()

def get_json_file(filename):

    if not os.path.exists(filename):
        return {}

    json_file = open(filename)
    json_str = json_file.read()
    return json.loads(json_str)

def dump_data_and_update_config(filename, dictionary, city, parent_key, sub_key, countGroupsDone):
    current_group_members_dict = get_json_file("cities/" + city + "/" + filename)
    current_group_members_dict.update(dictionary)
    create_json_file(current_group_members_dict, "cities/" + city + "/" + filename)
    dictionary.clear()
    config.set(parent_key, sub_key, str(countGroupsDone))
    with open('crawler.cfg', 'wb') as configfile:
        config.write(configfile)

def eprint(*args, **kwargs):
    """Convenience function to print to stderr."""
    print(*args, file=sys.stderr, **kwargs)

if __name__=="__main__":
    main()