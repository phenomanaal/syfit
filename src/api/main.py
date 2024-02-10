from fastapi import FastAPI

app = FastAPI()

# Importing routes from other modules
from src.api import user

# Include routes from other modules
app.include_router(user.router)
