from fastapi import FastAPI
import app.models  # register all models on Base.metadata
from app.routes.jobs import router as job_router
from app.routes.users import router as user_router

app = FastAPI()


@app.get('/healthcheck')
def get_healthcheck():
    return {"status": "ok"}


app.include_router(job_router)
app.include_router(user_router)