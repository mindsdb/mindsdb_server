import json


def wizard():
    input()
    pass

def read(path=None):
    config = {}
    with open('mindsdb_server/default_config.json', 'r') as fp:
        config = json.load(fp)
    if path:
        try:
            with open(path,'r') as fp:
                user_config = json.load(fp)
            # TODO make deep merge
            config.update(user_config)
        except Exception:
            pass
    return config
