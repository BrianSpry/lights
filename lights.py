import requests
import json
import time
import random

API_URL = 'http://192.168.0.100/api/'
BRIX_URL = 'http://192.168.0.100/api/1brixsprix'

LIGHTS = 'lights'
CHIEF = '1'
BROKEN_PIECE_OF_SHIT = '2'
KEEF = '3'
POOP = '4'
STATE = 'state'
GROUPS = 'groups'
ALL = '0'
ACTION = 'action'
CONFIG = 'config'

def get_on_status(light):
    cur_url = '/'.join([BRIX_URL,LIGHTS,light])
    print cur_url
    return json.loads(requests.get(cur_url).text)['state']['on']

def get_config():
    cur_url = '/'.join(BRIX_URL,CONFIG)
    return json.loads(requests.get(cur_url).text)

def get_all_lights():
    cur_url = '/'.join([BRIX_URL,LIGHTS])
    return json.loads(requests.get(cur_url).text)

def turn_on_light(light):
    data = json.dumps({'on':True})
    cur_url = '/'.join([BRIX_URL,LIGHTS,light,STATE])
    x = requests.put(cur_url, data=data)

def turn_off_light(light):
    data = json.dumps({'on':False})
    cur_url = '/'.join([BRIX_URL,LIGHTS,light,STATE])
    x = requests.put(cur_url, data=data)

def turn_on_all(hue=10000):
    data = json.dumps({'on':True,'hue':hue})
    cur_url = '/'.join([BRIX_URL,GROUPS,ALL,ACTION])
    x = requests.put(cur_url,data=data)
    print x.text

def change_hue_all(hue=10000):
    data = json.dumps({'hue':hue})
    cur_url = '/'.join([BRIX_URL,GROUPS,ALL,ACTION])
    x = requests.put(cur_url,data=data)
    print x.text

def turn_off_all():
    data = json.dumps({'on':False})
    cur_url = '/'.join([BRIX_URL,GROUPS,ALL,ACTION])
    x = requests.put(cur_url,data=data)
    print x.text

def random_color(length,interval):
    number_intervals = int(length/interval)
    initial_color = random.randint(0,65535)
    turn_on_all(initial_color)
    for i in xrange(0,number_intervals):
        next_color =  random.randint(0,65535)
        change_hue_all(next_color)
        time.sleep(interval)
    change_hue_all(10000)

def create_group(light_group):
    pass

chief_status = get_on_status(CHIEF)
keef_status = get_on_status(KEEF)
kitchen_status = get_on_status(BROKEN_PIECE_OF_SHIT)
poop_status = get_on_status(POOP)

print chief_status, keef_status, kitchen_status, poop_status
