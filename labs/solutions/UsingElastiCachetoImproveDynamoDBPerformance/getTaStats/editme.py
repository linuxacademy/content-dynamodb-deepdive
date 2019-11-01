from curtain import scanTable, deserialize
from pymemcache.client import base
import json

def getStats():
    endpoint = 'EndpointURL'
    memClient = base.Client((endpoint, 11211))
    data = []
    
    items = memClient.get('scan')
    if items is None:
        items = scanTable()
        while len(items) < 2:
            items = scanTable()

        data = deserialize(items)

        memClient.set('scan', json.dumps(data))
    else:
        data = json.loads(items.decode())
    
    ordered = sorted(data, key = lambda i: i['wins'], reverse=True)
    return ordered