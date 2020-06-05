import json


def wizard():
    input()
    pass


def read(path):
    with open(path,'r') as fp:
        return json.load(fp)
