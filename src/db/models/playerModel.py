import random
from datetime import datetime, timezone
from typing import Annotated, Optional

from pydantic import (
  BaseModel,
  BeforeValidator,
  ConfigDict,
  Field,
)

import core.titles as titles

PyObjectId = Annotated[str, BeforeValidator(str)]


class PlayerModel(BaseModel):
  """Container for single Player record.

  Args:
      BaseModel: Pydantic base model.

  Returns:
      _type_: _description_
  """

  # Primary key stored as str on the instance
  # Aliased to '_id' on MongoDB
  id: Optional[PyObjectId] = Field(
    alias='_id', default=None
  )
  discord_id: int = Field(...)
  title: str = Field(default=titles.PlayerTitles._1)
  playerClass: str = Field(...)
  stats: dict[str, int] = Field(
    default={
      'level': int,
      'currentxp': int,
      'requiredxp': int,
      'maxhp': int,
      'hp': int,
      'maxsan': int,
      'san': int,
      'atk': int,
      'dfs': int,
      'rst': int,
      'per': int,
      'sth': int,
    }
  )
  tokens: int = Field(...)
  favor: int = Field(...)
  inventory: dict[str, int] | None = Field(default=None)
  cooldowns: dict[str, float | None] = Field(
    default={
      'worship': None,
      'duel': None,
      'hunt': None,
    }
  )
  registered_at: datetime = Field(...)
  model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    json_schema_extra={
      'example': {
        'discord_id': 123456789987654321,
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
        'registered_at': datetime.now(),
      }
    },
  )

  def calculate_xp_gauss(
    self, m_multiplier: int, s_multiplier: int
  ) -> int:
    xp_mu = self.stats['level'] * m_multiplier
    xp_sigma = self.stats['level'] * s_multiplier
    return int(random.gauss(xp_mu, xp_sigma))

  def calculate_next_lv_xp(self) -> int:
    return (self.stats['level'] ** 2) * 50

  def cooldown_by_name(
    self,
    cooldowns: dict,
    command: str,
    target_name: Optional[str] = None,
  ) -> str | None:
    timestamp = self.cooldowns[command]
    if timestamp:
      timeSince = (
        datetime.now(timezone.utc).timestamp() - timestamp
      )
      timeRemaining = (
        cooldowns.get(command) * 60
      ) - timeSince
      if timeRemaining > 0:
        minutes, seconds = divmod(timeRemaining, 60)
        hours, minutes = divmod(minutes, 60)
        if target_name:
          return f'Try again in {
            "%d:%02d:%02d"
            % (
              hours,
              minutes,
              seconds,
            )
          }'
        elif target_name is None:
          return f'**{target_name}** has {
            "%d:%02d:%02d"
            % (
              hours,
              minutes,
              seconds,
            )
          } of cooldown remaining'
