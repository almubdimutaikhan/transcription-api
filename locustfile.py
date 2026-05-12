from locust import HttpUser, task, between
import random


class TranscriptionUser(HttpUser):
    wait_time = between(1, 3)
    token: str = ""

    def on_start(self):
        email = f"loadtest_{random.randint(1, 999999)}@test.com"
        password = "password123"

        self.client.post("/auth/register", json={"email": email, "password": password})

        resp = self.client.post("/auth/token", json={"email": email, "password": password})
        if resp.status_code != 200 or not resp.text:
            raise Exception(f"Login failed: {resp.status_code} {resp.text}")
        self.token = resp.json()["access_token"]

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def create_job(self):
        self.client.post(
            "/jobs/",
            json={
                "language": "en",
                "audio_url": "https://example.com/audio.mp3",
                "file_ext": "mp3",
                "priority": 1,
            },
            headers=self._headers(),
        )

    @task(1)
    def list_jobs(self):
        self.client.get("/jobs/", headers=self._headers())
