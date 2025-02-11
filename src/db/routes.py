from bson import ObjectId
from fastapi import APIRouter, Body, Request
from pydantic import ValidationError

from db.models.playerModels import Player, Stats

router = APIRouter()


@router.get('/')
async def getPlayers(request: Request) -> list[Player]:
  db = request.players
  response = list(db.find({}))
  for item in response:
    item['_id'] = str(item['_id'])
  return response


@router.get('/')
async def getPlayerByDiscordId(request: Request, discord_id):
  db = request.players
  response = db.find_one({'discord_id': discord_id})
  if response:
    response['_id'] = str(response['_id'])
    response['stats'] = Stats(**response['stats'])
    # Try to match the response to a Player object.
    try:
      response = Player(**response)
      return response
    except ValidationError as e:
      print(e)
      return ValidationError
  else:
    return None


@router.post('/')
async def addPlayer(request: Request, player: Player = Body(...)):
  db = request.players
  response = db.insert_one(player.model_dump())
  return {'id': str(response.inserted_id)}


@router.delete('/{id}')
async def deletePlayer(request: Request, id):
  _id = ObjectId(id)
  db = request.players
  response = db.delete_one({'_id': _id})
  return {'deleted_count': response.deleted_count}


@router.put('/{id}')
async def updatePlayer(
  request: Request, id, player: Player = Body(...)
):
  try:
    _id = ObjectId(id)
    db = request.players
    response = db.update_one(
      {'_id': _id}, {'$set': player.model_dump()}
    )
  except Exception as e:
    raise Exception(e)
  return {'updated_count': response.modified_count}
