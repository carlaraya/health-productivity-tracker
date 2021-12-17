"""
Basic testing of data lake's validity. Not much actual testing yet but there might be in the future.
"""
import json
import os

DATA_LAKE_DIR = '../data-lake/'

def test_sleep_json(fpath):
    jsonDict = load_json(fpath)

def test_activity_json(fpath):
    jsonDict = load_json(fpath)

def test_calendar_json(fpath):
    jsonDict = load_json(fpath)
        
def load_json(fpath):
    try:
        jsonDict = json.load(open(fpath, 'r'))
    except json.decoder.JSONDecodeError:
        raise AssertionError('Invalid json file: ' + fpath)
    return jsonDict

def main():
    for fname in os.listdir(DATA_LAKE_DIR):
        fpath = DATA_LAKE_DIR + fname
        if 'sleep' in fpath:
            test_sleep_json(fpath)
        elif 'activity' in fpath:
            test_activity_json(fpath)
        elif 'calendar' in fpath:
            test_calendar_json(fpath)
        else:
            raise AssertionError('Invalid file name in data lake, or test not written for category of file: ' + fpath)

if __name__ == '__main__':
    main()
