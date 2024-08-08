# from locust import HttpUser, TaskSet, task, between
# import random

# class UserBehavior(TaskSet):
    
#     def on_start(self):
#         # When a user starts, they get a unique voter_id
#         self.voter_id = hex(random.getrandbits(64))[2:-1]
#         self.client.cookies.set('voter_id', self.voter_id)
    
#     @task(1)
#     def vote(self):
#         # Simulate voting for either option A or option B
#         vote = random.choice(['a', 'b'])
#         self.client.post("/", {"vote": vote})
    
#     @task(2)
#     def load_homepage(self):
#         # Load the homepage
#         self.client.get("/")

# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     wait_time = between(1, 5)

# if __name__ == "__main__":
#     import os
#     os.system("locust -f locustfile.py --host http://vote")


from locust import HttpUser, TaskSet, task, between
import random

class UserBehavior(TaskSet):
    
    def on_start(self):
        # When a user starts, they get a unique voter_id
        self.voter_id = hex(random.getrandbits(64))[2:-1]
        self.client.cookies.set('voter_id', self.voter_id)
    
    @task(1)
    def vote(self):
        # Simulate voting for either option A or option B
        vote = random.choice(['a', 'b'])
        self.client.post("/", {"vote": vote})
    
    @task(2)
    def load_homepage(self):
        # Load the homepage
        self.client.get("/")

    @task(3)
    def simulate_slow_queries(self):
        # Simulate a slow query by requesting an endpoint that takes time
        self.client.get("/slow-query")  # Make sure your app has a /slow-query endpoint that introduces delay
    
    @task(4)
    def simulate_500_error(self):
        # Simulate a 500 Internal Server Error
        response = self.client.get("/simulate_500")  # Ensure the app has an endpoint that returns a 500 status code
        if response.status_code == 500:
            raise Exception("Simulated 500 Internal Server Error")

    @task(5)
    def simulate_high_memory_usage(self):
        # Simulate high memory usage by requesting an endpoint that uses memory
        self.client.get("/memory-intensive")  # Ensure your app has a memory-intensive operation here
    
    @task(6)
    def simulate_lock_contention(self):
        # Simulate lock contention by running operations that might cause DB locks
        self.client.post("/lock-contention", {"key": random.randint(1, 100000)})  # Ensure your app has an endpoint that causes lock contention

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --host http://vote")
