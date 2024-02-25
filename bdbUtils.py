from datetime import datetime
from json import JSONEncoder, JSONDecoder


class MyEncoder(JSONEncoder):
    """Extended JSONEncoder to support tuples, sets, and datetime objects"""

    def encode(self, obj):
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': item}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            if isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            else:
                return item

        return super(MyEncoder, self).encode(hint_tuples(obj))

    def default(self, o):
        if isinstance(o, datetime):
            return {'_date': datetime.strftime(o, '%Y-%m-%d')}
        if isinstance(o, set):
            return {'_set': list(o)}

        return JSONEncoder.default(self, o)


class MyDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if '__tuple__' in d:
            return tuple(d['items'])
        if '_date' in d:
            try:
                return datetime.strptime(d['_date'], '%Y-%m-%d')
            except Exception as e:
                raise Exception('Invalid date format')
        if '_set' in d:
            return set(d['_set'])
        return d


def tname_to_schema_key(tname: str) -> str:
    return tname + '.schema'


def tname_to_data_key(tname: str) -> str:
    return tname + '.data'
