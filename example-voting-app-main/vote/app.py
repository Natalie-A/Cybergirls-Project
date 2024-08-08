# from flask import Flask, render_template, request, make_response, g
# from redis import Redis
# import os
# import socket
# import random
# import json
# import logging

# option_a = os.getenv('OPTION_A', "Cats")
# option_b = os.getenv('OPTION_B', "Dogs")
# hostname = socket.gethostname()

# app = Flask(__name__)

# gunicorn_error_logger = logging.getLogger('gunicorn.error')
# app.logger.handlers.extend(gunicorn_error_logger.handlers)
# app.logger.setLevel(logging.INFO)

# def get_redis():
#     if not hasattr(g, 'redis'):
#         g.redis = Redis(host="redis", db=0, socket_timeout=5)
#     return g.redis

# @app.route("/", methods=['POST','GET'])
# def hello():
#     voter_id = request.cookies.get('voter_id')
#     if not voter_id:
#         voter_id = hex(random.getrandbits(64))[2:-1]

#     vote = None

#     if request.method == 'POST':
#         redis = get_redis()
#         vote = request.form['vote']
#         app.logger.info('Received vote for %s', vote)
#         data = json.dumps({'voter_id': voter_id, 'vote': vote})
#         redis.rpush('votes', data)

#     resp = make_response(render_template(
#         'index.html',
#         option_a=option_a,
#         option_b=option_b,
#         hostname=hostname,
#         vote=vote,
#     ))
#     resp.set_cookie('voter_id', voter_id)
#     return resp


# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=80, debug=True, threaded=True)


from flask import Flask, render_template, request, make_response, g
from redis import Redis, RedisError
import os
import socket
import random
import json
import logging
import time

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
hostname = socket.gethostname()

app = Flask(__name__)

# Configure logging with gunicorn
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

# Redis connection pooling settings
REDIS_MAX_CONNECTIONS = int(os.getenv('REDIS_MAX_CONNECTIONS', 20))

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(
            host="redis", 
            db=0, 
            socket_timeout=5, 
            max_connections=REDIS_MAX_CONNECTIONS
        )
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        app.logger.info('Received vote for %s', vote)
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        
        try:
            redis.rpush('votes', data)
        except RedisError as e:
            app.logger.error('Redis error: %s', e)
            return make_response("Internal server error", 500)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp

@app.route("/slow-query")
def slow_query():
    # Simulate a slow query by adding an artificial delay
    time.sleep(5)  # Delay for 5 seconds
    return "This is a slow query response", 200

@app.route("/simulate_500")
def simulate_500():
    # Simulate a 500 Internal Server Error
    return "Simulated 500 error", 500

@app.route("/memory-intensive")
def memory_intensive():
    # Simulate a memory-intensive operation
    data = [random.getrandbits(20) for _ in range(1000000)]
    return "Memory-intensive operation completed", 200

@app.route("/lock-contention", methods=['POST'])
def lock_contention():
    # Simulate lock contention by performing a Redis operation that could cause locking
    redis = get_redis()
    key = request.form.get('key', 'default_key')
    
    try:
        # Simulate a lock by setting a key with a short expiration
        redis.set(key, random.getrandbits(64), ex=2)
        time.sleep(2)  # Simulate a delay that causes lock contention
        redis.get(key)
    except RedisError as e:
        app.logger.error('Redis error during lock contention: %s', e)
        return make_response("Internal server error", 500)
    
    return "Lock contention simulation completed", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
