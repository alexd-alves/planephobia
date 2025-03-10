from fastapi import (
  APIRouter,
  Body,
  HTTPException,
  Response,
  status,
)
from pymongo import ReturnDocument

from db.models.playerCollectionModel import PlayerCollection
from db.models.playerModel import PlayerModel
from db.models.updatePlayerModel import UpdatePlayerModel

router = APIRouter()


@router.post(
  '/',
  response_description='Add new Player',
  response_model=PlayerModel,
  status_code=status.HTTP_201_CREATED,
  response_model_by_alias=False,
)
async def add_player(app, player: PlayerModel = Body(...)):
  """
  Insert a new Player record.
  Unique `id` will be created and provided in response.
  """
  new_player = await app.players.insert_one(
    player.model_dump(by_alias=True, exclude=['id'])
  )
  created_player = await app.players.find_one(
    {'_id': new_player.inserted_id}
  )

  return created_player


@router.get(
  '/',
  response_description='List all Players',
  response_model=PlayerCollection,
  response_model_by_alias=False,
)
async def list_players(app):
  """
  List all player data. Response is limited to 1000 results.
  """
  return PlayerCollection(
    players=await app.players.find({}, {'_id': 0}).to_list(
      1000
    )
  )


@router.get(
  '/{id}',
  response_description='Get a single Player',
  response_model=PlayerModel,
  response_model_by_alias=False,
)
async def get_player(app, discord_id: int):
  """
  Get the record for a specific Player, looked up by `discord_id`.
  """
  if (
    player := await app.players.find_one(
      {'discord_id': discord_id}
    )
  ) is not None:
    return player

  raise HTTPException(
    status_code=404, detail=f'Player {discord_id} not found'
  )


@router.delete(
  '/{id}', response_description='Delete a Player'
)
async def delete_player(app, discord_id: int):
  """
  Remove a single Player from the database.
  """
  delete_result = await app.players.delete_one(
    {'discord_id': discord_id}
  )

  if delete_result.deleted_count == 1:
    return Response(status_code=status.HTTP_204_NO_CONTENT)

  raise HTTPException(
    status_code=404,
    detail=f'Player {discord_id} not found',
  )


@router.put(
  '/{id}',
  response_description='Update a Player',
  response_model=PlayerModel,
  response_model_by_alias=False,
)
async def update_player(
  app,
  discord_id: int,
  player: UpdatePlayerModel = Body(...),
):
  """
  Update individual fields of an existing Player record.

  Only provided fields are updated, missing or `null` are ignored.
  """
  player = {
    k: v
    for k, v in player.model_dump(by_alias=True).items()
    if v is not None
  }

  if len(player) >= 1:
    update_result = await app.players.find_one_and_update(
      {'discord_id': discord_id},
      {'$set': player},
      return_document=ReturnDocument.AFTER,
    )

    if update_result is not None:
      return update_result
    else:
      raise HTTPException(
        status_code=404,
        detail=f'Player {discord_id} not found',
      )

  # Update is empty, just return matching document
  if (
    existing_player := await app.players.find_one(
      {'discord_id': discord_id}
    )
  ) is not None:
    return existing_player

  raise HTTPException(
    status_code=404, detail=f'Player {discord_id} not found'
  )
