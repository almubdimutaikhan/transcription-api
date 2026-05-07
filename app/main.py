from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

import app.models  # register all models on Base.metadata
import app.database as _db
from app.routes.auth import router as auth_router
from app.routes.jobs import router as job_router
from app.routes.users import router as user_router

app = FastAPI(title='Transcription API')


@app.get('/healthcheck', tags=['health'])
async def healthcheck(request: Request):
    try:
        async with _db.engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        return {'status': 'ok', 'db': 'ok'}
    except Exception:
        return JSONResponse(status_code=503, content={'status': 'error', 'db': 'unreachable'})


app.include_router(auth_router)
app.include_router(job_router)
app.include_router(user_router)
