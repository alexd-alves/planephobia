from typing import List

from pydantic import BaseModel

from db.models.playerModel import PlayerModel


class PlayerCollection(BaseModel):
  """A container holding a list of `PlayerModel` instances to avoid top-level array JSON vulnerability."""

  players: List[PlayerModel]
