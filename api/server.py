from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Onyrix AI DAW")

app.include_router(router)