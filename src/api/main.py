from fastapi import FastAPI
from src.api import user, measurement

app = FastAPI()

# Include routes from other modules
app.include_router(user.router)
app.include_router(measurement.router)
