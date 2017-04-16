from collections import defaultdict
import pandas as pd
import json
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

default_loc = {
    'CHICAGO' :
        {
            'lat':41.8781,
            'lon':87.6298
        },
    'PHOENIX' :
        {
            'lat':33.4484,
            'lon':-112.0740
        },
    'SAN JOSE' :
        {
            'lat':37.3382,
            'lon':-121.8863
        }
}

city_groups_dict = defaultdict(lambda :[])
groups_city_dict = defaultdict(lambda :"")
group_events_dict = defaultdict(lambda : defaultdict(lambda :[]))
group_members_dict = defaultdict(lambda : defaultdict(lambda :[]))
member_groups_dict = defaultdict(lambda : "")
event_groups_dict = defaultdict(lambda :"")
rsvp_event_members_dict = defaultdict(lambda : defaultdict(lambda :[]))
members_info_dict = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda: 0.0)))
events_info_dict = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda: 0.0)))
location_lat_lon_dict = defaultdict(lambda :defaultdict(lambda :0.0))

def create_json_file(dictionary, filename):
    json_repr = json.dumps(dictionary)
    f = open(filename, "w+")
    f.write(json_repr)
    f.close()


def main():
    cities = ["PHOENIX", "SAN JOSE", "CHICAGO"]
    get_groups_from_cities(cities)
    get_events_from_groups()
    get_members_from_groups()
    get_rsvp_from_events()
    get_member_info()
    get_event_info()


def get_groups_from_cities(cities):
    global city_groups_dict
    city_data = pd.read_csv("mclre_data/groups.csv")
    city_list = city_data.region
    group_list = list(city_data.group_id)
    for i in xrange(len(city_list)):
        city_groups_dict[str(city_list[i])].append(str(group_list[i]))
        groups_city_dict[str(group_list[i])] = (str(city_list[i]))

def get_events_from_groups():
    group_events = pd.read_csv("mclre_data/group_events.csv")
    global group_events_dict
    global groups_city_dict
    global event_groups_dict

    group_ids = group_events.group_id
    event_ids = group_events.event_id
    for i in xrange(len(group_ids)):
        group_events_dict[groups_city_dict[str(group_ids[i])]][str(group_ids[i])].append(str(event_ids[i]))
        event_groups_dict[str(event_ids[i])] = str(group_ids[i])
    for city in group_events_dict:
        create_json_file(group_events_dict[city], "cities/"+"L"+city+"/group_events.json")

def get_members_from_groups():
    group_members = pd.read_csv("mclre_data/group_users.csv")
    global group_members_dict
    global groups_city_dict

    group_ids = group_members.group_id
    member_ids = group_members.user_id
    for i in xrange(len(group_ids)):
        group_members_dict[groups_city_dict[str(group_ids[i])]][str(group_ids[i])].append(str(member_ids[i]))
        member_groups_dict[str(member_ids[i])] = str(group_ids[i])

    for city in group_members_dict:
        create_json_file(group_members_dict[city], "cities/"+"L"+city+"/group_members.json")

def get_rsvp_from_events():
    global event_groups_dict
    global groups_city_dict
    global rsvp_event_members_dict
    response_list = []
    member_list = []
    event_list = []
    for i in xrange(1, 18):
        rsvp_data = pd.read_csv("mclre_data/rsvps_"+str(i)+".csv")
        response_list.extend(rsvp_data.response)
        member_list.extend(rsvp_data.user_id)
        event_list.extend(rsvp_data.event_id)

    for i in xrange(len(response_list)):
        if response_list[i] == "yes":
            city = groups_city_dict[event_groups_dict[str(event_list[i])]]
            rsvp_event_members_dict[city][str(event_list[i])].append(str(member_list[i]))
    for city in rsvp_event_members_dict:
        create_json_file(rsvp_event_members_dict[city], "cities/"+"L"+city+"/rsvp_events.json")

def get_member_info():
    global members_info_dict
    global member_groups_dict
    global groups_city_dict
    member_id = []
    lat = []
    long = []
    for i in xrange(1, 8):
        user_data = pd.read_csv("mclre_data/users_"+str(i)+".csv")
        member_id.extend(user_data.user_id)
        lat.extend(user_data.latitude)
        long.extend(user_data.longitude)

    for i in xrange(len(user_data)):
        city = groups_city_dict[member_groups_dict[str(member_id[i])]]
        members_info_dict[city][str(member_id[i])]["lat"] = float(lat[i])
        members_info_dict[city][str(member_id[i])]["lon"] = float(long[i])
    for city in members_info_dict:
        create_json_file(members_info_dict[city], "cities/" + "L" + city + "/members_info.json")

def get_event_info():
    global events_info_dict
    global groups_city_dict
    global event_groups_dict
    global location_lat_lon_dict
    event_id = []
    location = []
    event_time = []
    description = []

    location_data = pd.read_csv("mclre_data/locations.csv")
    loc_id = list(location_data.location_id)
    lat = list(location_data.latitude)
    long = list(location_data.longitude)

    for i in xrange(len(loc_id)):
        l = loc_id[i]
        if pd.isnull(l):
            continue
        location_lat_lon_dict[l]["lat"] = lat[i]
        location_lat_lon_dict[l]["lon"] = long[i]

    for i in xrange(1, 25):
        event_data = pd.read_csv("mclre_data/events_"+str(i)+".csv")
        event_id.extend(event_data.event_id)
        location.extend(event_data.location_id)
        event_time.extend(event_data.time)
        description.extend(event_data.description)

    for i in xrange(len(event_id)):
        city = groups_city_dict[event_groups_dict[event_id[i]]]
        events_info_dict[city][event_id[i]]["time"] = str(event_time[i])
        if pd.isnull(description[i]):
            desc = ""
        else:
            desc = str(description[i])
        events_info_dict[city][event_id[i]]["description"] = desc

        if pd.isnull(location[i]):
            lattitude = default_loc[city]["lat"]
            longitude  = default_loc[city]["lon"]
        else:
            l = location[i]
            lattitude = location_lat_lon_dict[l]["lat"]
            longitude = location_lat_lon_dict[l]["lon"]
        events_info_dict[city][event_id[i]]["lat"] = float(lattitude)
        events_info_dict[city][event_id[i]]["lon"] = float(longitude)

    for city in events_info_dict:
        create_json_file(events_info_dict[city], "cities/" + "L" + city + "/events_info.json")


if __name__ == "__main__":
    logging.info(" ----------- Start Local Crawler ------------")
    main()
    logging.info(" ----------- End Local Crawler ------------")