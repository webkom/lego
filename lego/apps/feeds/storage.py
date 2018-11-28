from django_redis import get_redis_connection


class RedisListStorage:
    """
    Interface for storing lists in redis.
    """

    key_format = "feed_list:{key}:{list}"
    max_length = 20
    data_type = str

    def __init__(self, key, **kwargs):
        self.base_key = key
        self.max_length = kwargs.get("max_length", self.max_length)
        self.data_type = kwargs.get("data_type", self.data_type)

    @property
    def redis(self):
        try:
            return self._redis
        except AttributeError:
            self._redis = get_redis_connection("default")
            return self._redis

    def get_key(self, list_name):
        return self.key_format.format(key=self.base_key, list=list_name)

    def get_keys(self, list_names):
        return [self.get_key(list_name) for list_name in list_names]

    def to_result(self, results):
        if results:
            if len(results) == 1:
                return results[0]
            else:
                return tuple(results)

    def add(self, **kwargs):
        if kwargs:
            pipe = self.redis.pipeline()
            for list_name, values in kwargs.items():
                if values:
                    key = self.get_key(list_name)
                    for value in values:
                        pipe.rpush(key, value)
                    # Removes items from list's head
                    pipe.ltrim(key, -self.max_length, -1)
            pipe.execute()

    def remove(self, **kwargs):
        if kwargs:
            pipe = self.redis.pipeline()
            for list_name, values in kwargs.items():
                key = self.get_key(list_name)
                for value in values:
                    # Removes all occurrences of value in the list
                    pipe.lrem(key, 0, value)
            pipe.execute()

    def count(self, *args):
        if args:
            keys = self.get_keys(args)
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.llen(key)
            return self.to_result(pipe.execute())

    def get(self, *args):
        if args:
            keys = self.get_keys(args)
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.lrange(key, 0, -1)
            results = pipe.execute()
            results = [list(map(self.data_type, items)) for items in results]
            return self.to_result(results)

    def flush(self, *args):
        if args:
            keys = self.get_keys(args)
            self.redis.delete(*keys)
