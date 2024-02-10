from fastapi import FastAPI

app = FastAPI()

# Importing routes from other modules
from src.api import user, measurement


# Include routes from other modules
app.include_router(user.router)
app.include_router(measurement.router)
