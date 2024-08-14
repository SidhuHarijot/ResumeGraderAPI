from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def load_test(self):
        self.client.get("/")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:8000"
