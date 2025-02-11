import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient

from db.routes import router

# Get db connection details from env variables
load_dotenv()
ATLAS_URI = os.getenv('ATLAS_URI')


# Db setup
async def connectToDB():
  db = MongoClient(ATLAS_URI)
  print(db)
  return db


@asynccontextmanager
async def lifespan(app: FastAPI):
  dbHost = await connectToDB()
  app.db = dbHost['testing']
  app.players = app.db['players']
  print('Connected to database.')
  yield
  print('Shutting down db connection.')


app = FastAPI(lifespan=lifespan)
app.include_router(router)
