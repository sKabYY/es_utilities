import esjson
import requests
import time


def try_request(retries, interval, method, *args, **kwargs):
    '''
    "method" is the function to do real request.
    '''
    i = 0
    res = None
    while not res and i < retries:
        try:
            res = method(*args, **kwargs)
        except requests.ConnectionError, e:
            i += 1
            if i >= retries:
                raise e
            time.sleep(interval)
    return res.text


def espost(url, data, retries=3, interval=1):
    headers = {'content-type': 'application/json'}
    data_str = esjson.dumps(data)
    return try_request(
        retries, interval,
        requests.post, url, data_str, headers=headers
    )


def esget(url, retries=3, interval=1):
    headers = {'content-type': 'application/json'}
    return try_request(
        retries, interval,
        requests.get, url, headers=headers
    )
