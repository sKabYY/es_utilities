from translator.translator import (
    translate,
    Hits,
)

from interp.tilib import (
    eq2nd, _any,
    setup_environment,
)

from interp.titype import mkvoid, mkprimitive


__global_url = 'localhost'
__global_port = '9200'
__global_index = '*'


def connect(url, port):
    global __global_url
    global __global_port
    __global_url = url
    __global_port = port
    return mkvoid()


def set_index(index):
    global __global_index
    __global_index = index
    return mkvoid()


def get_index():
    return __global_index


def prompt():
    return '%s:%s/%s' % (__global_url, __global_port, __global_index)


def fill_default(args, default_list):
    '''
    '''
    res = list(args)
    start = len(res)
    end = len(default_list)
    if start < end:
        res.append(default_list[start])
        start += 1
    return res


def hits(*args):
    '''
    args: [size, fields, condition, sort]
    '''
    default_args = fill_default(args, [10, None, None, None])
    post_data = translate(Hits(*default_args))
    return post_data


def ties_primitive_procedures():
    PM = [
        ('connect', connect, eq2nd(2)),
        ('set-index!', set_index, eq2nd(1)),
        ('get-index', get_index, eq2nd(0)),
        ('hits', hits, _any),
    ]
    return map(lambda (s, b, a): (s, mkprimitive(s, a, b)), PM)


def setup_ties_environment():
    env = setup_environment()
    env.putall(ties_primitive_procedures())
    return env
