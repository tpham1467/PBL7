# lib
from config.fast_api import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# route
from routers import cli, crawl, data_file, db, preprocess, test, tracking

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

app.include_router(test.router)
app.include_router(data_file.router)
app.include_router(crawl.router)
app.include_router(cli.router)
app.include_router(db.router)
app.include_router(preprocess.router)
app.include_router(tracking.router)
