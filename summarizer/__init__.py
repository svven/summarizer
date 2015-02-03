"""
Summarizer initialization.
"""
import config, database, redis, summary, aggregator

## Database
database.init(config)
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)

## Summary
summary.config.from_object(config)

## Aggregator
aggregator.init(config) # delayed init
