# lib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#route
from routers import keyphrases

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(keyphrases.router)