from __future__ import unicode_literals
import codecs
import sys
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

api_key= "API_KEY"

def main():
    cities = []
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

def get_members_from_groups(group_ids):
    #return dict containing group vs list of member ids

def get_events_from_groups(group_ids):
    #return dict containing group vs list of event ids

def get_rsvp_from_groups(event_ids):
    #return dict containing event vs list of rsvps (member) ids

def get_member_info(member_id):
    #return dict member attributes

def get_event_info(event_id):
    #return dict event attributes


if __name__=="__main__":
        main()


## Run this script and send it into a csv:
## python meetup-pages-names-dates.py > meetup_groups.csv