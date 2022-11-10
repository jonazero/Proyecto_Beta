import json


def json2dic(myfile):
    with open(myfile, encoding='utf-8') as json_file:
        dis = json.load(json_file)
    return dis


def dic2json(myfile, dic):
    with open(myfile, "w", encoding='utf-8') as outfile:
        json.dump(dic, outfile)
