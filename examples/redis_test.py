import redis


r = redis.Redis(host="localhost", port=6379, db=0)
r.json().set("mykey", ".", {"hello": "world", "i am": ["a", "json", "object!"]})
