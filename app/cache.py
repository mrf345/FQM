import pickle
import functools
import os

from app.utils import check_iterator_empty
from app.middleware import redis


def cache_call(resp_type='html'):
    _cache = {}

    def decorator(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            key = f'{wrapped.__name__}:{args}-{kwargs}'

            if 'DOCKER' in os.environ:
                cached = redis.get(key)

                if resp_type == 'html' and cached:
                    cached = cached.decode('utf-8')
                elif cached:
                    cached = pickle.loads(cached)
            else:
                cached = _cache.get(key)

            if cached is not None:
                return cached

            resp = wrapped(*args, **kwargs)

            if 'DOCKER' in os.environ:
                if resp_type == 'html' and type(resp) in {str, bytes}:
                    redis.set(key, resp)
                else:
                    redis.set(key, pickle.dumps(resp))
            else:
                _cache[key] = resp

            return resp

        def cache_clear():
            if 'DOCKER' in os.environ:
                keys, empty = check_iterator_empty(
                    redis.scan_iter(f'{wrapped.__name__}:*')
                )

                if not empty:
                    redis.delete(*keys)

            else:
                _cache.clear()

        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator

