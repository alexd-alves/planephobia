from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

import core.titles as titles


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


class Cooldowns(BaseModel):
  worship: float | None
  duel: float | None
  hunt: float | None


class Player(BaseModel):
  id: Optional[str] = Field(default_factory=str, alias='_id')
  discord_id: int
  title: str = Field(default=titles.PlayerTitles._1)
  playerClass: str
  stats: Stats
  tokens: int
  favor: int
  inventory: dict[str, int] | None = None
  cooldowns: Cooldowns
  registered_at: datetime
