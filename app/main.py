from fastapi import FastAPI, Path
import app.models  # register all models on Base.metadata
from app.routes.jobs import router as job_router
app = FastAPI()

@app.get('/healthcheck')
def get_healthcheck():
    return {"status": "ok"}

app.include_router(job_router)