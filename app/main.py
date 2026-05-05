from fastapi import FastAPI, Path
from app.routes.jobs import router as job_router
app = FastAPI()

@app.get('/healthcheck')
def get_healthcheck():
    return {"status": "ok"}

app.include_router(job_router)