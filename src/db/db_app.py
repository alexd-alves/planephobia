import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from motor import motor_asyncio

from db.routes import router

# Get db connection details from env variables
load_dotenv()
ATLAS_URI = os.getenv('ATLAS_URI')


# Db setup
async def connectToDB():
  """Connects to Database.

  Returns:
      AsyncIOMotorClient: New connection to single MongoDB instance.
  """
  client = motor_asyncio.AsyncIOMotorClient(ATLAS_URI)
  print(client)
  return client


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Context manager to ensure connection to DB is ended.

  Args:
      app (FastAPI): FastAPI entry point.
  """
  client = await connectToDB()
  app.db = client.get_database('testing_apiv2')
  app.players = app.db.get_collection('players')
  print('Connected to database.')
  yield
  print('Shutting down db connection.')


app = FastAPI(lifespan=lifespan)
app.include_router(router)
