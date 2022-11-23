from django.core.cache import cache

def get_cache(cache_key):
    # cache_data = cache.get(cache_key)
    cache_data = None
    return cache_data


def set_cache(cache_key,cache_data):
    # cache.set(cache_key, cache_data, timeout=150)
    pass
    return

def delete_cache(cache_key):
    # if cache_key in cache:
    #     cache.delete(cache_key)
    pass
    return

def update_cache(cache_key,cache_data):
    # if cache_key in cache:
    #     cache.delete(cache_key)
    #     cache.set(cache_key, cache_data)
    pass
    return



