from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict


class UpdatePlayerModel(BaseModel):
  """Container for updating an existing Player record.

  Args:
      BaseModel: Pydantic base model.
  """

  # Primary key stored as str on the instance
  # Aliased to '_id' on MongoDB
  title: Optional[str] = None
  playerClass: Optional[str] = None
  stats: Optional[dict[str, int]] = None
  tokens: Optional[int] = None
  favor: Optional[int] = None
  inventory: Optional[dict[str, int]] = None
  cooldowns: Optional[dict[str, float | None]] = None
  model_config = ConfigDict(
    arbitrary_types_allowed=True,
    json_encoders={ObjectId: str},
    json_schema_extra={
      'example': {
        'title': 'The Destroyer of Worlds',
        'playerClass': 'Test Class A',
        'stats': {
          'level': 1,
          'currentxp': 41,
          'requiredxp': 100,
          'maxhp': 15,
          'hp': 12,
          'maxsan': 5,
          'san': 5,
          'atk': 3,
          'dfs': 2,
          'rst': 1,
          'per': 2,
          'sth': 1,
        },
        'tokens': 15409,
        'favor': 140,
        'inventory': {
          'rumbottle': 5,
        },
        'cooldowns': {
          'worship': 15443.1,
          'duel': 1204.0,
          'hunt': 400.1,
        },
      }
    },
  )
