from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

import core.titles as titles

# Default stats


class Stats(BaseModel):
  level: int
  currentxp: int
  requiredxp: int
  maxhp: int
  hp: int
  maxsan: int
  san: int
  atk: int
  dfs: int
  rst: int
  per: int
  sth: int


# Class-specific stats
# class MortAssistStats(Stats):
#   level: int
#   currentxp: int
#   requiredxp: int
#   maxhp: int
#   maxsan: int
#   hp: int
#   atk: int
#   dfs: int
#   san: int
#   rst: int
#   per: int
#   sth: int


class Cooldowns(BaseModel):
  worship: float | None


class Player(BaseModel):
  id: Optional[str] = Field(default_factory=str, alias='_id')
  discord_id: int
  title: str = Field(default=titles.PlayerTitles._1)
  stats: Stats
  tokens: int
  favor: int
  inventory: dict[str, int] | None = None
  cooldowns: Cooldowns
  registered_at: datetime
