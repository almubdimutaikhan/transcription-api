from fastapi import FastAPI, Path
from typing import Annotated
from pydantic import BaseModel, Field
app = FastAPI()

class Job(BaseModel):
    language: str = Field()
    audio_url: str = Field()
    priority: int = Field(default=0)

@app.post('/jobs/new')
def create_job(job: Job):
    return {"status": "ok", "job": job}

@app.get('/jobs/{job_id}')
def find_job(job_id: Annotated[str, Path(min_length=1)]):
    return {"status": "nok", "message": f"job with id {job_id} not found" }

@app.get('/healthcheck')
def get_healthcheck():
    return {"status": "ok"}