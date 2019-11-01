from pymemcache.client import base

def invalidateCache():
    endpoint = 'EndpointURL'

    memClient = base.Client((endpoint, 11211))
    print('Invalidating Cache!')
    memClient.delete('scan')