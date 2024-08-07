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

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --host http://vote")
