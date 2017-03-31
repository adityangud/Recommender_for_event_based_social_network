from __future__ import unicode_literals
import requests
import codecs
import sys
import requests
from collections import defaultdict
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

api_key= "API_KEY"

def main():
    cities = [("Chicago", "IL")]
    cities_groups_dict = get_groups_from_cities(cities)

    for city in cities:
        group_members_dict = get_members_from_groups(cities_groups_dict[city])
        group_events_dict = get_events_from_groups(cities_groups_dict[city])
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
        data = request.json()
        return data

    for (city, state) in cities:
        while (True):
            group_ids = []
            response = get_results({"sign":"true","country":"US", "city":city, "state":state, "radius": 100, "key":api_key, "order": 'id'})
            time.sleep(1)
            results_count = response['meta']['count']
            if results_count == 0:
                break
            for group in response['results']:
                group_ids.append(group['id'])
                #print "," .join(map(unicode, [group['id'], group['name'].replace(","," "), group['urlname'], datetime.datetime.fromtimestamp(group['created']/1000.0), group['members']]))
        city_groups[(city, state)] = group_ids
        time.sleep(1)
    return city_groups



def get_members_from_groups(group_ids):
    #return dict containing group vs list of member ids
    return group_ids

def get_events_from_groups(group_ids):
    #return dict containing group vs list of event ids
    return group_ids

def get_rsvp_from_groups(event_ids):
    #return dict containing event vs list of rsvps (member) ids
    return event_ids

def get_member_info(member_id):
    #return dict member attributes
    return member_id

def get_event_info(event_id):
    #return dict event attributes
    return event_id

if __name__=="__main__":
        main()


## Run this script and send it into a csv:
## python meetup-pages-names-dates.py > meetup_groups.csv
